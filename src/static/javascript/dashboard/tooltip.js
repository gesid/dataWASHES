/**
 * tooltip.js — Positioning inteligente dos tooltips de ajuda.
 *
 * Extrai e preserva a lógica original dos tooltips (.tooltip): reposiciona
 * o texto acima/abaixo e para esquerda/direita em telas pequenas.
 */
export function initTooltips() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach((tooltip) => {
        const tooltipText = tooltip.querySelector('.tooltip-text');
        if (!tooltipText) return;

        tooltip.addEventListener('mouseenter', () => {
            const rect = tooltip.getBoundingClientRect();
            const spaceAbove = rect.top;
            if (spaceAbove < 100) tooltipText.classList.add('bottom');
            else tooltipText.classList.remove('bottom');

            if (window.innerWidth <= 768) {
                const spaceRight = window.innerWidth - rect.right;
                if (spaceRight < 200) {
                    tooltipText.classList.add('mobile-left');
                    tooltipText.classList.remove('mobile-right');
                } else {
                    tooltipText.classList.add('mobile-right');
                    tooltipText.classList.remove('mobile-left');
                }
            }
        });
    });
}