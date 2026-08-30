/**
 * table.js — Tabela de artigos premiados aprimorada.
 *
 * Reutiliza as linhas renderizadas pelo template (vinculadas por data-paper-id)
 * e adiciona: busca por título/autor/instituição, ordenação em todas as colunas,
 * paginação dinâmica, filtro integrado ao estado global e exportação CSV.
 */

import { filterPapers, matchesSearch, getAwardData, getAllPapers } from './data.js';
import { getState, onStateChange } from './state.js';
import { classifyAward, debounce, esc } from './utils.js';

const PAGE_SIZE = 5;

const SORT_RANK = { none: 0, honorable: 1, '3rd': 2, '2nd': 3, '1st': 4 };

let state = {
    search: '',
    sortCol: null,
    sortDir: 1, // 1 asc, -1 desc
    page: 1,
};

let awardPapers = [];
let rows = new Map(); // Paper_id -> <tr>

/** Edição exibida pela tabela (aba). Padrão: edição mais recente (2026). */
let tableYear = null;

/** Inicializa a tabela. Deve ser chamado após o DOM estar pronto. */
export function initTable() {
    awardPapers = flattenAward(getAwardData());
    collectRows();
    const editions = [...new Set(awardPapers.map((p) => p.Year))].sort((a, b) => b - a);
    tableYear = editions[0] ?? null;

    const search = document.getElementById('table-search');
    if (search) {
        search.addEventListener('input', debounce((e) => {
            state.search = e.target.value;
            state.page = 1;
            renderTable();
        }, 200));
    }

    document.querySelectorAll('.th-sort').forEach((btn) => {
        btn.addEventListener('click', () => {
            const col = btn.dataset.col;
            if (state.sortCol === col) state.sortDir *= -1;
            else { state.sortCol = col; state.sortDir = 1; }
            state.page = 1;
            renderTable();
        });
    });

    const exportBtn = document.getElementById('table-export');
    if (exportBtn) exportBtn.addEventListener('click', exportCsv);

    onStateChange(() => {
        state.page = 1;
        renderTable();
        syncYearButtons();
    });

    renderTable();
    syncYearButtons();
}

/** Sincroniza as abas de edição com a edição efetiva exibida (tableYear local). */
function syncYearButtons() {
    const activeYear = tableYear;
    document.querySelectorAll('.pag-year-button').forEach((btn) => {
        const edition = Number(btn.dataset.edition);
        const isActive = activeYear !== null && edition === activeYear;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-pressed', String(isActive));
        btn.setAttribute('aria-selected', String(isActive));
        btn.setAttribute('role', 'tab');
        btn.toggleAttribute('disabled', isActive);
    });
}

function flattenAward(awardData) {
    return awardData.flatMap((edition) => (edition.Papers || []).map((p) => {
        const award = classifyAward(p.Award);
        return { ...p, AwardCategory: award.cat, AwardLabel: award.label };
    }));
}

function collectRows() {
    rows.clear();
    document.querySelectorAll('#award-tbody tr').forEach((tr) => {
        const id = Number(tr.dataset.paperId);
        if (!Number.isNaN(id)) rows.set(id, tr);
    });
}

/** Lista resultado filtrada + ordenada (pré-paginação, usada também no CSV).
 *  A edição exibida vem das pílulas locais da tabela (tableYear); os filtros
 *  de ano globais (year/yearFrom/yearTo) não governam esta tabela. */
function visiblePapers() {
    const globalState = getState();
    const baseState = { ...globalState, year: null, yearFrom: null, yearTo: null };
    const base = filterPapers(awardPapers, baseState).filter((p) => p.Year === tableYear);
    const query = state.search.trim();
    const filtered = query ? base.filter((p) => matchesSearch(p, query)) : base;

    if (state.sortCol) {
        filtered.sort((a, b) => sortValue(a, state.sortCol) < sortValue(b, state.sortCol) ? -state.sortDir : state.sortDir);
    }
    return filtered;
}

function sortValue(paper, col) {
    switch (col) {
        case 'title': return String(paper.Title).toLowerCase();
        case 'year': return paper.Year;
        case 'award': return SORT_RANK[paper.AwardCategory];
        case 'authors': {
            const first = paper.Authors && paper.Authors[0];
            return String(first ? `${first.Name} ${first.Institution_acronym || ''}` : '').toLowerCase();
        }
        default: return 0;
    }
}

function renderTable() {
    const list = visiblePapers();
    const totalPages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
    if (state.page > totalPages) state.page = totalPages;

    const pageItems = list.slice((state.page - 1) * PAGE_SIZE, state.page * PAGE_SIZE);
    const pageIds = new Set(pageItems.map((p) => p.Paper_id));

    rows.forEach((tr) => {
        const show = pageIds.has(Number(tr.dataset.paperId));
        tr.style.display = show ? '' : 'none';
    });

    renderInfo(list.length, totalPages);
    renderPagination(list.length, totalPages);
    renderEmptyState(list.length);
    updateSortIndicators();
}

