/**
 * utils.js — Helpers genéricos e formatação.
 *
 * Funções puras de apoio usadas pelos demais módulos do dashboard.
 * Não dependem de estado ou de DOM.
 */

/**
 * Escapa uma string para uso seguro dentro de HTML gerado dinamicamente.
 * @param {*} value - valor a ser escapado
 * @returns {string}
 */
export function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, (ch) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    })[ch]);
}

/**
 * Formata um número no padrão pt-BR.
 * @param {number} value
 * @returns {string}
 */
export function fmt(value) {
    return Number(value ?? 0).toLocaleString('pt-BR');
}

/**
 * Calcula a porcentagem de `part` sobre `total`.
 * @param {number} part
 * @param {number} total
 * @param {number} [digits=1]
 * @returns {string} string percentual (ex.: "12.5")
 */
export function pct(part, total, digits = 1) {
    if (!total) return '0.0';
    return ((part / total) * 100).toFixed(digits);
}

/**
 * Retorna a forma singular/plural de acordo com `count`.
 * @param {number} count
 * @param {string} singular - ex.: "artigo"
 * @param {string} [plural] - ex.: "artigos"
 * @returns {string}
 */
export function pluralize(count, singular, plural) {
    const target = count === 1 ? singular : (plural || singular + 's');
    return `${count} ${target}`;
}

/**
 * Traduz o código de idioma para exibição.
 * @param {string} lang - "pt" | "en" | outro
 * @returns {string}
 */
export function languageLabel(lang) {
    if (lang === 'pt') return 'Português';
    if (lang === 'en') return 'Inglês';
    return lang || 'N/D';
}

/**
 * Classifica o texto de premiação em uma categoria normalizada.
 * @param {string} text - valor original do campo "Award"
 * @returns {{cat: string, label: string}} cat ∈ none|1st|2nd|3rd|honorable
 */
export function classifyAward(text) {
    const raw = String(text ?? '').trim();
    const label = raw.replace(/Mencao/i, 'Menção') || '—';
    if (!raw || raw === '-') return { cat: 'none', label };
    const first = raw.charAt(0);
    if (first === '1') return { cat: '1st', label };
    if (first === '2') return { cat: '2nd', label };
    if (first === '3') return { cat: '3rd', label };
    return { cat: 'honorable', label };
}

/**
 * Debounce simples.
 * @param {Function} fn
 * @param {number} [ms=150]
 * @returns {Function}
 */
export function debounce(fn, ms = 150) {
    let timer = null;
    return function debounced(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), ms);
    };
}

/**
 * Verifica se `needles` (array de strings) possui algum termo em `haystack`
 * (busca case-insensitive e tolerante a acentos simples).
 * @param {string} haystack
 * @param {string[]} needles
 * @returns {boolean}
 */
export function includesAny(haystack, needles) {
    if (!haystack) return false;
    const text = haystack.toLowerCase();
    return needles.some((needle) => needle && text.includes(needle.toLowerCase()));
}

/**
 * Remove os placeholders de carregamento de um container (ou do documento).
 * Descarrega a classe `chart-card-loading` e remove qualquer `.skeleton-overlay`
 * / `.skeleton-card` associado. Usada no bloco finally de cada componente para
 * que a falha em um render nunca trave o descarregamento dos demais.
 * @param {string|Element} [root='.dashboard'] - seletor ou elemento raiz
 */
export function hideLoading(root = '.dashboard') {
    const scope = typeof root === 'string' ? document.querySelector(root) : root;
    const targets = scope ? [scope] : document.querySelectorAll('.chart-card-loading');

    let cards = [];
    if (scope) {
        cards = scope.classList.contains('chart-card-loading')
            ? [scope, ...scope.querySelectorAll('.chart-card-loading')]
            : [...scope.querySelectorAll('.chart-card-loading')];
    }
    cards.forEach((card) => card.classList.remove('chart-card-loading'));

    const overlays = scope
        ? [...scope.querySelectorAll('.skeleton-overlay')]
        : [...document.querySelectorAll('.skeleton-overlay')];
    overlays.forEach((el) => el.remove());

    if (scope) {
        scope.querySelectorAll('.skeleton-card').forEach((el) => el.remove());
    } else {
        document.querySelectorAll('.skeleton-card').forEach((el) => el.remove());
    }
}