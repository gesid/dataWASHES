/**
 * charts.js — Renderização e interação dos gráficos.
 *
 * Encapsula a fábrica de gráficos (graphs_generator.js) com:
 *  - atalho para o estado global (cross-filtering via clique);
 *  - tooltips ricos com estatísticas adicionais;
 *  - guarda contra re-render desnecessário (mesmo estado + dados);
 *  - barras segmentadas, listas ranqueadas e abas do ranking social.
 *
 * Nunca cria um gráfico novo se o estado/dados não mudaram.
 */

import {
    insert_horizontal_bar_chart,
    insert_line_chart,
    insert_vertical_bar_chart,
    insert_brazil_map_chart,
    insert_cloud_word_chart,
    insert_compare_bar_chart,
    destroyChart,
    resizeChart,
} from '../graphs_generator.js';
import { getYears, yearStats, classificationDist, filterPapers, getAllPapers, isBrazilianState, foreignCountryName } from './data.js';
import { getState, toggleFilter } from './state.js';
import { renderModalPapers } from './modal.js';
import { openDrilldown } from './drilldown.js';
import { isCloudMode } from './wordcloud.js';
import { isPanelActive } from './tabs.js';
import { pct, hideLoading } from './utils.js';

/** Identidade declarativa e imutável dos idiomas: a cor/legenda de uma série
 *  vem SEMPRE da chave ('pt' | 'en') — nunca do índice no array de datasets.
 *  Português = Ciano (#36BCEE); Inglês = Magenta (#E72B78). */
const LANGUAGE_META = {
    pt: { label: 'Português', color: '#36BCEE' },
    en: { label: 'Inglês', color: '#E72B78' },
};

const METHODOLOGY_PALETTE = ['#E72B78', '#36BCEE', '#66C75C', '#003358', '#0D6080', '#EC4899', '#22D3EE'];

/** Cores semânticas estáveis por categoria metodológica. Mesmo com a barra
 *  segmentada filtrada a 100%, a categoria ativa preserva a cor exata. */
const CATEGORY_COLORS = {
    Qualitativa: '#E72B78',
    Mista: '#36BCEE',
    Quantitativa: '#66C75C',
    Exploratória: '#E72B78',
    Descritiva: '#36BCEE',
    Explicativa: '#66C75C',
};

function categoryColor(item, idx) {
    return CATEGORY_COLORS[item.class] || METHODOLOGY_PALETTE[idx % METHODOLOGY_PALETTE.length];
}

/** Abre o modal de drill-down com os papers do filtro corrente ampliado por `extra`. */
function openDrilldownWith(extra) {
    openDrilldown(filterPapers(getAllPapers(), { ...getState(), ...extra }));
}

/** Discrimina clique simples de duplo clique: o clique passa a ser apenas
 *  confirmado (debounce) e o dblclick cancela o clique pendente. Assim o
 *  drill-down não alterna o filtro duas vezes. */
function deferClick(onClick, onDblClick, delay = 220) {
    let timer = null;
    return {
        single: (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => onClick(...args), delay);
        },
        double: (...args) => {
            clearTimeout(timer);
            onDblClick(...args);
        },
    };
}
const METHOD_LABELS = {
    Procedures: 'Procedimentos',
    Data_collection: 'Coleta de dados',
    Quantitative_Data_Analysis: 'Análise de dados quantitativos',
    Qualitative_Data_Analysis: 'Análise de dados qualitativos',
};

/** Mapeia cada visual para o card que exibe o seu placeholder de loading. */
const CARD_FOR = {
    'artigos-por-edicao': '.dashboard .artigos_por_edicao',
    'artigos-por-idioma': '.dashboard .artigos_por_idioma',
    'ranking-institutions': '.dashboard .ranking_social',
    'ranking-authors': '.dashboard .ranking_social',
    'papers_per_state': '.dashboard .artigos_por_estado',
    'nuvem-de-palavras': '.dashboard .nuvem_palavras',
    'bar-abordagem': '.dashboard .method-card.abordagem',
    'bar-objetivo': '.dashboard .method-card.objetivo',
    'rank-procedimentos': '.dashboard .method-card.procedimentos',
    'rank-coleta-de-dados': '.dashboard .method-card.coleta-de-dados',
    'rank-quantitativos': '.dashboard .method-card.dados-quantitativos',
    'rank-qualitativos': '.dashboard .method-card.dados-qualitativos',
};