/** Paginação clássica: visível sempre que a lista couber em mais de 1 página. */
function shouldShowPagination(total, totalPages) {
    return totalPages > 1;
}

function renderInfo(total, totalPages) {
    const info = document.getElementById('table-info');
    if (!info) return;
    if (total === 0) {
        info.textContent = 'Nenhum artigo corresponde aos filtros.';
        return;
    }
    if (!shouldShowPagination(total, totalPages)) {
        info.textContent = `${total} artigo${total === 1 ? '' : 's'}`;
        return;
    }
    const range = (state.page - 1) * PAGE_SIZE + 1;
    const rangeEnd = Math.min(state.page * PAGE_SIZE, total);
    info.textContent = `${range}–${rangeEnd} de ${total} (página ${state.page}/${totalPages})`;
}

function renderPagination(total, totalPages) {
    const container = document.getElementById('table-pagination');
    if (!container) return;
    container.innerHTML = '';

    if (!shouldShowPagination(total, totalPages)) return;

    const makeBtn = (label, page, opts = {}) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'table-page-btn';
        b.textContent = label;
        if (opts.title) b.title = opts.title;
        if (opts.ariaLabel) b.setAttribute('aria-label', opts.ariaLabel);
        if (opts.current) {
            b.classList.add('active');
            b.setAttribute('aria-current', 'page');
            b.disabled = true;
        }
        if (opts.disabled) b.disabled = true;
        b.addEventListener('click', () => { state.page = page; renderTable(); });
        return b;
    };

    const prev = makeBtn('‹', Math.max(1, state.page - 1), {
        ariaLabel: 'Página anterior', title: 'Página anterior',
        disabled: state.page <= 1 || total === 0,
    });
    const next = makeBtn('›', Math.min(totalPages, state.page + 1), {
        ariaLabel: 'Próxima página', title: 'Próxima página',
        disabled: state.page >= totalPages || total === 0,
    });

    container.appendChild(prev);
    pageWindow(state.page, totalPages).forEach((p) => {
        if (p === '…') {
            const span = document.createElement('span');
            span.className = 'table-page-ellipsis';
            span.textContent = '…';
            container.appendChild(span);
        } else {
            container.appendChild(makeBtn(String(p), p, {
                current: p === state.page,
                disabled: total === 0,
                title: `Página ${p}`,
            }));
        }
    });
    container.appendChild(next);
}

/** Janela de páginas numeradas com reticências (sempre 1 e última). */
function pageWindow(current, total) {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const raw = new Set([1, total, current - 1, current, current + 1]);
    const pages = [...raw].filter((p) => p >= 1 && p <= total).sort((a, b) => a - b);
    const out = [];
    let previous = 0;
    for (const p of pages) {
        if (p - previous > 1) out.push('…');
        out.push(p);
        previous = p;
    }
    return out;
}

function renderEmptyState(total) {
    const empty = document.getElementById('table-empty');
    if (!empty) return;
    empty.hidden = total !== 0;
}

function updateSortIndicators() {
    document.querySelectorAll('.th-sort').forEach((btn) => {
        const th = btn.closest('th');
        if (state.sortCol === btn.dataset.col) {
            th.setAttribute('aria-sort', state.sortDir === 1 ? 'ascending' : 'descending');
            btn.classList.add('sort-active');
            btn.textContent = btn.dataset.label + (state.sortDir === 1 ? ' ↑' : ' ↓');
        } else {
            th.removeAttribute('aria-sort');
            btn.classList.remove('sort-active');
            btn.textContent = btn.dataset.label;
        }
    });
}

function exportCsv() {
    const list = visiblePapers();
    const header = ['Título', 'Autores', 'Ano', 'Premiação', 'Link'];
    const lines = list.map((p) => [
        p.Title,
        (p.Authors || []).map((a) => `${a.Name} (${a.Institution_acronym || ''})`).join('; '),
        p.Year,
        p.AwardLabel,
        p.Download_link || '',
    ]);
    const csv = [header, ...lines]
        .map((row) => row.map((cell) => `"${String(cell ?? '').replace(/"/g, '""')}"`).join(';'))
        .join('\r\n');
    // BOM para acentuação correta no Excel
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'datawashes-artigos-premiados.csv';
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 500);
}

/**
 * Compatibilidade: abas de edição do template (seleção rápida de ano).
 * Apenas paginam/filtram a tabela; o estado global não é tocado (desacopladas).
 */
export function paginatePapersTable(_button, edition) {
    tableYear = Number(edition);
    state.page = 1;
    renderTable();
    syncYearButtons();
}

/** Buscar um paper completo pelo id (fallback para o dump completo). */
export function getPaperById(id) {
    return awardPapers.find((p) => p.Paper_id === id)
        || getAllPapers().find((p) => p.Paper_id === id);
}

// Compatibilidade com onclick inline de templates antigos.
window.paginate_papers_table = (_button, edition) => {
    tableYear = Number(edition);
    state.page = 1;
    renderTable();
    syncYearButtons();
};