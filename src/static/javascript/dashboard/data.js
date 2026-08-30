/**
 * data.js — Camada de dados do dashboard.
 *
 * Separa dados, transformações e renderização:
 *  - Recebe o dump completo de papers (e dos premiados) uma única vez;
 *  - Expõe funções puras de filtragem e agregação consumidas pelas views;
 *  - Centraliza todo cálculo para evitar consultas repetidas.
 *
 * Convenções de negócio preservadas do backend:
 *  - Instituição e estado consideram o PRIMEIRO autor do artigo;
 *  - Campos de metodologia podem conter múltiplos valores separados por ", ".
 */

import { includesAny } from './utils.js';

/** UFs brasileiras oficiais — distinguem estados (BR) de instituições internacionais. */
const BRAZIL_UFS = new Set([
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
    'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
    'SP', 'SE', 'TO',
]);

/** @returns {boolean} true se o valor corresponde a uma UF brasileira oficial. */
export function isBrazilianState(state) {
    return typeof state === 'string' && BRAZIL_UFS.has(state.trim().toUpperCase());
}

/** Códigos de State usados para identificar países estrangeiros (fora do BR). */
const FOREIGN_COUNTRIES = {
    'EUA': 'EUA',
    'CA': 'Canadá',
    'GER': 'Alemanha',
    'FR': 'França',
};

/** @returns {string|undefined} nome do país para um State estrangeiro conhecido
 *  (undefined para UFs BR, '#' ou códigos desconhecidos). */
export function foreignCountryName(state) {
    if (typeof state !== 'string') return undefined;
    const key = state.trim().toUpperCase();
    return FOREIGN_COUNTRIES[key];
}

/** @type {Object[]} papers completos (PaperDB) */
let papers = [];
/** @type {Object[]} agrupamento por ano dos premiados (AwardPapersDB) */
let awardData = [];
/** @type {Map<number,string>} Paper_id -> texto de premiação */
const awardMap = new Map();
/** @type {number[]} anos ordenados das edições */
let years = [];

/**
 * Inicializa a camada de dados com os dumps serializados no template.
 * @param {Object[]} paperList
 * @param {Object[]} awardList
 */
export function initData(paperList, awardList) {
    papers = Array.isArray(paperList) ? paperList : [];
    awardData = Array.isArray(awardList) ? awardList : [];
    awardMap.clear();
    awardData.forEach((edition) => {
        (edition.Papers || []).forEach((paper) => {
            if (paper && paper.Paper_id !== undefined) awardMap.set(paper.Paper_id, paper.Award);
        });
    });
    years = [...new Set(papers.map((p) => p.Year))].sort((a, b) => a - b);
}

/** @returns {Object[]} todos os papers */
export function getAllPapers() {
    return papers;
}

/** @returns {number[]} anos ordenados */
export function getYears() {
    return years;
}

/**
 * Texto de premiação de um artigo (undefined se não premiado/ausente).
 * @param {number} paperId
 * @returns {string|undefined}
 */
export function awardOf(paperId) {
    return awardMap.get(paperId);
}

/** @returns {Object[]} registros de premiados (ano -> Papers) */
export function getAwardData() {
    return awardData;
}

/**
 * Lista de opções para cada dimensão de filtro, derivada do conjunto completo.
 * @returns {Object} {languages, institutions, states, approaches, objectives, procedures}
 */
export function buildOptionLists() {
    const languages = new Set();
    const institutions = new Set();
    const states = new Set();
    const approaches = new Set();
    const objectives = new Set();
    const procedures = new Set();

    papers.forEach((paper) => {
        if (paper.Language) languages.add(paper.Language);
        if (paper.Approach && paper.Approach !== '#') approaches.add(paper.Approach);
        if (paper.Objective && paper.Objective !== '#') objectives.add(paper.Objective);
        addMulti(procedures, paper.Procedures);
        const first = paper.Authors && paper.Authors[0];
        if (first) {
            if (first.Institution_acronym) institutions.add(first.Institution_acronym);
            if (first.State) states.add(first.State);
        }
    });

    return {
        languages: sortLocale([...languages]),
        institutions: sortLocale([...institutions]),
        states: sortLocale([...states]),
        approaches: [...approaches],
        objectives: [...objectives],
        procedures: sortLocale([...procedures]),
    };
}

