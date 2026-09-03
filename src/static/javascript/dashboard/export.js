/**
 * export.js — Exportação multi-formato do dashboard.
 *
 * Fornece geradores para CSV, BibTeX, RIS e JSON, além do componente
 * dropdown de UI que dispara a exportação com base nos filtros ativos.
 */

import { filterPapers, getAllPapers, getAwardText } from './data.js';
import { getState, onStateChange } from './state.js';

/* ======================================================================
   Triggers de download
   ====================================================================== */

function triggerDownload(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 500);
}

/* ======================================================================
   CSV
   ====================================================================== */

function csvCell(value) {
    return `"${String(value ?? '').replace(/"/g, '""')}"`;
}

function generateCSV(papersArray) {
    const header = [
        'ID', 'Titulo', 'Autores', 'Instituicoes', 'Ano', 'Idioma',
        'Premiacao', 'Abordagem', 'Objetivo', 'Procedimento',
        'Coleta_de_dados', 'Analise_quantitativa', 'Analise_qualitativa',
        'Citacoes', 'Link_SOL',
    ];

    const rows = papersArray.map((p) => {
        const authors = (p.Authors || []).map((a) => a.Name).join('; ');
        const institutions = (p.Authors || [])
            .map((a) => a.Institution_acronym).filter(Boolean).join('; ');
        return [
            p.Paper_id, p.Title, authors, institutions, p.Year,
            p.Language, getAwardText(p.Paper_id), p.Approach,
            p.Objective, p.Procedures, p.Data_collection,
            p.Quantitative_Data_Analysis, p.Qualitative_Data_Analysis,
            (p.Cited_by || []).length, p.Download_link || '',
        ];
    });

    return '\uFEFF' + [header, ...rows]
        .map((row) => row.map(csvCell).join(';'))
        .join('\r\n');
}

/* ======================================================================
   BibTeX
   ====================================================================== */

function bibtexEscape(text) {
    return String(text ?? '').replace(/[{}\\]/g, '\\$&');
}

function generateBibTeX(papersArray) {
    return papersArray.map((p) => {
        const key = `washes_${p.Paper_id}_${p.Year}`;
        const authors = (p.Authors || [])
            .map((a) => a.Name || '')
            .filter(Boolean)
            .join(' and ');
        const title = bibtexEscape(p.Title);
        return [
            `@inproceedings{${key},`,
            `  title = {${title}},`,
            `  author = {${authors}},`,
            `  booktitle = {Anais do Workshop sobre Aspectos Sociais, Humanos e Econômicos de Software (WASHES ${p.Year})},`,
            `  year = {${p.Year}},`,
            `  publisher = {SBC},`,
            `  url = {${p.Download_link || ''}}`,
            `}`,
        ].join('\n');
    }).join('\n\n');
}

/* ======================================================================
   RIS
   ====================================================================== */

function generateRIS(papersArray) {
    return papersArray.map((p) => {
        const lines = [
            'TY  - CONF',
            `TI  - ${p.Title || ''}`,
            `T2  - Workshop sobre Aspectos Sociais, Humanos e Econômicos de Software`,
            `PY  - ${p.Year || ''}`,
            `PB  - SBC`,
            `UR  - ${p.Download_link || ''}`,
        ];
        (p.Authors || []).forEach((a) => {
            if (a.Name) lines.push(`AU  - ${a.Name}`);
        });
        if (p.Language) lines.push(`LA  - ${p.Language === 'pt' ? 'Portuguese' : p.Language === 'en' ? 'English' : p.Language}`);
        if (p.Abstract) lines.push(`AB  - ${p.Abstract}`);
        lines.push('ER  - ');
        return lines.join('\n');
    }).join('\n\n');
}

/* ======================================================================
   JSON
   ====================================================================== */

function generateJSON(papersArray) {
    return '\uFEFF' + JSON.stringify(papersArray, null, 2);
}

/* ======================================================================
   Dispatch por formato
   ====================================================================== */

const GENERATORS = {
    csv:  { generate: generateCSV,  mime: 'text/csv;charset=utf-8;',          ext: 'csv'  },
    bib:  { generate: generateBibTeX, mime: 'application/x-bibtex;charset=utf-8;', ext: 'bib'  },
    ris:  { generate: generateRIS,  mime: 'application/x-research-info-systems;charset=utf-8;', ext: 'ris'  },
    json: { generate: generateJSON, mime: 'application/json;charset=utf-8;',  ext: 'json' },
};

function getCurrentPapers() {
    return filterPapers(getAllPapers(), getState());
}

function exportFormat(format) {
    const gen = GENERATORS[format];
    if (!gen) return;
    const papers = getCurrentPapers();
    const content = gen.generate(papers);
    triggerDownload(content, `datawashes_artigos.${gen.ext}`, gen.mime);
}

