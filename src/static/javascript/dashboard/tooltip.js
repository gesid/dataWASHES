/**
 * tooltip.js — Dicas de ajuda acessíveis (.tooltip).
 *
 * Posiciona o texto acima/abaixo e à esquerda/direita em telas pequenas e
 * torna as dicas utilizáveis por mouse, teclado e toque, além de expor o
 * conteúdo via aria-describedby para leitores de tela.
 */
function positionTooltip(tooltip, tooltipText) {
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
}

export function initTooltips() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach((tooltip, index) => {
        const tooltipText = tooltip.querySelector('.tooltip-text');
        if (!tooltipText) return;

        const id = tooltipText.id || `tooltip-text-${index}`;
        tooltipText.id = id;
        tooltip.setAttribute('tabindex', '0');
        tooltip.setAttribute('aria-describedby', id);

        const open = () => {
            positionTooltip(tooltip, tooltipText);
            tooltipText.classList.add('is-open');
        };
        const close = () => {
            tooltipText.classList.remove('is-open');
        };
        const toggle = () => {
            if (tooltipText.classList.contains('is-open')) close();
            else open();
        };

        // Mouse: abre ao passar, fecha ao sair.
        tooltip.addEventListener('pointerenter', (e) => {
            if (e.pointerType === 'mouse') open();
        });
        tooltip.addEventListener('pointerleave', (e) => {
            if (e.pointerType === 'mouse') close();
        });

        // Toque/caneta: alterna ao tocar (sem roubar o foco do dedo).
        tooltip.addEventListener('pointerdown', (e) => {
            if (e.pointerType === 'mouse') return;
            e.preventDefault();
            toggle();
        });

        // Teclado: Tab foca e abre; Enter/Space alterna; Esc fecha e mantém o foco.
        tooltip.addEventListener('focusin', open);
        tooltip.addEventListener('focusout', close);
        tooltip.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggle();
            } else if (e.key === 'Escape') {
                close();
                tooltip.focus({ preventScroll: true });
            }
        });
    });

    // Tocar fora de uma dica aberta a fecha novamente.
    document.addEventListener('pointerdown', (e) => {
        if (e.pointerType === 'mouse') return;
        tooltips.forEach((tooltip) => {
            if (!tooltip.contains(e.target)) {
                const tooltipText = tooltip.querySelector('.tooltip-text');
                if (tooltipText) tooltipText.classList.remove('is-open');
            }
        });
    });
}