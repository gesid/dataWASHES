/**
 * kpis.js — Bloco de KPIs estratégicos.
 *
 * Quatro cards principais com métricas-micro integradas (subtextos):
 *  Artigos publicados · Comunidade de autores · Instituições participantes · Artigos premiados.
 * Todos os valores são derivados do conjunto filtrado (storytelling com dados reais).
 */

import { computeKpis } from './data.js';
import { fmt } from './utils.js';

/** Ícones SVG inline no mesmo traço visual dos KPIs. */
const ICONS = {
    papers: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    authors: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    institution: '<path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    award: '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
};

/**
 * Renderiza o grid de KPIs com base no conjunto filtrado.
 * @param {Object[]} filteredPapers
 * @param {Object[]} allPapers
 */
export function renderKpis(filteredPapers) {
    const kpis = computeKpis(filteredPapers || []);
    const fmtDec = (v) => {
        const n = Number(v);
        return Number.isFinite(n) ? n.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) : '0';
    };

    const cards = [
        {
            tone: 'kpi-magenta',
            icon: ICONS.papers,
            value: fmt(kpis.totalPapers),
            label: 'Artigos publicados',
            subtext: `${fmt(kpis.editions)} ediç${kpis.editions === 1 ? 'ão' : 'ões'} realizadas`,
            subAria: `${fmt(kpis.totalPapers)} artigos publicados, ${kpis.editions} edições realizadas`,
        },
        {
            tone: 'kpi-cyan',
            icon: ICONS.authors,
            value: fmt(kpis.totalAuthors),
            label: 'Comunidade de autores',
            subtext: `Média de ${fmtDec(kpis.avgAuthorsPerPaper)} autores/artigo`,
            subAria: `${fmt(kpis.totalAuthors)} autores únicos, média de ${fmtDec(kpis.avgAuthorsPerPaper)} autores por artigo`,
        },
        {
            tone: 'kpi-navy',
            icon: ICONS.institution,
            value: fmt(kpis.institutions),
            label: 'Instituições participantes',
            subtext: `Presentes em ${fmt(kpis.states)} ${kpis.states === 1 ? 'estado' : 'estados'}`,
            subAria: `${fmt(kpis.institutions)} instituições presentes em ${fmt(kpis.states)} estados`,
        },
        {
            tone: 'kpi-green',
            icon: ICONS.award,
            value: fmt(kpis.totalAwards),
            label: 'Artigos premiados',
            subtext: '1º, 2º, 3º e Menções Honrosas',
            subAria: `${fmt(kpis.totalAwards)} artigos premiados (1º, 2º, 3º e menções honrosas)`,
        },
    ];

    const grid = document.getElementById('kpi-grid');
    if (!grid) return;
    grid.innerHTML = '';

    cards.forEach((card) => {
        const div = document.createElement('div');
        div.className = `kpi-card ${card.tone}`;

        const head = document.createElement('div');
        head.className = 'kpi-card-head';
        const label = document.createElement('span');
        label.className = 'kpi-label';
        label.textContent = card.label;
        const icon = document.createElement('span');
        icon.className = 'kpi-icon';
        icon.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${card.icon}</svg>`;
        head.append(label, icon);

        const main = document.createElement('div');
        main.className = 'kpi-main';
        const value = document.createElement('span');
        value.className = 'kpi-value';
        value.textContent = card.value;
        main.appendChild(value);

        const sub = document.createElement('span');
        sub.className = 'kpi-sub';
        sub.textContent = card.subtext;
        sub.setAttribute('aria-label', card.subAria);

        div.append(head, main, sub);
        grid.appendChild(div);
    });
}