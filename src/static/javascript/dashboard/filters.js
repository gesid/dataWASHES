/**
 * filters.js — Controle rápido do dashboard.
 *
 * Layout em duas camadas:
 *  1. Linha discreta: busca por texto livre + idioma + botão "Filtros avançados".
 *  2. Sanfona expandível com os filtros restantes (faixa de anos, instituição,
 *     estado, premiação e metodologia).
 * Todos os controles alimentam o estado global e disparam re-renderização.
 */

import { buildOptionLists, getYears, filterPapers, getAllPapers } from './data.js';
import { getState, setFilter, resetFilters, onStateChange } from './state.js';
import { openDrilldown } from './drilldown.js';
import { languageLabel, debounce } from './utils.js';

const AWARD_OPTIONS = [
    { value: 'awarded', label: 'premiados' },
    { value: '1st', label: '1º Lugar' },
    { value: '2nd', label: '2º Lugar' },
    { value: '3rd', label: '3º Lugar' },
    { value: 'honorable', label: 'Menção Honrosa' },
];

const FIELD_LABELS = {
    search: 'Busca',
    year: 'Ano',
    yearFrom: 'Ano (de)',
    yearTo: 'Ano (até)',
    language: 'Idioma',
    institution: 'Instituição',
    state: 'Estado',
    award: 'Premiação',
    approach: 'Abordagem',
    objective: 'Objetivo',
    procedure: 'Procedimento',
};

/** Seletores agrupados na sanfona "Filtros Avançados". */
const ADVANCED_FIELDS = ['year', 'yearFrom', 'yearTo', 'institution', 'state', 'award', 'approach', 'objective', 'procedure'];

/**
 * Constrói o controle rápido no container #filters-bar.
 */
export function initFilters() {
    const container = document.getElementById('filters-bar');
    if (!container) return;

    const options = buildOptionLists();
    const years = getYears();

    container.innerHTML = '';

    const fieldOpts = {
        year: years.map((y) => ({ value: y, label: String(y) })),
        yearFrom: years.map((y) => ({ value: y, label: `≥ ${y}` })),
        yearTo: years.map((y) => ({ value: y, label: `≤ ${y}` })),
        language: options.languages.map((l) => ({ value: l, label: languageLabel(l) })),
        institution: options.institutions.map((i) => ({ value: i, label: i })),
        state: options.states.map((s) => ({ value: s, label: s })),
        award: AWARD_OPTIONS,
        approach: options.approaches.map((a) => ({ value: a, label: a })),
        objective: options.objectives.map((o) => ({ value: o, label: o })),
        procedure: options.procedures.map((p) => ({ value: p, label: p })),
    };

    const makeSelect = (field) => {
        const label = FIELD_LABELS[field];
        const opts = fieldOpts[field] || [];
        const wrap = document.createElement('div');
        wrap.className = 'filter-field';
        wrap.dataset.label = label;

        const select = document.createElement('select');
        select.id = `filter-${field}`;
        select.className = 'filter-select';
        select.name = field;
        select.setAttribute('aria-label', label);

        const none = document.createElement('option');
        none.value = '';
        none.textContent = `${label} · Todos`;
        select.appendChild(none);

        opts.forEach((opt) => {
            const el = document.createElement('option');
            el.value = opt.value;
            el.textContent = opt.label;
            select.appendChild(el);
        });

        select.value = getState()[field] ?? '';
        select.addEventListener('change', () => setFilter(field, select.value));
        wrap.append(select);
        return wrap;
    };

    // ── Linha principal ──
    const row = document.createElement('div');
    row.className = 'quick-filters-row';
    row.setAttribute('role', 'search');
    row.setAttribute('aria-label', 'Busca e filtros rápidos do dashboard');

    const searchWrap = document.createElement('div');
    searchWrap.className = 'quick-search-wrap';
    const searchInput = document.createElement('input');
    searchInput.type = 'search';
    searchInput.id = 'global-search';
    searchInput.className = 'quick-search';
    searchInput.placeholder = 'Buscar por título, autor ou instituição…';
    searchInput.autocomplete = 'off';
    searchInput.setAttribute('aria-label', 'Buscar por título, autor ou instituição');
    searchInput.value = getState().search || '';
    searchInput.addEventListener('input', debounce((e) => {
        setFilter('search', e.target.value);
    }, 220));
    searchWrap.append(searchInput);

    const quickSelects = document.createElement('div');
    quickSelects.className = 'quick-selects';
    quickSelects.append(makeSelect('language'));

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'filters-advanced-toggle';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-controls', 'filters-advanced');
    toggle.innerHTML = '<span>Filtros avançados</span><span class="filters-chevron" aria-hidden="true">▾</span>';
    toggle.addEventListener('click', () => {
        const open = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!open));
        advanced.hidden = open;
        toggle.classList.toggle('open', !open);
    });

    const reset = document.createElement('button');
    reset.type = 'button';
    reset.className = 'filter-reset-btn';
    reset.innerHTML = '<span aria-hidden="true">✕</span> Limpar filtros';
    reset.addEventListener('click', resetFilters);

    const actions = document.createElement('div');
    actions.className = 'quick-actions';
    actions.append(toggle, reset);
    row.append(searchWrap, quickSelects, actions);

    // ── Filtros avançados (sanfona) ──
    const advanced = document.createElement('div');
    advanced.className = 'filters-advanced';
    advanced.id = 'filters-advanced';
    advanced.hidden = true;
    const advancedGrid = document.createElement('div');
    advancedGrid.className = 'filters-advanced-grid';
    ADVANCED_FIELDS.forEach((key) => advancedGrid.append(makeSelect(key)));
    advanced.append(advancedGrid);

    container.append(row, advanced);
    renderActiveChips(container);

    onStateChange(() => {
        syncControls(container);
        renderActiveChips(container);
    });

    return { reset, searchInput };
}