function addMulti(set, raw) {
    if (!raw || raw === '#') return;
    String(raw).split(',').map((v) => v.trim()).filter(Boolean).forEach((v) => set.add(v));
}

function sortLocale(list) {
    return list.sort((a, b) => a.localeCompare(b, 'pt-BR'));
}

/**
 * Aplica todos os filtros ativos do estado sobre um conjunto de papers.
 * Todos os filtros combinam em AND.
 * @param {Object[]} source
 * @param {Object} state - snapshot de getState()
 * @returns {Object[]}
 */
export function filterPapers(source, state) {
    return source.filter((paper) => {
        const first = paper.Authors && paper.Authors[0];

        if (state.search && state.search.trim() && !matchesSearch(paper, state.search)) return false;

        if (state.year !== null && paper.Year !== state.year) return false;

        if (state.yearFrom !== null && paper.Year < state.yearFrom) return false;

        if (state.yearTo !== null && paper.Year > state.yearTo) return false;

        if (state.language !== null && paper.Language !== state.language) return false;

        if (state.institution !== null) {
            if (!first || first.Institution_acronym !== state.institution) return false;
        }

        if (state.state !== null) {
            if (!first || first.State !== state.state) return false;
        }

        if (state.approach !== null && paper.Approach !== state.approach) return false;

        if (state.objective !== null && paper.Objective !== state.objective) return false;

        if (state.procedure !== null && !fieldContains(paper.Procedures, state.procedure)) return false;

        if (state.award !== null) {
            const award = classifyAwardState(awardMap.get(paper.Paper_id));
            if (state.award === 'awarded' && award === 'none') return false;
            if (state.award !== 'awarded' && award !== state.award) return false;
        }

        return true;
    });
}

function fieldContains(raw, value) {
    if (!raw || raw === '#') return false;
    return String(raw).split(',').map((v) => v.trim()).includes(value);
}

function classifyAwardState(text) {
    const raw = String(text ?? '').trim();
    if (!raw || raw === '-') return 'none';
    const first = raw.charAt(0);
    return first === '1' ? '1st' : first === '2' ? '2nd' : first === '3' ? '3rd' : 'honorable';
}

/**
 * Estatísticas por ano (tooltips ricos).
 * @param {Object[]} source
 * @returns {Object} {year: {papers, authors, qualitative, quantitative, mixed, institutions}}
 */
export function yearStats(source) {
    const byYear = {};
    source.forEach((paper) => {
        const bucket = (byYear[paper.Year] ||= {
            papers: 0,
            authors: new Set(),
            qualitative: 0,
            quantitative: 0,
            mixed: 0,
            institutions: new Set(),
        });
        bucket.papers += 1;
        (paper.Authors || []).forEach((a) => {
            if (a.Author_id !== undefined) bucket.authors.add(a.Author_id);
        });
        if (paper.Approach === 'Qualitativa') bucket.qualitative += 1;
        else if (paper.Approach === 'Quantitativa') bucket.quantitative += 1;
        else if (paper.Approach === 'Mista') bucket.mixed += 1;
        const inst = paper.Authors && paper.Authors[0] && paper.Authors[0].Institution_acronym;
        if (inst) bucket.institutions.add(inst);
    });
    const result = {};
    for (const [year, bucket] of Object.entries(byYear)) {
        result[year] = {
            papers: bucket.papers,
            authors: bucket.authors.size,
            qualitative: bucket.qualitative,
            quantitative: bucket.quantitative,
            mixed: bucket.mixed,
            institutions: bucket.institutions.size,
        };
    }
    return result;
}

/* ===== Agregações básicas (todas recebem o conjunto filtrado) ===== */

/** Contagem de publicações por ano (ordenada). @returns {[{year, publications}]} */
export function countByYear(source) {
    const counts = {};
    source.forEach((p) => { counts[p.Year] = (counts[p.Year] || 0) + 1; });
    return years
        .filter((y) => counts[y] !== undefined)
        .map((year) => ({ year, publications: counts[year] }));
}