/** Abas do card de ranking social. */
const RANKING_TABS = ['institutions', 'authors'];
let rankingTab = 'institutions';
let onRankingTabChange = null;

/** Mapeia cada visual para a aba (painel) na qual ele vive. */
const PANEL_OF = {
    'artigos-por-edicao': 'visao',
    'artigos-por-idioma': 'visao',
    'ranking-institutions': 'comunidade',
    'ranking-authors': 'comunidade',
    'papers_per_state': 'comunidade',
    'nuvem-de-palavras': 'comunidade',
    'bar-abordagem': 'metodologico',
    'bar-objetivo': 'metodologico',
    'rank-procedimentos': 'metodologico',
    'rank-coleta-de-dados': 'metodologico',
    'rank-quantitativos': 'metodologico',
    'rank-qualitativos': 'metodologico',
};

/** Canvas (gráficos) de cada painel para reajuste ao ativar a aba. */
const PANEL_CHARTS = {
    visao: ['artigos-por-edicao', 'artigos-por-idioma'],
    comunidade: ['papers_per_state', 'ranking-institutions', 'ranking-authors', 'nuvem-de-palavras'],
    metodologico: [],
    premiados: [],
};

/**
 * Reajusta os gráficos de um painel (resize + update sem animação).
 * Chamado na ativação da aba, pois canvas ocultos nascem com dimensões 0.
 * @param {string} panelId - id da aba
 */
export function resizePanelCharts(panelId) {
    (PANEL_CHARTS[panelId] || []).forEach((id) => {
        const el = document.getElementById(id);
        if (el) resizeChart(el);
    });
}

/**
 * Inicializa a alternância de abas do ranking social.
 * @param {Function} [onChange] - chamado ao trocar de aba para re-renderizar
 */
export function initRankingTabs(onChange) {
    onRankingTabChange = onChange || null;
    const container = document.getElementById('ranking-tabs');
    if (!container) return;
    container.innerHTML = '';

    RANKING_TABS.forEach((tab) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tab-btn';
        btn.dataset.tab = tab;
        btn.setAttribute('role', 'tab');
        btn.setAttribute('aria-selected', String(tab === rankingTab));
        btn.textContent = tab === 'institutions' ? 'Instituições' : 'Autores';
        btn.addEventListener('click', () => {
            if (rankingTab === tab) return;
            setRankingTab(tab);
            if (onRankingTabChange) onRankingTabChange();
        });
        container.appendChild(btn);
    });
    syncRankingUI();
}

/** @returns {string} aba ativa do ranking */
export function getRankingTab() {
    return rankingTab;
}

function setRankingTab(next) {
    if (!RANKING_TABS.includes(next)) return;
    rankingTab = next;
    syncRankingUI();
}

function syncRankingUI() {
    document.querySelectorAll('#ranking-tabs .tab-btn').forEach((btn) => {
        const active = btn.dataset.tab === rankingTab;
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-selected', String(active));
    });
    const inst = document.getElementById('ranking-body-institutions');
    const authors = document.getElementById('ranking-body-authors');
    if (inst) inst.hidden = rankingTab !== 'institutions';
    if (authors) authors.hidden = rankingTab !== 'authors';

    const hiddenCanvasId = rankingTab === 'institutions' ? 'ranking-authors' : 'ranking-institutions';
    const hiddenCanvas = document.getElementById(hiddenCanvasId);
    if (hiddenCanvas) destroyChart(hiddenCanvas);
}

/** Assinatura (estado + dados) de cada visual para pular renders repetidos. */
const lastSignature = new Map();

/**
 * Renderiza um visual apenas se a assinatura da última renderização mudou.
 */
function renderOnce(id, signature, render) {
    if (lastSignature.get(id) === signature) return;
    lastSignature.set(id, signature);
    render();
}

/**
 * Envolve a renderização de um componente em try/catch/finally isolados.
 * Uma falha em um gráfico nunca impede o descarregamento dos skeletons nem
 * interrompe a renderização dos demais componentes.
 */
function renderSafe(id, signature, render, cardSelector) {
    try {
        renderOnce(id, signature, render);
    } catch (err) {
        console.error(`Falha ao renderizar o gráfico "${id}":`, err);
    } finally {
        hideLoading(cardSelector || '.dashboard');
    }
}

function clear(id) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '';
}

