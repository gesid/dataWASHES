/**
 * tabs.js — Navegação por seções (abas) do dashboard.
 *
 * Organiza o conteúdo em quatro painéis exibidos um por vez, eliminando a
 * rolagem infinita: ao clicar na aba, o painel correspondente é exibido
 * instantaneamente com transição suave. Integra-se ao estado global:
 * qualquer mudança de filtro dispara uma re-renderização do painel ativo.
 */

/** Definição das abas (ordem de exibição). */
const TABS = [
    { id: 'visao', icon: '📊', label: 'Visão Geral & Evolução' },
    { id: 'comunidade', icon: '🗺️', label: 'Comunidade & Geografia' },
    { id: 'metodologico', icon: '🧬', label: 'Perfil Metodológico' },
    { id: 'premiados', icon: '🏅', label: 'Artigos Premiados' },
];

let activeTabId = TABS[0].id;
let onChange = null;

/**
 * Inicializa a barra de abas no container #section-tabs.
 * @param {Function} [onTabChangeCb] - chamado ao trocar de aba (id da aba)
 *   para que o orquestrador re-renderize o painel ativo.
 */
export function initTabs(onTabChangeCb) {
    onChange = onTabChangeCb || null;
    const bar = document.getElementById('section-tabs');
    if (!bar) return;

    bar.innerHTML = '';

    TABS.forEach((tab) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tab-btn';
        btn.dataset.tab = tab.id;
        btn.id = `tab-${tab.id}`;
        btn.setAttribute('role', 'tab');
        btn.setAttribute('aria-controls', `panel-${tab.id}`);
        btn.setAttribute('aria-selected', 'false');
        btn.tabIndex = -1;
        btn.innerHTML = `<span class="tab-icon" aria-hidden="true">${tab.icon}</span> ${tab.label}`;
        btn.addEventListener('click', () => switchTab(tab.id));
        bar.appendChild(btn);
    });

    bar.addEventListener('keydown', (event) => {
        const tabs = [...bar.querySelectorAll('[role="tab"]')];
        const index = tabs.findIndex((b) => b.dataset.tab === activeTabId);
        let next = -1;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = tabs.length - 1;
        if (next < 0) return;
        event.preventDefault();
        switchTab(tabs[next].dataset.tab);
        tabs[next].focus();
    });

    switchTab(activeTabId, false, true);
}

/**
 * Ativa uma aba: atualiza aria/hidden nos painéis e notifica o orquestrador.
 * @param {string} tabId - id da aba
 * @param {boolean} [notify=true] - dispara o callback de troca
 * @param {boolean} [force=false] - sincroniza a UI mesmo se já for a aba ativa
 */
export function switchTab(tabId, notify = true, force = false) {
    if (!TABS.some((t) => t.id === tabId)) return;
    if (!force && tabId === activeTabId) return;
    activeTabId = tabId;

    document.querySelectorAll('#section-tabs .tab-btn').forEach((btn) => {
        const active = btn.dataset.tab === activeTabId;
        btn.classList.toggle('active', active);
        btn.setAttribute('aria-selected', String(active));
        btn.tabIndex = active ? 0 : -1;
    });

    document.querySelectorAll('.tab-panel').forEach((panel) => {
        const show = panel.dataset.panel === activeTabId;
        if (show) {
            panel.hidden = false;
        } else {
            panel.hidden = true;
        }
    });

    if (onChange && notify) onChange(activeTabId);
}

/** @returns {string} id da aba atualmente visível */
export function getActiveTab() {
    return activeTabId;
}

/**
 * Verifica se uma aba/componente está visível no momento.
 * Usada pelos gráficos para renderizar apenas o painel ativo.
 * @param {string} tabId
 * @returns {boolean}
 */
export function isPanelActive(tabId) {
    return tabId === activeTabId;
}