/** Contagem por idioma com histórico por ano (para o line chart). */
export function countByLanguageSeries(source) {
    const langs = new Set();
    const perYear = {};
    source.forEach((p) => {
        if (p.Language) langs.add(p.Language);
        (perYear[p.Year] ||= {})[p.Language] = (perYear[p.Year][p.Language] || 0) + 1;
    });
    const data = years
        .filter((y) => perYear[y] !== undefined)
        .map((year) => ({ year, ...perYear[year] }));
    return { data, langs: [...langs] };
}

/** Ranking de instituições pela quantidade de artigos do primeiro autor. */
export function institutionRank(source) {
    const counts = {};
    source.forEach((p) => {
        const first = p.Authors && p.Authors[0];
        if (first && first.Institution_acronym) {
            counts[first.Institution_acronym] = (counts[first.Institution_acronym] || 0) + 1;
        }
    });
    return Object.entries(counts)
        .map(([institution, publications]) => ({ institution, publications }))
        .sort((a, b) => b.publications - a.publications);
}

/** Ranking de autores pela quantidade de artigos. */
export function authorRank(source) {
    const counts = new Map();
    source.forEach((p) => {
        (p.Authors || []).forEach((a) => {
            const key = a.Author_id !== undefined ? a.Author_id : a.Name;
            if (!counts.has(key)) counts.set(key, { id: key, name: a.Name, count: 0 });
            counts.get(key).count += 1;
        });
    });
    return [...counts.values()].sort((a, b) => b.count - a.count);
}

/** Ranking de estados pela quantidade de artigos do primeiro autor. */
export function stateRank(source) {
    const counts = {};
    source.forEach((p) => {
        const first = p.Authors && p.Authors[0];
        if (first && first.State) counts[first.State] = (counts[first.State] || 0) + 1;
    });
    return Object.entries(counts)
        .map(([state, publications]) => ({ state, publications }))
        .sort((a, b) => b.publications - a.publications);
}

/**
 * Distribuição de uma dimensão de classificação ({class, count}).
 * @param {Object[]} source
 * @param {string} field - Approach | Objective | Procedures | Data_collection | ...
 * @returns {[{class, count}]}
 */
export function classificationDist(source, field) {
    const counts = {};
    source.forEach((p) => {
        const raw = p[field];
        if (!raw || raw === '#') return;
        String(raw).split(',').map((v) => v.trim()).filter(Boolean).forEach((v) => {
            counts[v] = (counts[v] || 0) + 1;
        });
    });
    return Object.entries(counts)
        .map(([cls, count]) => ({ class: cls, count }))
        .sort((a, b) => b.count - a.count);
}

/** Nuvem de palavras-chave. @returns {[{keyword, count, paper_ids}]} */
export function keywordsCloud(source) {
    const map = new Map();
    source.forEach((p) => {
        if (!p.Keywords || p.Keywords === '#' || p.Keywords === '') return;
        String(p.Keywords).split(',').forEach((kw) => {
            String(kw).split(/\s+/).forEach((word) => {
                const clean = word.trim();
                if (!clean || clean === '#' || ['de', 'e', 'do'].includes(clean.toLowerCase())) return;
                const key = clean.toLowerCase();
                if (!map.has(key)) map.set(key, { keyword: key, count: 0, paper_ids: new Set() });
                const entry = map.get(key);
                entry.count += 1;
                entry.paper_ids.add(p.Paper_id);
            });
        });
    });
    return [...map.values()]
        .map((entry) => ({ keyword: entry.keyword, count: entry.count, paper_ids: [...entry.paper_ids] }))
        .sort((a, b) => b.count - a.count);
}

/** Palavras-chave como lista de palavras-chave completas (sem texto em p.Keywords) — não usado por ora. */

/* ===== KPIs ===== */

/**
 * Calcula todos os KPIs para o conjunto filtrado + variação vs. ano anterior.
 * @param {Object[]} source
 * @returns {Object} kpis
 */
