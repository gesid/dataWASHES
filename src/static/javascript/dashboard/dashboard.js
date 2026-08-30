/**
 * dashboard.js — Orquestrador do dashboard.
 *
 * Ponto de entrada chamado pelo template. Monta os módulos, registra o
 * observador do estado global e coordena a renderização completa a cada
 * mudança de filtro (gráficos, KPIs, timeline, nuvem e tabela).
 */

import { initData, filterPapers, getAllPapers } from './data.js';
import { getState, onStateChange, resetFilters } from './state.js';
import { renderKpis } from './kpis.js';
import { renderAll, clearAllCharts, initCompareControls, initRankingTabs, resizePanelCharts } from './charts.js';
import { renderTimeline } from './timeline.js';
import { initFilters } from './filters.js';
import { initTable } from './table.js';
import { initWordCloudToggle, update as updateWordCloud } from './wordcloud.js';
import { initModalKeyboard, closePapersModal } from './modal.js';
import { initDrilldown } from './drilldown.js';
import { initTooltips } from './tooltip.js';
import { initTabs, getActiveTab } from './tabs.js';
import { hideLoading } from './utils.js';

let emptyToggle = null; // listener "limpar filtros" do estado vazio
let booted = false;
const SKELETON_CHART_CLASSES = [
    'artigos_premiados',
    'artigos_por_edicao',
    'artigos_por_idioma',
    'ranking_social',
    'nuvem_palavras',
    'artigos_por_estado',
];

/**
 * Bootstrap do dashboard (chamado após o parser do HTML).
 * @param {Object[]} allPapers - dump completo de papers
 * @param {Object[]} awardData - dump de artigos premiados por edição
 */
export function initDashboard(allPapers, awardData) {
    try {
        initData(allPapers, awardData);
        initModalKeyboard();
        initDrilldown();
        initTooltips();
        initSkeletons();
        initFilters();
        initTable();
        initWordCloudToggle(fullRender);
        initCompareControls(fullRender);
        initRankingTabs(fullRender);
        initTabs((tabId) => {
            fullRender();
            resizePanelCharts(tabId);
        });
        wireEmptyStateReset();
    } catch (err) {
        console.error('Erro na montagem inicial do dashboard:', err);
    }

    onStateChange(fullRender);
    // Primeira render apó o skeleton ser visível (transição de carregamento).
    setTimeout(() => {
        try {
            fullRender();
            resizePanelCharts(getActiveTab());
        } catch (err) {
            console.error('Erro crítico na renderização inicial do dashboard:', err);
        } finally {
            // Garante que os skeletons sejam descarregados mesmo com falha parcial.
            clearSkeletons();
            const db = document.querySelector('.dashboard');
            if (db) db.classList.add('ready');
        }
    }, 120);

    let renderInFlight = false;
    function fullRender() {
        // Bloqueia re-render recursivo: se um render já estiver em execução
        // (ex.: evento em cascata de resize/abc), a chamada é descartada. A
        // ativação de uma aba dispara apenas UM render por clique.
        if (renderInFlight) return;
        renderInFlight = true;
        try {
        const state = getState();
        const filtered = filterPapers(getAllPapers(), state);

        if (filtered.length === 0) {
            showEmptyState();
            clearAllCharts();
        } else {
            hideEmptyState();
        }

        // Cada componente é isolado: uma falha nunca bloqueia os demais.
        try {
            renderKpis(filtered, getAllPapers());
        } catch (err) {
            console.error('Falha ao renderizar os KPIs:', err);
        }
        try {
            renderTimeline(filtered);
        } catch (err) {
            console.error('Falha ao renderizar a timeline:', err);
        }
        try {
            updateWordCloud(filtered);
        } catch (err) {
            console.error('Falha ao atualizar a nuvem de palavras:', err);
        }
        try {
            renderAll({ papers: filtered, state });
        } catch (err) {
            console.error('Falha ao renderizar os gráficos:', err);
        }

        if (!booted) {
            booted = true;
            clearSkeletons();
        }
        } finally {
            renderInFlight = false;
        }
    }
}

/** Exibe placeholders de carregamento enquanto o módulo inicializa. */
function initSkeletons() {
    const grid = document.getElementById('kpi-grid');
    if (grid) {
        grid.innerHTML = Array.from({ length: 8 },
            () => '<div class="kpi-card skeleton-card" aria-hidden="true"></div>').join('');
    }
    SKELETON_CHART_CLASSES.forEach((cls) => {
        const card = document.querySelector(`.dashboard .${cls}`);
        if (!card) return;
        card.classList.add('chart-card-loading');
        const overlay = document.createElement('div');
        overlay.className = 'skeleton-overlay';
        overlay.setAttribute('aria-hidden', 'true');
        card.appendChild(overlay);
    });
}

/** Remove os placeholders no fim da primeira renderização (idempotente). */
function clearSkeletons() {
    hideLoading();
    const db = document.querySelector('.dashboard');
    if (db) db.classList.add('ready');
}

function wireEmptyStateReset() {
    if (emptyToggle) return;
    const btn = document.querySelector('#empty-state .empty-reset');
    if (btn) btn.addEventListener('click', () => resetFilters());
    emptyToggle = true;
}

function showEmptyState() {
    const el = document.getElementById('empty-state');
    if (el) el.hidden = false;
}

function hideEmptyState() {
    const el = document.getElementById('empty-state');
    if (el) el.hidden = true;
}

// Mantém exposto para event handlers inline do template.
window.closePapersModal = closePapersModal;