/**
 * Renderiza um componente apenas se o painel da aba correspondente estiver
 * visível. Em painéis ocultos o render é pulado (a assinatura permanece),
 * então o gráfico é construído sob demanda na primeira ativação da aba.
 */
function renderActive(id, signature, render, cardSelector) {
    if (!isPanelActive(PANEL_OF[id])) return;
    renderSafe(id, signature, render, cardSelector);
}

/** @returns {string[]} rótulos de ano no padrão atual: "YYYY (N°)" */
function yearLabels() {
    return getYears().map((year, index) => `${year} (${index + 1}°)`);
}

/* ===== BUILDERS DE CONFIG + CLICK ===== */

/** Estado da comparação entre dois anos (independente dos filtros globais). */
const compare = { enabled: false, yearA: null, yearB: null };
let onCompareChange = null;

/**
 * Constroi os controles de comparação no container #compare-controls.
 * @param {Function} [onChange] - chamado ao alterar a comparação para re-renderizar
 */
export function initCompareControls(onChange) {
    onCompareChange = onChange || null;
    const container = document.getElementById('compare-controls');
    if (!container) return;
    const years = getYears();
    if (years.length < 2) return;

    const last = years[years.length - 1];
    const prev = years[years.length - 2];
    compare.yearA = compare.yearA || last;
    compare.yearB = compare.yearB || prev;

    container.innerHTML = '';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'compare-toggle';
    btn.textContent = 'Comparar anos';
    btn.setAttribute('aria-pressed', 'false');
    btn.addEventListener('click', () => {
        compare.enabled = !compare.enabled;
        syncCompareUI();
        if (onCompareChange) onCompareChange();
    });
    container.appendChild(btn);

    const selectsWrap = document.createElement('div');
    selectsWrap.className = 'compare-year-controls';
    selectsWrap.hidden = true;

    const mk = (key, label, toneClass) => {
        const wrap = document.createElement('div');
        wrap.className = `filter-field ${toneClass}`;
        const lbl = document.createElement('label');
        lbl.textContent = label;
        const sel = document.createElement('select');
        sel.className = 'filter-select';
        sel.setAttribute('aria-label', label);
        years.forEach((y) => {
            const o = document.createElement('option');
            o.value = y;
            o.textContent = y;
            sel.appendChild(o);
        });
        sel.value = compare[key];
        sel.addEventListener('change', () => {
            compare[key] = Number(sel.value);
            if (compare.yearA === compare.yearB) {
                const alt = key === 'yearA' ? 'yearB' : 'yearA';
                compare[alt] = years.find((y) => y !== compare[key]) ?? compare[alt];
            }
            syncCompareUI();
            if (onCompareChange) onCompareChange();
        });
        wrap.append(lbl, sel);
        return wrap;
    };

    selectsWrap.append(mk('yearA', 'Ano A', 'compare-year-a'), mk('yearB', 'Ano B', 'compare-year-b'));
    container.appendChild(selectsWrap);

    function syncCompareUI() {
        btn.classList.toggle('active', compare.enabled);
        btn.setAttribute('aria-pressed', String(compare.enabled));
        selectsWrap.hidden = !compare.enabled;
        const sels = selectsWrap.querySelectorAll('select');
        if (sels[0]) sels[0].value = compare.yearA;
        if (sels[1]) sels[1].value = compare.yearB;
    }
}

function compareEnabled() {
    return compare.enabled && compare.yearA !== null && compare.yearB !== null;
}

function buildYearArea(papers, stats) {
    if (compareEnabled()) {
        buildCompareChart(papers);
        return;
    }
    const data = {};
    (papers || []).forEach((p) => { data[p.Year] = (data[p.Year] || 0) + 1; });
    const years = getYears();
    const labels = yearLabels();
    const newest = years[years.length - 1];
    const values = years.map((y) => data[y] || 0);
    const tooltipRows = (year) => {
        const s = stats[year];
        if (!s) return [];
        return [
            `${pct(s.papers, papers.length, 1)}% do total filtrado`,
            `${s.authors} autores distintos`,
            `${s.qualitative} qualitativos · ${s.mixed} mistos · ${s.quantitative} quantitativos`,
            `${s.institutions} instituições`,
        ];
    };
    const activeYear = getState().year;
    const activeLabel = activeYear !== null ? yearLabels()[years.indexOf(activeYear)] : null;
    const yearClick = deferClick(
        (label) => toggleFilter('year', parseInt(String(label).split(' ')[0], 10)),
        (label) => openDrilldownWith({ year: parseInt(String(label).split(' ')[0], 10) })
    );
    insert_vertical_bar_chart(document.getElementById('artigos-por-edicao'), {
        labels,
        data: values,
        selected: activeLabel,
        highlight: (label) => parseInt(String(label).split(' ')[0], 10) === newest,
        onClick: yearClick.single,
        onDblClick: yearClick.double,
        tooltip: tooltipRows,
    });
}