/** Sincroniza os controles com o estado (sem disparar eventos). */
function syncControls(container) {
    const state = getState();
    container.querySelectorAll('.filter-select').forEach((select) => {
        select.value = state[select.name] ?? '';
    });
    const search = container.querySelector('#global-search');
    if (search && search.value !== (state.search || '')) {
        search.value = state.search || '';
    }
}

/** Renderiza chips dos filtros ativos + contador. */
function renderActiveChips(container) {
    const existing = container.querySelector('.active-chips');
    if (existing) existing.remove();
    const existingDd = container.querySelector('.drilldown-btn');
    if (existingDd) existingDd.remove();

    const state = getState();
    const valueLabel = { language: languageLabel };

    const active = Object.entries(state)
        .filter(([key]) => key !== 'search')
        .filter(([, v]) => v !== null && v !== '');
    const chips = document.createElement('div');
    chips.className = 'active-chips';
    chips.setAttribute('aria-live', 'polite');

    if (!active.length) return;

    active.forEach(([key, value]) => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'chip';
        chip.title = 'Remover filtro';
        const display = (valueLabel[key] ? valueLabel[key](value) : value);
        chip.textContent = `${FIELD_LABELS[key] || key}: ${display} ✕`;
        chip.addEventListener('click', () => setFilter(key, null));
        chips.appendChild(chip);
    });

    container.appendChild(chips);

    // Ação rápida: ver os artigos correspondentes ao filtro corrente.
    const filteredCount = filterPapers(getAllPapers(), getState()).length;
    const dd = document.createElement('button');
    dd.type = 'button';
    dd.className = 'drilldown-btn';
    dd.setAttribute('aria-haspopup', 'dialog');
    dd.title = 'Listar os artigos correspondentes aos filtros ativos';
    dd.textContent = `📄 Ver ${filteredCount} artigo${filteredCount === 1 ? '' : 's'} correspondentes ↗`;
    dd.addEventListener('click', () => openDrilldown(filterPapers(getAllPapers(), getState())));
    container.appendChild(dd);
}