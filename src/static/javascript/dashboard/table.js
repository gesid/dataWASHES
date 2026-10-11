/**
 * table.js — Tabela de artigos premiados aprimorada.
 *
 * Reutiliza as linhas renderizadas pelo template (vinculadas por data-paper-id)
 * e adiciona: busca por título/autor/instituição, ordenação em todas as colunas,
 * filtro integrado ao estado global e exportação CSV. Todos os artigos
 * correspondentes são exibidos de uma só vez (sem paginação numérica).
 */

import { filterPapers, matchesSearch, getAwardData, getAllPapers } from './data.js';
import { getState, onStateChange } from './state.js';
import { classifyAward, debounce, esc } from './utils.js';

const SORT_RANK = { none: 0, honorable: 1, '3rd': 2, '2nd': 3, '1st': 4 };

let state = {
    search: '',
    sortCol: null,
    sortDir: 1, // 1 asc, -1 desc
};

let awardPapers = [];
let rows = new Map(); // Paper_id -> <tr>
let awardPaperById = new Map(); // "Paper_id" -> paper premiado (para busca por texto)

/** Edição exibida pela tabela (aba). 'all' = todos os anos; senão um ano (ex.: 2026). */
let tableYear = 'all';

/** Inicializa a tabela. Deve ser chamado após o DOM estar pronto. */
export function initTable() {
    awardPapers = flattenAward(getAwardData());
    awardPaperById = new Map(awardPapers.map((p) => [String(p.Paper_id), p]));
    collectRows();
    tableYear = 'all';

    const search = document.getElementById('table-search');
    if (search) {
        search.addEventListener('input', debounce((e) => {
            state.search = e.target.value;
            renderTable();
        }, 200));
    }

    document.querySelectorAll('.th-sort').forEach((btn) => {
        btn.addEventListener('click', () => {
            const col = btn.dataset.col;
            if (state.sortCol === col) state.sortDir *= -1;
            else { state.sortCol = col; state.sortDir = 1; }
            renderTable();
        });
    });

    const exportBtn = document.getElementById('table-export');
    if (exportBtn) exportBtn.addEventListener('click', exportCsv);

    onStateChange(() => {
        // Recalcula a interseção a cada mudança de filtro global: a tabela usa
        // o MESMO conjunto filtrado que alimenta os KPIs e nunca fica defasada.
        renderTable();
    });

    renderTable();
}

/** Sincroniza as abas de edição com a edição efetiva exibida (tableYear local). */
function syncYearButtons() {
    const activeYear = tableYear;
    document.querySelectorAll('.pag-year-button').forEach((btn) => {
        const edition = btn.dataset.edition;
        const isActive = activeYear === 'all'
            ? edition === 'all'
            : (edition !== 'all' && Number(edition) === activeYear);
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-pressed', String(isActive));
        btn.setAttribute('aria-selected', String(isActive));
        btn.setAttribute('role', 'tab');
        btn.toggleAttribute('disabled', isActive);
    });
}

function flattenAward(awardData) {
    // Descarta placeholders sem premiação real (Award "" ou "-"). É a mesma
    // regra usada pelo KPI "Artigos premiados" (categoria 'none'), garantindo
    // paridade de baseline entre o KPI e o total da tabela.
    return awardData.flatMap((edition) => (edition.Papers || [])
        .map((p) => {
            const award = classifyAward(p.Award);
            return { ...p, AwardCategory: award.cat, AwardLabel: award.label };
        })
        .filter((p) => p.AwardCategory !== 'none'));
}

function collectRows() {
    rows.clear();
    document.querySelectorAll('#award-tbody tr').forEach((tr) => {
        const id = Number(tr.dataset.paperId);
        if (!Number.isNaN(id)) rows.set(id, tr);
    });
}

/** IDs válidos segundo os filtros globais ativos — o MESMO conjunto que
 *  alimenta os KPIs (inclui metodologia, estado, premiação, ano global, etc.).
 *  Os objetos de `award_papers.json` não carregam campos como `Procedures`,
 *  por isso a tabela NÃO pode aplicar `filterPapers` sobre eles: precisa
 *  cruzar os IDs com o conjunto completo de `papers.json`.
 *  @returns {Set<string>} */
