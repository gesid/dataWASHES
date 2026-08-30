/**
 * modal.js — Modal de listagem de artigos (drill-down).
 *
 * Extraído do template original para manter as funcionalidades existentes
 * (abrir lista de papers a partir de qualquer gráfico) de forma modular.
 */

/** Elementos cacheados após o primeiro uso. */
let els = null;

function elements() {
    if (!els) {
        els = {
            modal: document.getElementById('papers-modal'),
            title: document.getElementById('papers-modal-title'),
            body: document.getElementById('papers-modal-body'),
        };
    }
    return els;
}

/**
 * Abre o modal listando os papers fornecidos.
 * @param {string} title
 * @param {Object[]} papers
 */
export function renderModalPapers(title, papers) {
    const { modal, title: titleEl, body } = elements();
    const count = papers.length;
    titleEl.textContent = `${title} (${count} artigo${count !== 1 ? 's' : ''})`;
    body.innerHTML = '';

    if (count === 0) {
        const empty = document.createElement('p');
        empty.style.color = 'var(--dw-text-secondary)';
        empty.style.textAlign = 'center';
        empty.style.padding = '20px 0';
        empty.textContent = 'Nenhum artigo encontrado.';
        body.appendChild(empty);
    } else {
        const ul = document.createElement('ul');
        ul.className = 'papers-modal-list';
        papers.forEach((paper) => {
            const authorsStr = (paper.Authors || [])
                .map((a) => `${a.Name} (${a.Institution_acronym || '—'})`)
                .join(', ');
            const li = document.createElement('li');
            li.className = 'papers-modal-card';
            const titleDiv = document.createElement('div');
            titleDiv.className = 'papers-modal-card-title';
            titleDiv.textContent = paper.Title;
            const metaDiv = document.createElement('div');
            metaDiv.className = 'papers-modal-card-meta';
            metaDiv.textContent = `${paper.Year} · ${authorsStr}`;
            const link = document.createElement('a');
            link.className = 'papers-modal-card-link';
            link.href = paper.Download_link || '#';
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = '🔍 Acessar na SOL SBC';
            li.append(titleDiv, metaDiv, link);
            ul.appendChild(li);
        });
        body.appendChild(ul);
    }

    modal.classList.add('visible');
    document.body.style.overflow = 'hidden';
    titleEl.focus();
}

/** Fecha o modal e restaura o scroll. */
export function closePapersModal() {
    const { modal, body } = elements();
    modal.classList.remove('visible');
    document.body.style.overflow = '';
    body.innerHTML = '';
}

/** Atalho de teclado (Escape) para fechar o modal. */
export function initModalKeyboard() {
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') closePapersModal();
    });
}

// Compatibilidade com onclick inline de templates antigos.
window.renderModalPapers = renderModalPapers;
window.closePapersModal = closePapersModal;