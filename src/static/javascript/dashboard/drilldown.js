/**
 * drilldown.js — Modal "Artigos correspondentes aos filtros".
 *
 * Lista todos os papers do filtro corrente (barra de filtros ou duplo-clique
 * em uma categoria/barra) com busca rápida, badge de premiação e link direto
 * para o SOL SBC. Fecha com o botão ✕, clique no fundo ou tecla Esc.
 */

import { matchesSearch, awardOf } from './data.js';
import { classifyAward } from './utils.js';

let papers = [];
let els = null;

function elements() {
    if (!els) {
        els = {
            modal: document.getElementById('drilldown-modal'),
            body: document.getElementById('drilldown-body'),
            search: document.getElementById('drilldown-search'),
            count: document.getElementById('drilldown-count'),
        };
    }
    return els;
}

/**
 * Abre o modal de drill-down com a lista de papers fornecida.
 * @param {Object[]} paperList
 */
export function openDrilldown(paperList) {
    papers = Array.isArray(paperList) ? paperList : [];
    const { modal, body, search, count } = elements();
    if (!modal) return;
    if (search) search.value = '';
    body.innerHTML = '';
    renderDrilldown();
    modal.classList.add('visible');
    document.body.style.overflow = 'hidden';
    const title = document.getElementById('drilldown-title');
    if (title) title.focus();
    if (count) count.textContent = '';
}

/** Fecha o modal e restaura o scroll da página. */
export function closeDrilldownModal() {
    const { modal, body } = elements();
    if (!modal) return;
    modal.classList.remove('visible');
    document.body.style.overflow = '';
    body.innerHTML = '';
}

/** Renderiza a lista com os papers correspondentes à busca atual. */
function renderDrilldown() {
    const { body, count } = elements();
    if (!body) return;

    const query = docsQuery();
    const filtered = query ? papers.filter((p) => matchesSearch(p, query)) : papers;
    if (count) count.textContent = `${filtered.length} de ${papers.length} artigo${papers.length === 1 ? '' : 's'}`;

    body.innerHTML = '';
    if (!filtered.length) {
        const empty = document.createElement('p');
        empty.className = 'drilldown-empty';
        empty.textContent = papers.length ? 'Nenhum artigo corresponde à busca.' : 'Nenhum artigo corresponde aos filtros.';
        body.appendChild(empty);
        return;
    }

    const ul = document.createElement('ul');
    ul.className = 'papers-modal-list';
    filtered.forEach((paper) => {
        const li = document.createElement('li');
        li.className = 'papers-modal-card';

        const head = document.createElement('div');
        head.className = 'papers-modal-card-head';
        const titleDiv = document.createElement('div');
        titleDiv.className = 'papers-modal-card-title';
        titleDiv.textContent = paper.Title;
        head.appendChild(titleDiv);

        const awardBadge = buildAwardBadge(paper);
        if (awardBadge) head.appendChild(awardBadge);

        const metaDiv = document.createElement('div');
        metaDiv.className = 'papers-modal-card-meta';
        const authorsStr = (paper.Authors || [])
            .map((a) => `${a.Name} (${a.Institution_acronym || '—'})`)
            .join(', ');
        metaDiv.textContent = `${paper.Year} · ${authorsStr}`;

        const link = document.createElement('a');
        link.className = 'papers-modal-card-link';
        link.href = paper.Download_link || '#';
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Acessar no SOL SBC ↗';

        li.append(head, metaDiv, link);
        ul.appendChild(li);
    });
    body.appendChild(ul);
}

/** Badge de premiação (evita textos vazios/maculados). */
function buildAwardBadge(paper) {
    const raw = awardOf(paper.Paper_id);
    if (!raw || !String(raw).trim() || String(raw).trim() === '-') return null;
    const { cat } = classifyAward(raw);
    const badge = document.createElement('span');
    badge.className = `award-badge award-${cat}`;
    badge.textContent = classifyAward(raw).label;
    return badge;
}

function docsQuery() {
    const { search } = elements();
    return search ? search.value.trim() : '';
}

/**
 * Inicializa o modal: busca rápida, fechar com Esc e compatibilidade com os
 * event handlers inline do template (window.closeDrilldownModal).
 */
export function initDrilldown() {
    const { search } = elements();
    if (search) {
        search.addEventListener('input', () => renderDrilldown());
    }
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') closeDrilldownModal();
    });
}

window.openDrilldown = openDrilldown;
window.closeDrilldownModal = closeDrilldownModal;