function globalValidPaperIds() {
    return new Set(
        filterPapers(getAllPapers(), getState()).map((p) => p.Paper_id.toString()),
    );
}

/** Lista resultado filtrada + ordenada (pré-paginação, usada também no CSV).
 *  A edição exibida vem das pílulas locais da tabela (tableYear); 'all' mostra
 *  todos os anos e um ano específico filtra.
 *
 *  Ordem estrita de interseção (para nunca divergir do KPI "Artigos premiados"):
 *   1. IDs válidos do estado global (globalValidPaperIds);
 *   2. ano da pílula local da tabela;
 *   3. busca local (#table-search). */
function visiblePapers() {
    const globalValidIds = globalValidPaperIds();
    const query = state.search.trim();

    const filtered = awardPapers.filter((paper) => {
        const isGlobalMatch = globalValidIds.has(paper.Paper_id.toString());
        const isYearMatch = (tableYear === 'all' || paper.Year === tableYear);
        const isTextMatch = !query || matchesSearch(paper, query);
        return isGlobalMatch && isYearMatch && isTextMatch;
    });

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

/** Atualiza a visibilidade das linhas da tabela e os estados de vazio/info.
 *  Exportada para o orquestrador (dashboard.js) garantir que a tabela seja
 *  revalidada a cada mudança de filtro global, junto com os KPIs. */
export function renderTable() {
    // Busca global ativa reabre a tabela em "Todos" para que qualquer resultado
    // correspondente fique visível, independentemente da pílula local.
    if ((getState().search || '').trim()) tableYear = 'all';

    const globalValidIds = globalValidPaperIds();
    const query = state.search.trim();
    let visibleCount = 0;

    rows.forEach((row) => {
        const paperId = row.dataset.paperId;
        const paper = awardPaperById.get(paperId);
        const rowYear = row.dataset.year || (paper ? String(paper.Year) : '');

        const isGlobalMatch = globalValidIds.has(paperId);
        const isYearMatch = (tableYear === 'all' || rowYear === String(tableYear));
        const isTextMatch = !query || Boolean(paper && matchesSearch(paper, query));

        const show = isGlobalMatch && isYearMatch && isTextMatch;
        row.style.display = show ? '' : 'none';
        if (show) visibleCount += 1;
    });

    hidePagination();
    renderInfo(visibleCount);
    renderEmptyState(visibleCount);
    updateSortIndicators();
    syncYearButtons();
}

/** Oculta o container de paginação numérica (a tabela exibe tudo de uma vez). */
function hidePagination() {
    const container = document.getElementById('table-pagination');
    if (container) {
        container.innerHTML = '';
        container.hidden = true;
    }
}

function renderInfo(total) {
    const info = document.getElementById('table-info');
    if (!info) return;
    if (total === 0) {
        info.textContent = 'Nenhum artigo corresponde aos filtros.';
        return;
    }
    const tableQuery = state.search.trim();
    const globalQuery = (getState().search || '').trim();
    const isSearching = Boolean(tableQuery || globalQuery);
    if (isSearching) {
        info.textContent = `${total} artigo${total === 1 ? '' : 's'} encontrado${total === 1 ? '' : 's'}`;
    } else {
        info.textContent = `${total} artigo${total === 1 ? '' : 's'} premiado${total === 1 ? '' : 's'}`;
    }
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
 * 'all' (ou null/vazio) exibe todos os anos; um valor numérico filtra por ano.
 */
export function paginatePapersTable(_button, edition) {
    if (edition === 'all' || edition === null || edition === undefined || edition === '') {
        tableYear = 'all';
    } else {
        tableYear = Number(edition);
    }
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
    if (edition === 'all' || edition === null || edition === undefined || edition === '') {
        tableYear = 'all';
    } else {
        tableYear = Number(edition);
    }
    renderTable();
    syncYearButtons();
};