/** Comparação anual por abordagem (dois anos lado a lado). */
function buildCompareChart(papers) {
    const { yearA, yearB } = compare;
    const dist = (year) => classificationDist((papers || []).filter((p) => p.Year === year), 'Approach')
        .reduce((map, item) => { map[item.class] = item.count; return map; }, {});
    const distA = dist(yearA);
    const distB = dist(yearB);
    const labels = [...new Set([...Object.keys(distA), ...Object.keys(distB)])]
        .sort((a, b) => a.localeCompare(b, 'pt-BR'));

    const canvas = document.getElementById('artigos-por-edicao');
    if (!canvas) return;
    if (!labels.length) {
        destroyChart(canvas);
        return;
    }
    insert_compare_bar_chart(canvas, {
        labels,
        series: [
            { label: `Ano ${yearA}`, data: labels.map((v) => distA[v] || 0) },
            { label: `Ano ${yearB}`, data: labels.map((v) => distB[v] || 0) },
        ],
        onClick: (label) => toggleFilter('approach', label),
    });
}

function buildLanguageLine(papers) {
    // Contagem por ano e idioma, sempre indexada pela chave explícita.
    const data = {};
    (papers || []).forEach((p) => {
        if (!(p.Language in LANGUAGE_META)) return;
        if (!data[p.Year]) data[p.Year] = {};
        data[p.Year][p.Language] = (data[p.Year][p.Language] || 0) + 1;
    });
    // Com filtro de idioma ativo, apenas a linha daquele idioma é exibida,
    // mantendo cor e legenda corretas; sem filtro, ambas as linhas.
    const active = getState().language || null;
    const keys = active && active in LANGUAGE_META ? [active] : Object.keys(LANGUAGE_META);
    const series = keys.map((key) => ({
        key,
        label: LANGUAGE_META[key].label,
        color: LANGUAGE_META[key].color,
        data: getYears().map((year) => (data[year] && data[year][key]) || 0),
    }));
    const langClick = deferClick(
        (yearLabel, key) => toggleFilter('language', key),
        (yearLabel, key) => openDrilldownWith({ language: key })
    );
    insert_line_chart(document.getElementById('artigos-por-idioma'), {
        labels: yearLabels(),
        series,
        onClick: langClick.single,
        onDblClick: langClick.double,
    });
}

function buildInstitutionBar(papers) {
    const counts = {};
    const countryByInst = {};
    (papers || []).forEach((p) => {
        const first = p.Authors && p.Authors[0];
        if (first && first.Institution_acronym) {
            counts[first.Institution_acronym] = (counts[first.Institution_acronym] || 0) + 1;
            if (!isBrazilianState(first.State) && foreignCountryName(first.State)) {
                countryByInst[first.Institution_acronym] = foreignCountryName(first.State);
            }
        }
    });
    const entries = Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    const instClick = deferClick(
        (name) => toggleFilter('institution', name),
        (name) => openDrilldownWith({ institution: name })
    );
    insert_horizontal_bar_chart(document.getElementById('ranking-institutions'), {
        labels: entries.map(([name]) => (countryByInst[name] ? `${name} (${countryByInst[name]})` : name)),
        data: entries.map(([, count]) => count),
        rank: true,
        selected: getState().institution,
        labelsMap: new Map(entries.map(([name]) => [countryByInst[name] ? `${name} (${countryByInst[name]})` : name, name])),
        onClick: instClick.single,
        onDblClick: instClick.double,
    });
}