export function computeKpis(source) {
    const authors = new Set();
    const institutions = new Set();
    const states = new Set();
    const brazilStates = new Set();
    const foreignCountries = new Set();
    let english = 0;
    let qualitative = 0;
    let authorCount = 0;

    source.forEach((p) => {
        (p.Authors || []).forEach((a) => {
            authorCount += 1;
            if (a.Author_id !== undefined) authors.add(a.Author_id);
            if (a.State && foreignCountryName(a.State)) foreignCountries.add(a.State.trim().toUpperCase());
        });
        const first = p.Authors && p.Authors[0];
        if (first) {
            if (first.Institution_acronym) institutions.add(first.Institution_acronym);
            if (first.State) {
                states.add(first.State);
                if (isBrazilianState(first.State)) brazilStates.add(first.State);
            }
        }
        if (p.Language === 'en') english += 1;
        if (p.Approach === 'Qualitativa') qualitative += 1;
    });

    const byYear = countByYear(source);
    const editions = byYear.length;
    const awardCount = source.filter((p) => {
        const a = classifyAwardState(awardMap.get(p.Paper_id));
        return a !== 'none';
    }).length;

    return {
        totalPapers: source.length,
        editions,
        totalAuthors: authors.size,
        totalAwards: awardCount,
        institutions: institutions.size,
        states: brazilStates.size,
        brazilStatesCount: brazilStates.size,
        foreignCountriesCount: foreignCountries.size,
        hasInternational: states.size > brazilStates.size,
        avgAuthorsPerPaper: source.length ? +(authorCount / source.length).toFixed(1) : 0,
        englishPct: Boolean(source.length) ? +((english / source.length) * 100).toFixed(1) : 0,
        qualitativePct: Boolean(source.length) ? +((qualitative / source.length) * 100).toFixed(1) : 0,
        byYear,
    };
}

/**
 * Variação percentual e delta entre o valor filtrado atual e o ano anterior
 * (usada nos KPIs de "crescimento em relação ao ano anterior").
 * @param {Object} kpis - resultado de computeKpis()
 * @param {Object} allKpis - KPIs do conjunto completo
 * @returns {Object} {papersDelta, papersPct, authorsDelta, authorsPct}
 */
export function computeGrowth(kpis, allKpis) {
    const { activeYear, prevYear, prevPapers, prevAuthors } = inferAnchors(kpis.byYear);
    const currentPapers = kpis.totalPapers;
    const currentAuthors = kpis.totalAuthors;
    return {
        activeYear,
        prevYear,
        papersDelta: prevPapers !== null ? currentPapers - prevPapers : null,
        papersPct: prevPapers ? +(((currentPapers - prevPapers) / prevPapers) * 100).toFixed(1) : null,
        authorsDelta: prevAuthors !== null ? currentAuthors - prevAuthors : null,
        authorsPct: prevAuthors ? +(((currentAuthors - prevAuthors) / prevAuthors) * 100).toFixed(1) : null,
        allPapers: allKpis.totalPapers,
    };
}

/** Detecta o ano de referência e o ano anterior a partir da série por ano. */
function inferAnchors(byYear) {
    if (!byYear.length) return { activeYear: null, prevYear: null, prevPapers: null, prevAuthors: null };
    const last = byYear[byYear.length - 1];
    const previous = byYear.length >= 2 ? byYear[byYear.length - 2] : null;
    return {
        activeYear: last.year,
        prevYear: previous ? previous.year : null,
        prevPapers: previous ? previous.publications : null,
        prevAuthors: null,
    };
}

/** Filtros de busca livre (título/autor/instituição) usados pela tabela e pela busca global de textos. */
export function matchesSearch(paper, needle) {
    const terms = needle.toLowerCase().trim().split(/\s+/).filter(Boolean);
    if (!terms.length) return true;
    const haystack = [
        paper.Title,
        ...(paper.Authors || []).map((a) => `${a.Name} ${a.Institution_acronym || ''}`),
    ].join(' | ');
    return terms.every((term) => includesAny(haystack, [term]));
}