/**
 * timeline.js — Pílulas de anos (Linha do tempo).
 *
 * Renderiza os controles [Todos] [2016] … [2026] como pílulas horizontais.
 * Clicar em um ano alterna o filtro global `year`; "Todos" limpa o filtro.
 * A pílula ativa recebe fundo magenta com texto branco.
 */

import { getYears } from './data.js';
import { toggleFilter, getState } from './state.js';
import { fmt } from './utils.js';

/**
 * Renderiza as pílulas de anos a partir do conjunto filtrado.
 * @param {Object[]} filteredPapers - papers considerados (contagem por ano)
 */
export function renderTimeline(filteredPapers) {
    const container = document.getElementById('year-pills');
    if (!container) return;

    const counts = {};
    (filteredPapers || []).forEach((p) => { counts[p.Year] = (counts[p.Year] || 0) + 1; });
    const years = getYears();
    const activeYear = getState().year;

    container.innerHTML = '';

    const group = document.createElement('div');
    group.className = 'year-pills-group';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', 'Filtrar por edição (ano)');

    const mkPill = (label, title, active, tag) => {
        const pill = document.createElement('button');
        pill.type = 'button';
        pill.className = `year-pill${active ? ' active' : ''}${tag ? ` ${tag}` : ''}`;
        pill.textContent = label;
        pill.title = title || label;
        pill.setAttribute('aria-pressed', String(active));
        return pill;
    };

    const all = mkPill('Todos', 'Todas as edições', activeYear === null, 'pill-all');
    all.addEventListener('click', () => {
        if (activeYear !== null) toggleFilter('year', activeYear);
    });
    group.appendChild(all);

    years.forEach((year) => {
        const count = counts[year] || 0;
        const active = activeYear === year;
        const pill = mkPill(String(year), `${year} · ${fmt(count)} artigo${count === 1 ? '' : 's'}`, active);
        pill.setAttribute('aria-label', `${year}: ${fmt(count)} artigo${count === 1 ? '' : 's'}; clique para filtrar`);
        pill.addEventListener('click', () => toggleFilter('year', year));
        group.appendChild(pill);
    });

    container.appendChild(group);
}