function buildAuthorBar(papers) {
    const counts = new Map();
    (papers || []).forEach((p) => {
        (p.Authors || []).forEach((a) => {
            const key = `${a.Name}|${a.Author_id}`;
            counts.set(key, (counts.get(key) || 0) + 1);
        });
    });
    const entries = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10);
    insert_horizontal_bar_chart(document.getElementById('ranking-authors'), {
        labels: entries.map(([key]) => key.split('|')[0]),
        data: entries.map(([, count]) => count),
        rank: true,
        onClick: (name) => {
            const matched = (papers || []).filter((p) => (p.Authors || []).some((a) => `${a.Name}` === name));
            renderModalPapers(`Artigos de ${name}`, matched);
        },
    });
}

function buildStateMap(papers) {
    const counts = {};
    (papers || []).forEach((p) => {
        const first = p.Authors && p.Authors[0];
        if (first && first.State) counts[first.State] = (counts[first.State] || 0) + 1;
    });
    const mapClick = deferClick(
        (stateName) => toggleFilter('state', stateName),
        (stateName) => openDrilldownWith({ state: stateName })
    );
    insert_brazil_map_chart(document.getElementById('papers_per_state'), {
        ...counts,
        onClick: mapClick.single,
        onDblClick: mapClick.double,
    });
}

/** Barras segmentadas (Abordagem / Objetivo) com clique para filtrar. */
function buildSegmented(containerId, field, items) {
    clear(containerId);
    const total = (items || []).reduce((s, i) => s + i.count, 0);
    if (!total) return;
    const container = document.getElementById(containerId);
    if (!container) return;

    const bar = document.createElement('div');
    bar.className = 'segmented-bar';
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', field);
    const segSelected = getState()[fieldKey(field)];
    (items || []).forEach((item, idx) => {
        const seg = document.createElement('div');
        seg.className = 'segment';
        const isSelected = segSelected !== null && item.class === segSelected;
        seg.style.width = `${(item.count / total) * 100}%`;
        seg.style.backgroundColor = categoryColor(item, idx);
        seg.style.cursor = 'pointer';
        seg.title = `${item.class}: ${item.count} artigos`;
        seg.setAttribute('role', 'button');
        seg.setAttribute('tabindex', '0');
        seg.classList.toggle('selected', isSelected);
        seg.classList.toggle('dimmed', segSelected !== null && !isSelected);
        const segClick = deferClick(
            () => toggleFilter(fieldKey(field), item.class),
            () => openDrilldownWith({ [fieldKey(field)]: item.class })
        );
        seg.addEventListener('click', segClick.single);
        seg.addEventListener('dblclick', segClick.double);
        seg.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleFilter(fieldKey(field), item.class);
            }
        });
        bar.appendChild(seg);
    });
    container.appendChild(bar);

    const badges = document.createElement('div');
    badges.className = 'badge-grid';
    (items || []).forEach((item, idx) => {
        const badge = document.createElement('button');
        badge.type = 'button';
        badge.className = 'method-badge';
        badge.style.cursor = 'pointer';
        const isSelected = segSelected !== null && item.class === segSelected;
        badge.classList.toggle('selected', isSelected);
        badge.classList.toggle('dimmed', segSelected !== null && !isSelected);
        const badgeClick = deferClick(
            () => toggleFilter(fieldKey(field), item.class),
            () => openDrilldownWith({ [fieldKey(field)]: item.class })
        );
        badge.addEventListener('click', badgeClick.single);
        badge.addEventListener('dblclick', badgeClick.double);
        const pctValue = pct(item.count, total);
        badge.innerHTML =
            `<span class="badge-dot" style="background-color:${categoryColor(item, idx)}"></span>` +
            `<span class="badge-label">${item.class}</span> ` +
            `<span class="badge-count">${item.count}</span> ` +
            `<span class="badge-pct">(${pctValue}%)</span>`;
        badges.appendChild(badge);
    });
    container.appendChild(badges);
}

/**
 * Listas ranqueadas (Procedimentos/Coleta/Análises).
 * Procedimentos filtra por cross-filter; as demais abrem o modal de artigos.
 * A cor das barras de progresso vem do tom (data-tone) do card no CSS.
 */
