/**
 * wordcloud.js — Alternância Nuvem / Ranking de palavras-chave.
 *
 * Modo Nuvem: mantém o gráfico de palavras-chave (charts.js).
 * Modo Ranking: lista ordenada decrescente com palavra, quantidade e
 * porcentagem. Ambos abrem o modal de artigos ao clicar.
 */

import { renderModalPapers } from './modal.js';
import { pct } from './utils.js';
import { keywordsCloud } from './data.js';

const MODES = ['cloud', 'ranking'];

let mode = 'cloud';
let latestPapers = [];
let latestWords = [];
let onModeChange = null;

/**
 * Inicializa os botões de alternância Nuvem/Ranking.
 * @param {Function} [onModeChangeCb] - chamado quando a nuvem precisa ser
 *   reconstruída (ex.: ao voltar do modo Ranking), permitindo ao orquestrador
 *   disparar uma nova renderização.
 */
export function initWordCloudToggle(onModeChangeCb) {
    onModeChange = onModeChangeCb || null;
    const container = document.getElementById('wordcloud-toggle');
    if (!container) return;
    container.innerHTML = '';

    MODES.forEach((m) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'mode-btn';
        btn.dataset.mode = m;
        btn.textContent = m === 'cloud' ? 'Nuvem' : 'Ranking';
        btn.setAttribute('aria-pressed', String(mode === m));
        btn.addEventListener('click', () => setMode(m));
        container.appendChild(btn);
    });
}

/**
 * Recebe os papers filtrados atualizados a cada mudança de estado.
 * @param {Object[]} papers
 */
export function update(papers) {
    latestPapers = papers;
    latestWords = keywordsCloud(papers);
    if (mode === 'ranking') renderRanking();
}

/** @returns {boolean} true quando o modo atual é Nuvem */
export function isCloudMode() {
    return mode === 'cloud';
}

function setMode(next) {
    if (!MODES.includes(next) || next === mode) return;
    mode = next;
    document.querySelectorAll('.mode-btn').forEach((btn) => {
        btn.setAttribute('aria-pressed', String(btn.dataset.mode === mode));
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    const cloudEl = document.getElementById('cloud-mode');
    const rankingEl = document.getElementById('ranking-mode');
    if (cloudEl) cloudEl.hidden = mode !== 'cloud';
    if (rankingEl) rankingEl.hidden = mode !== 'ranking';

    if (mode === 'ranking') renderRanking();
    else if (onModeChange) onModeChange();
}

function renderRanking() {
    const container = document.getElementById('ranking-mode');
    if (!container) return;
    container.innerHTML = '';

    if (!latestWords.length) {
        const empty = document.createElement('p');
        empty.className = 'empty-hint';
        empty.textContent = 'Nenhuma palavra-chave para os filtros ativos.';
        container.appendChild(empty);
        return;
    }

    const list = document.createElement('div');
    list.className = 'rank-list';
    const total = latestWords.reduce((s, w) => s + w.count, 0);

    latestWords.forEach((word) => {
        const row = document.createElement('button');
        row.type = 'button';
        row.className = 'rank-item';
        row.style.cursor = 'pointer';
        row.addEventListener('click', () => {
            const matched = latestPapers.filter((p) => word.paper_ids.includes(p.Paper_id));
            renderModalPapers(`Artigos com a palavra-chave: ${word.keyword}`, matched);
        });
        row.innerHTML =
            `<span class="rank-name">${word.keyword}</span>` +
            `<span class="rank-stats">${word.count} · ${pct(word.count, total)}%</span>` +
            `<span class="rank-bar-track"><span class="rank-bar-fill" style="width:${pct(word.count, total)}%"></span></span>`;
        list.appendChild(row);
    });

    container.appendChild(list);
}