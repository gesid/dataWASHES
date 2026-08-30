/**
 * state.js — Estado global do dashboard.
 *
 * Fonte única de verdade dos filtros ativos. Todos os gráficos, KPIs,
 * tabela, nuvem e timeline consomem este estado e se re-renderizam
 * quando ele muda (padrão observer).
 */

export const FILTER_KEYS = [
    'search',
    'year',
    'yearFrom',
    'yearTo',
    'language',
    'institution',
    'state',
    'award',
    'approach',
    'objective',
    'procedure',
];

export const DEFAULTS = Object.freeze({
    search: '',
    year: null,
    yearFrom: null,
    yearTo: null,
    language: null,
    institution: null,
    state: null,
    award: null,
    approach: null,
    objective: null,
    procedure: null,
});

/** @type {typeof DEFAULTS} */
let state = { ...DEFAULTS };

/** @type {Set<Function>} */
const listeners = new Set();

/** @returns {typeof DEFAULTS} cópia do estado atual */
export function getState() {
    return { ...state };
}

/** @returns {boolean} true caso exista ao menos um filtro ativo */
export function hasActiveFilters() {
    return Object.values(state).some((value) => value !== null && value !== '');
}

/**
 * Define um filtro e notifica os observadores caso o valor tenha mudado.
 * @param {string} key - uma das FILTER_KEYS
 * @param {*} value - novo valor (null limpa o filtro)
 */
export function setFilter(key, value) {
    if (!FILTER_KEYS.includes(key)) return;
    let next = value === '' ? null : value;
    if (next !== null && key.startsWith('year')) next = Number(next);
    if (state[key] === next) return;
    state = { ...state, [key]: next };
    notify();
}

/**
 * Alterna um filtro: se `value` já está ativo, remove; caso contrário ativa.
 * @param {string} key
 * @param {*} value
 */
export function toggleFilter(key, value) {
    setFilter(key, state[key] === value ? null : value);
}

/** Limpa todos os filtros. */
export function resetFilters() {
    state = { ...DEFAULTS };
    notify();
}

/**
 * Define o filtro de ano inicial (antes da primeira renderização).
 * Usado para deixar o ano mais recente ativo por padrão no carregamento.
 * @param {number|null} year
 */
export function primeInitialYear(year) {
    if (year != null && state.year === null) {
        state = { ...state, year: Number(year) };
    }
}

/**
 * Registra um observador invocado a cada mudança de estado.
 * @param {(state: typeof DEFAULTS) => void} fn
 * @returns {() => void} função para remover o observador
 */
export function onStateChange(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
}

function notify() {
    const snapshot = state;
    listeners.forEach((fn) => fn(snapshot));
}