function buildRankedList(containerId, field, items, papers) {
    clear(containerId);
    const total = (items || []).reduce((s, i) => s + i.count, 0);
    if (!total) return;
    const container = document.getElementById(containerId);
    if (!container) return;
    const list = document.createElement('div');
    list.className = 'rank-list';

    [...items].sort((a, b) => b.count - a.count).forEach((item) => {
        const pctValue = pct(item.count, total);
        const row = document.createElement('button');
        row.type = 'button';
        row.className = 'rank-item';
        row.style.cursor = 'pointer';
        row.setAttribute('title', METHOD_LABELS[field] ? `Ver ${METHOD_LABELS[field]}: ${item.class}` : `Filtrar por ${field}: ${item.class}`);
        const fieldKeyFor = fieldKey(field);
        if (fieldKeyFor) {
            const active = getState()[fieldKeyFor];
            row.classList.toggle('selected', active !== null && active === item.class);
        }
        const rowClick = deferClick(
            () => {
                if (fieldKeyFor) {
                    toggleFilter(fieldKeyFor, item.class);
                    return;
                }
                const matched = (papers || []).filter((p) => (String(p[field] || '').split(',').map((v) => v.trim())).includes(item.class));
                renderModalPapers(`${METHOD_LABELS[field] || field}: ${item.class}`, matched);
            },
            () => {
                if (fieldKeyFor) {
                    openDrilldownWith({ [fieldKeyFor]: item.class });
                    return;
                }
                const matched = (papers || []).filter((p) => (String(p[field] || '').split(',').map((v) => v.trim())).includes(item.class));
                openDrilldown(matched);
            }
        );
        row.addEventListener('click', rowClick.single);
        row.addEventListener('dblclick', rowClick.double);
        row.innerHTML =
            `<span class="rank-name">${item.class}</span>` +
            `<span class="rank-stats">${item.count} (${pctValue}%)</span>` +
            `<span class="rank-bar-track"><span class="rank-bar-fill" style="width:${pctValue}%"></span></span>`;
        list.appendChild(row);
    });
    container.appendChild(list);
}

/** Mapeia o rótulo de dimensão para a chave de filtro do estado
 *  (undefined quer dizer "abrir modal", não filtrar). */
function fieldKey(field) {
    const map = {
        Approach: 'approach',
        Objective: 'objective',
        Procedures: 'procedure',
    };
    return map[field] || undefined;
}

/** Nuvem de palavras (modo nuvem), mantendo o drill-down por palavra-chave. */
function buildWordCloud(papers) {
    const canvas = document.getElementById('nuvem-de-palavras');
    if (!canvas) {
        console.warn('Canvas da nuvem de palavras não encontrado no DOM.');
        return;
    }
    const words = [];
    const map = new Map();
    (papers || []).forEach((p) => {
        if (!p.Keywords || p.Keywords === '#') return;
        String(p.Keywords).split(',').forEach((kw) => {
            String(kw).split(/\s+/).forEach((word) => {
                const clean = word.trim();
                if (!clean || clean === '#' || ['de', 'e', 'do'].includes(clean.toLowerCase())) return;
                const key = clean.toLowerCase();
                if (!map.has(key)) map.set(key, { keyword: key, count: 0, paper_ids: [] });
                const entry = map.get(key);
                entry.count += 1;
                entry.paper_ids.push(p.Paper_id);
            });
        });
    });
    map.forEach((entry) => words.push({ keyword: entry.keyword, count: entry.count, paper_ids: entry.paper_ids }));
    const cloudClick = deferClick(
        (wordItem) => {
            const matched = (papers || []).filter((p) => wordItem.paper_ids && wordItem.paper_ids.includes(p.Paper_id));
            renderModalPapers(`Artigos com a palavra-chave: ${wordItem.text || wordItem.keyword}`, matched);
        },
        (wordItem) => {
            const matched = (papers || []).filter((p) => wordItem.paper_ids && wordItem.paper_ids.includes(p.Paper_id));
            openDrilldown(matched);
        }
    );
    // Legibilidade global: limita aos 50 tópicos mais frequentes e usa escala
    // Raiz Quadrada para o tamanho da fonte (o plugin chartjs-chart-wordcloud
    // lê o fonte diretamente do valor do dataset, em px): a palavra mais
    // frequente fica em 36px e as demais decaem suavemente até o mínimo de
    // 13px, sem "gigante cercado de invisíveis".
    words.sort((a, b) => b.count - a.count);
    const topWords = words.slice(0, 50);
    const counts = topWords.map((w) => w.count);
    const maxCount = Math.max(1, ...counts);
    const MIN_FONT = 13;
    const MAX_FONT = 36;
    const fontOf = (c) => Math.max(MIN_FONT, Math.min(MAX_FONT, Math.round(MIN_FONT + (MAX_FONT - MIN_FONT) * Math.sqrt(c / maxCount))));
    insert_cloud_word_chart(canvas, {
        labels: topWords.map((w) => w.keyword),
        data: counts.map(fontOf),
        counts,
        wordItems: topWords,
        onClick: cloudClick.single,
        onDblClick: cloudClick.double,
    });
}