/* ======================================================================
   Dropdown UI
   ====================================================================== */

/**
 * Inicializa o dropdown de exportação na barra de filtros.
 * Deve ser chamado dentro de initFilters() após montar a row.
 * @param {HTMLElement} row - o .quick-filters-row
 */
export function initExportDropdown(row) {
    const wrap = document.createElement('div');
    wrap.className = 'export-dropdown';
    wrap.id = 'export-dropdown';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'export-dropdown-btn';
    btn.id = 'export-dropdown-btn';
    btn.setAttribute('aria-haspopup', 'true');
    btn.setAttribute('aria-expanded', 'false');
    btn.title = 'Exportar dados nos formatos CSV, BibTeX, RIS ou JSON';
    btn.innerHTML = '<span>📥 Exportar Dados</span><span class="export-dropdown-chevron" aria-hidden="true">▾</span>';

    const menu = document.createElement('div');
    menu.className = 'export-dropdown-menu';
    menu.id = 'export-dropdown-menu';
    menu.setAttribute('role', 'menu');
    menu.hidden = true;

    const formats = [
        { fmt: 'csv',  icon: '📄', label: 'Planilha CSV',         ext: '.csv'  },
        { fmt: 'bib',  icon: '📚', label: 'Citações BibTeX',      ext: '.bib'  },
        { fmt: 'ris',  icon: '🔖', label: 'Referências RIS',       ext: '.ris'  },
        { fmt: 'json', icon: '⚙️', label: 'Dados JSON',            ext: '.json' },
    ];

    formats.forEach(({ fmt, icon, label, ext }) => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'export-menu-item';
        item.setAttribute('role', 'menuitem');
        item.dataset.format = fmt;
        item.innerHTML = `<span class="export-item-icon">${icon}</span><span class="export-item-text">${label} <code>${ext}</code></span>`;
        item.addEventListener('click', () => {
            exportFormat(fmt);
            closeMenu();
        });
        menu.appendChild(item);
    });

    wrap.append(btn, menu);
    row.appendChild(wrap);

    /* ── Toggle ── */
    function toggleMenu() {
        const open = btn.getAttribute('aria-expanded') === 'true';
        if (open) closeMenu(); else openMenu();
    }

    function openMenu() {
        menu.hidden = false;
        btn.setAttribute('aria-expanded', 'true');
        btn.classList.add('open');
        positionMenu();
        const first = menu.querySelector('.export-menu-item');
        if (first) first.focus();
    }

    function closeMenu() {
        menu.hidden = true;
        btn.setAttribute('aria-expanded', 'false');
        btn.classList.remove('open');
    }

    btn.addEventListener('click', toggleMenu);

    /* ── Keyboard ── */
    btn.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            if (menu.hidden) openMenu();
            const items = [...menu.querySelectorAll('.export-menu-item')];
            if (items.length) {
                (e.key === 'ArrowDown' ? items[0] : items[items.length - 1]).focus();
            }
        }
    });

    menu.addEventListener('keydown', (e) => {
        const items = [...menu.querySelectorAll('.export-menu-item')];
        const idx = items.indexOf(document.activeElement);
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            items[(idx + 1) % items.length].focus();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            items[(idx - 1 + items.length) % items.length].focus();
        } else if (e.key === 'Home') {
            e.preventDefault();
            items[0].focus();
        } else if (e.key === 'End') {
            e.preventDefault();
            items[items.length - 1].focus();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            closeMenu();
            btn.focus();
        } else if (e.key === 'Tab') {
            closeMenu();
        }
    });

    /* ── Fechar ao clicar fora ── */
    document.addEventListener('click', (e) => {
        if (!wrap.contains(e.target)) closeMenu();
    });

    /* ── Posicionamento ──
       O menu é ancorado via CSS (.export-dropdown-menu: position absolute,
       top: calc(100% + 6px), right: 0) em relação ao container .export-dropdown.
       Não definimos top/left/right inline aqui para não desconectar o menu do
       botão nem conflitar com os estilos responsivos. */
    function positionMenu() {
        menu.style.left = '';
        menu.style.right = '';
        menu.style.top = '';
    }

    window.addEventListener('resize', () => {
        if (!menu.hidden) positionMenu();
    });

    /* ── Label dinâmico ── */
    onStateChange(() => syncLabel(btn));
    syncLabel(btn);
}

function syncLabel(btn) {
    if (!btn) return;
    const total = getAllPapers().length;
    const filtered = getCurrentPapers().length;
    const span = btn.querySelector('span:first-child');
    if (span) {
        span.textContent = filtered === total
            ? `📥 Exportar Dados (${total})`
            : `📥 Exportar Dados (${filtered})`;
    }
}