/**
 * Renderiza todos os gráficos para um conjunto filtrado.
 * Cada componente é isolado em try/catch/finally: a falha de um nunca
 * bloqueia o descarregamento dos skeletons nem a renderização dos demais.
 * @param {Object} ctx - {papers, state}
 */
export function renderAll(ctx) {
    const papers = (ctx && ctx.papers) || [];
    const state = (ctx && ctx.state) || {};
    const stats = yearStats(papers);
    const gas = JSON.stringify(state || {});

    renderActive('artigos-por-edicao', gas + compareSignature(), () => buildYearArea(papers, stats), CARD_FOR['artigos-por-edicao']);
    renderActive('artigos-por-idioma', gas, () => buildLanguageLine(papers), CARD_FOR['artigos-por-idioma']);

    const rankSig = gas + `:${rankingTab}`;
    renderActive('ranking-institutions', rankSig, () => {
        if (rankingTab === 'institutions') buildInstitutionBar(papers);
    }, CARD_FOR['ranking-institutions']);
    renderActive('ranking-authors', rankSig, () => {
        if (rankingTab === 'authors') buildAuthorBar(papers);
    }, CARD_FOR['ranking-authors']);

    renderActive('papers_per_state', gas, () => buildStateMap(papers), CARD_FOR['papers_per_state']);

    const approachDist = classificationDist(papers, 'Approach');
    const objectiveDist = classificationDist(papers, 'Objective');
    renderActive('bar-abordagem', gas + JSON.stringify(approachDist), () => buildSegmented('bar-abordagem', 'Approach', approachDist), CARD_FOR['bar-abordagem']);
    renderActive('bar-objetivo', gas + JSON.stringify(objectiveDist), () => buildSegmented('bar-objetivo', 'Objective', objectiveDist), CARD_FOR['bar-objetivo']);
    const pSig = proceduresSig(papers);
    renderActive('rank-procedimentos', gas + pSig, () => buildRankedList('rank-procedimentos', 'Procedures', classificationDist(papers, 'Procedures'), papers), CARD_FOR['rank-procedimentos']);
    renderActive('rank-coleta-de-dados', gas + pSig, () => buildRankedList('rank-coleta-de-dados', 'Data_collection', classificationDist(papers, 'Data_collection'), papers), CARD_FOR['rank-coleta-de-dados']);
    renderActive('rank-quantitativos', gas + pSig, () => buildRankedList('rank-quantitativos', 'Quantitative_Data_Analysis', classificationDist(papers, 'Quantitative_Data_Analysis'), papers), CARD_FOR['rank-quantitativos']);
    renderActive('rank-qualitativos', gas + pSig, () => buildRankedList('rank-qualitativos', 'Qualitative_Data_Analysis', classificationDist(papers, 'Qualitative_Data_Analysis'), papers), CARD_FOR['rank-qualitativos']);

    renderActive('nuvem-de-palavras', gas + `:${isCloudMode()}`, () => {
        if (isCloudMode()) buildWordCloud(papers);
    }, CARD_FOR['nuvem-de-palavras']);
}

function compareSignature() {
    return compareEnabled() ? `cmp:${compare.yearA}:${compare.yearB}` : 'cmp:off';
}

function proceduresSig(papers) {
    return (papers || [])
        .map((p) => [p.Procedures, p.Data_collection, p.Quantitative_Data_Analysis, p.Qualitative_Data_Analysis])
        .join('|');
}

/** Limpa os gráficos (ex.: estado vazio). */
export function clearAllCharts() {
    lastSignature.clear();
    const canvasIds = [
        'artigos-por-edicao',
        'artigos-por-idioma',
        'ranking-institutions',
        'ranking-authors',
        'papers_per_state',
        'nuvem-de-palavras',
    ];
    canvasIds.forEach((id) => {
        const el = document.getElementById(id);
        if (el) destroyChart(el);
    });
    ['bar-abordagem', 'bar-objetivo', 'rank-procedimentos', 'rank-coleta-de-dados',
        'rank-quantitativos', 'rank-qualitativos', 'ranking-mode']
        .forEach((id) => clear(id));
}