import {Chart, registerables} from 'https://esm.sh/chart.js';
import {WordCloudController, WordElement} from 'https://esm.sh/chartjs-chart-wordcloud';
import {
    topojson,
    ChoroplethController,
    ChoroplethChart,
    GeoFeature,
    ProjectionScale,
    ColorScale,
} from 'https://esm.sh/chartjs-chart-geo';
import ChartDataLabels from 'https://esm.sh/chartjs-plugin-datalabels';

Chart.register(ChartDataLabels, WordCloudController, WordElement, ChoroplethController, GeoFeature, ProjectionScale, ColorScale, ...registerables);

Chart.defaults.font.family = "'Sofia Sans', sans-serif";

const PRIMARY_PALETTE = ['#E72B78', '#36BCEE', '#66C75C', '#003358', '#0D6080', '#EC4899', '#22D3EE'];

const _chartRegistry = new WeakMap();

/**
 * Mounts (or re-mounts) a Chart.js instance on a canvas element.
 * Destroys any previously mounted instance so the same canvas can be
 * safely reused on every dashboard re-render.
 * @param {HTMLCanvasElement} canvas - target canvas
 * @param {object} config - Chart.js (or Choropleth) configuration
 * @param {Function} [ChartCtor=Chart] - chart constructor to use
 * @returns {object} the created chart instance
 */
function mountChart(canvas, config, ChartCtor = Chart) {
    // Verifica se o canvas existe e possui contexto 2D válido antes de instanciar.
    if (!canvas || typeof canvas.getContext !== 'function') {
        console.warn('mountChart ignorado: canvas inexistente no DOM.', canvas);
        return null;
    }
    let ctx;
    try {
        ctx = canvas.getContext('2d');
    } catch (e) {
        ctx = null;
    }
    if (!ctx) {
        console.warn('mountChart ignorado: contexto 2D inválido.', canvas);
        return null;
    }

    const previous = _chartRegistry.get(canvas);
    if (previous) {
        previous.destroy();
        _chartRegistry.delete(canvas);
    }
    const chart = new ChartCtor(canvas, config);
    _chartRegistry.set(canvas, chart);
    return chart;
}

/**
 * Destroys the chart instance attached to a canvas, if any.
 * @param {HTMLCanvasElement} canvas
 */
export function destroyChart(canvas) {
    if (!canvas) return;
    const previous = _chartRegistry.get(canvas);
    if (previous) {
        previous.destroy();
        _chartRegistry.delete(canvas);
    }
}

/**
 * Reajusta um gráfico montado ao tamanho do container (Chart.resize) e
 * atualiza o desenho sem animação. Usado ao exibir painéis que estavam
 * ocultos, pois canvas em display:none nascem com dimensões 0.
 * @param {HTMLCanvasElement} canvas
 */
export function resizeChart(canvas) {
    if (!canvas) return;
    const chart = _chartRegistry.get(canvas);
    if (!chart) return;
    try {
        chart.resize();
        chart.update('none');
    } catch (err) {
        console.warn('resizeChart ignorado para o canvas:', canvas, err);
    }
}

/**
 * Habilita duplo-clique sobre um gráfico Chart.js usando o modo de interação
 * padrão (index + intersect). `resolve(index)` converte o índice em rótulo.
 * Usa o evento nativo (Chart.js não expõe onDblClick no options).
 */
function attachDoubleClick(element, chart, onDblClick, resolve) {
    if (!onDblClick || !element || !chart) return;
    element.addEventListener('dblclick', (event) => {
        try {
            const items = chart.getElementsAtEventForMode(event, 'index', { intersect: true }, false);
            if (items.length > 0) onDblClick(resolve ? resolve(items[0].index) : items[0].index);
        } catch (err) {
            console.warn('Duplo-clique ignorado no gráfico:', err);
        }
    });
}

const BRAZIL_GEOJSON_PATH = 'static/javascript/geo_info_Brazil/br-states.min.json'
let brazil_geoJSON = null

/** Interpola duas cores hex (#RRGGBB) com t ∈ [0,1] no espaço RGB. */
function interpolateHex(a, b, t) {
    const pa = [0, 1, 2].map((i) => parseInt(a.slice(1 + i * 2, 3 + i * 2), 16));
    const pb = [0, 1, 2].map((i) => parseInt(b.slice(1 + i * 2, 3 + i * 2), 16));
    const c = pa.map((v, i) => Math.round(v + (pb[i] - v) * t));
    return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

/** Nomes completos dos estados brasileiros (sigla UF → nome). */
const STATE_FULL_NAMES = {
    AC: 'Acre',
    AL: 'Alagoas',
    AP: 'Amapá',
    AM: 'Amazonas',
    BA: 'Bahia',
    CE: 'Ceará',
    DF: 'Distrito Federal',
    ES: 'Espírito Santo',
    GO: 'Goiás',
    MA: 'Maranhão',
    MT: 'Mato Grosso',
    MS: 'Mato Grosso do Sul',
    MG: 'Minas Gerais',
    PA: 'Pará',
    PB: 'Paraíba',
    PR: 'Paraná',
    PE: 'Pernambuco',
    PI: 'Piauí',
    RJ: 'Rio de Janeiro',
    RN: 'Rio Grande do Norte',
    RS: 'Rio Grande do Sul',
    RO: 'Rondônia',
    RR: 'Roraima',
    SC: 'Santa Catarina',
    SP: 'São Paulo',
    SE: 'Sergipe',
    TO: 'Tocantins',
};

async function loadGeoJSON() {
    if (!brazil_geoJSON) {
        try {
            const file = await fetch(BRAZIL_GEOJSON_PATH);
            if (!file.ok) throw new Error(`HTTP ${file.status}`);
            brazil_geoJSON = await file.json();
        } catch (err) {
            console.warn('Falha ao carregar o GeoJSON do Brasil:', err);
            brazil_geoJSON = null;
        }
    }
}

export function insert_horizontal_bar_chart(element, infos) {
    const labels = infos['labels'] || [];
    if (!element || !labels.length) {
        destroyChart(element);
        return;
    }
    // Ranking monocromático em Magenta: 1º lugar com cor cheia e os demais
    // decrescendo suavemente em opacidade (visual minimalista). Quando
    // `infos['selected']` coincide com o rótulo, a barra ganha Magenta cheio
    // e as restantes são rebaixadas (cross-filter com destaque visual).
    const selected = infos['selected'] || null;
    // `labelsMap` (Map rótulo-exibido → chave de filtro) permite exibir um rótulo
    // enriquecido (ex.: "Clemson (EUA)") mantendo o valor real usado no clique,
    // no dblclick e no destaque de cross-filter.
    const labelsMap = infos['labelsMap'] || null;
    const mapLabel = (label) => (labelsMap && labelsMap.has(label) ? labelsMap.get(label) : label);
    let color = [PRIMARY_PALETTE[0]];
    if (infos['rank']) {
        color = labels.map((label, i) => {
            if (selected && mapLabel(label) === selected) return `rgba(231, 43, 120, 1)`;
            if (selected) return `rgba(231, 43, 120, 0.12)`;
            const alpha = Math.max(0.3, 1 - i * 0.085);
            return `rgba(231, 43, 120, ${alpha.toFixed(2)})`;
        });
    }
    const ticks_data = new Set(infos['data'])
    const onClick = infos['onClick'] || null;
    const onDblClick = infos['onDblClick'] || null;
    const data = {
        labels: labels,
        datasets: [{
            axis: 'y',
            label: '',
            data: infos['data'],
            fill: false,
            backgroundColor: color,
            borderWidth: 0,
            borderRadius: 6,
        }]
    };
    const config = {
        type: 'bar',
        data,
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    right: 30
                }
            },
            onClick: onClick ? (evt, elements) => {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    onClick(mapLabel(labels[idx]));
                }
            } : undefined,
            onHover: (event, elements) => {
                event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
            },
            plugins: {
                legend: {
                    display: false
                },
                datalabels: {
                    anchor: "end",
                    align: "right",
                    font: {
                        size: 14
                    },
                    color: "#1E293B"
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        display: false,
                    },
                    ticks: {
                        stepSize: 1,
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    border: {
                        width: 2,
                        color: '#E2E8F0'
                    },
                },
            },
        }
    };
    const chart = mountChart(element, config)
    attachDoubleClick(element, chart, onDblClick, (idx) => mapLabel(labels[idx]));
}

export function insert_vertical_bar_chart(element, infos) {
    const labels = infos['labels'] || [];
    if (!element || !labels.length) {
        destroyChart(element);
        return;
    }
    // Barras verticais modernas: base Ciano suave com destaque em Magenta
    // oficial (função `highlight` recebe o rótulo e retorna true para destacar).
    // Quando `infos['selected']` (rótulo) é informado, a barra selecionada fica
    // Magenta cheio e as demais são rebaixadas ao Ciano translúcido
    // (cross-filter com destaque visual).
    const highlight = infos['highlight'] || null;
    const selected = infos['selected'] || null;
    const color = labels.map((label) => {
        if (selected && label === selected) return PRIMARY_PALETTE[0];
        if (highlight && highlight(label)) return PRIMARY_PALETTE[0];
        return selected ? 'rgba(54, 188, 238, 0.35)' : PRIMARY_PALETTE[1];
    });
    const ticks_data = new Set(infos['data'])
    const onClick = infos['onClick'] || null;
    const richTooltip = infos['tooltip'] || null;
    const onDblClick = infos['onDblClick'] || null;
    const data = {
        labels: labels,
        datasets: [{
            axis: 'y',
            label: '',
            data: infos['data'],
            fill: false,
            backgroundColor: color,
            borderWidth: 0,
            // Cantos arredondados apenas no topo (borderRadius: 6).
            borderRadius: { topLeft: 6, topRight: 6, bottomLeft: 0, bottomRight: 0 },
            maxBarThickness: 42,
        }]
    };
    const config = {
        type: 'bar',
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 30
                }
            },
            onClick: onClick ? (evt, elements) => {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    onClick(labels[idx]);
                }
            } : undefined,
            onHover: (event, elements) => {
                event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: (items) => items.length ? (items[0].label || '') : '',
                        label: (item) => {
                            const year = parseInt(String(item.label).split(' ')[0], 10);
                            const base = `${item.parsed.y} artigos`;
                            if (!richTooltip) return base;
                            const rows = richTooltip(year);
                            if (!rows || !rows.length) return base;
                            return [base, ...rows];
                        },
                    },
                },
                datalabels: {
                    anchor: "end",
                    align: "top",
                    font: {
                        size: 14
                    },
                    color: "#1E293B"
                }
            },
            scales: {
                y: {
                    grid: {
                        display: false
                    },
                    border: {
                        display: false,
                    },
                    ticks: {
                        stepSize: 1,
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        width: 2,
                        color: '#E2E8F0'
                    },
                },
            },
        }
    };
    const chart = mountChart(element, config)
    attachDoubleClick(element, chart, onDblClick, (idx) => labels[idx]);
}

/**
 * Gráfico de linhas por série declarativa. Espera:
 * infos = {labels, series: [{key, label, color, data}], onClick, onDblClick}
 * A identidade da série (cor/legenda) vem SEMPRE da chave explícita `key` e
 * nunca do índice numérico do array — assim um filtro que deixa apenas uma
 * série mantém a cor correta (ex.: Português=ciano, Inglês=magenta).
 */
export function insert_line_chart(element, infos) {
    const labels = infos['labels'] || [];
    const series = infos['series'] || [];
    if (!element || !labels.length || !series.length) {
        destroyChart(element);
        return;
    }
    const onClick = infos['onClick'] || null;
    const data = {
        labels: labels,
        datasets: series.map((s) => ({
            label: s.label,
            data: s.data,
            fill: true,
            backgroundColor: s.color + '1A', // ~10% de opacidade sob a linha
            borderColor: s.color,
            tension: 0.25,
            pointRadius: 3,
            pointHoverRadius: 6,
            borderWidth: 2.5,
            pointBackgroundColor: s.color,
        })),
    };
    const config = {
        type: 'line',
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: onClick ? (evt, elements) => {
                if (elements.length > 0) {
                    const el = elements[0];
                    const serie = series[el.datasetIndex] || series[0];
                    onClick(labels[el.index], serie.key, serie.label);
                }
            } : undefined,
            onHover: (event, elements) => {
                event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                datalabels: false
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        width: 2,
                        color: '#E2E8F0'
                    },
                    ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                    },
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        display: false
                    },
                    border: {
                        display: false,
                    },
                    ticks: {
                        stepSize: 1,
                        precision: 0,
                    }
                },
            },
        }
    };
    mountChart(element, config)
}

export function insert_area_chart(element, infos) {
    const labels = infos['labels'] || [];
    const values = infos['data'] || [];
    if (!element || !labels.length) {
        destroyChart(element);
        return;
    }
    const onClick = infos['onClick'] || null;
    const richTooltip = infos['tooltip'] || null;

    // Gradiente ciano suave preenchendo a área sob a linha.
    const ctx = typeof element.getContext === 'function' ? element.getContext('2d') : null;
    const gradient = ctx ? ctx.createLinearGradient(0, 0, 0, 300) : null;
    if (gradient) {
        gradient.addColorStop(0, 'rgba(54, 188, 238, 0.35)');
        gradient.addColorStop(0.6, 'rgba(54, 188, 238, 0.10)');
        gradient.addColorStop(1, 'rgba(54, 188, 238, 0.02)');
    }

    const config = {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Artigos',
                data: values,
                fill: gradient ? true : 'origin',
                backgroundColor: gradient || 'rgba(54, 188, 238, 0.12)',
                borderColor: PRIMARY_PALETTE[1],
                tension: 0.42,
                pointRadius: 4,
                pointHoverRadius: 7,
                borderWidth: 3,
                pointBackgroundColor: PRIMARY_PALETTE[1],
                pointBorderColor: '#FFFFFF',
                pointBorderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 28 } },
            onClick: onClick ? (evt, elements) => {
                if (elements && elements.length > 0) onClick(labels[elements[0].index]);
            } : undefined,
            onHover: (event, elements) => {
                event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: (items) => items.length ? (items[0].label || '') : '',
                        label: (item) => {
                            const year = parseInt(String(item.label).split(' ')[0], 10);
                            const base = `${item.parsed.y} artigo${item.parsed.y === 1 ? '' : 's'}`;
                            if (!richTooltip) return base;
                            const rows = richTooltip(year);
                            if (!rows || !rows.length) return base;
                            return [base, ...rows];
                        },
                    },
                },
                datalabels: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { display: false },
                    border: { display: false },
                    ticks: { stepSize: 1, precision: 0 },
                },
                x: {
                    grid: { display: false },
                    border: { width: 2, color: '#E2E8F0' },
                    ticks: { maxRotation: 0, autoSkip: true },
                },
            },
        },
    };
    mountChart(element, config);
}

function insert_doughnut_chart(element, infos) {
    const data = {
        labels: infos['labels'],
        datasets: [{
            label: '',
            data: infos['data'],
            backgroundColor: PRIMARY_PALETTE,
            hoverOffset: 6,
            borderWidth: 0,
        }]
    }
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            cutout: '70%',
            responsive: false,
            maintainAspectRatio: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            const data_sum = infos['data'].reduce((acc, value) => acc + value, 0)
                            const label = tooltipItem.label || '';
                            const value = tooltipItem.raw || '';

                            return `${label}: ${value} (${((value / data_sum) * 100).toFixed(1)}%)`;
                        }
                    },
                },
                datalabels: false
            },
        },
    }
    mountChart(element, config)
}

function insert_horizontal_bar_categories(element, infos) {
    const combined = infos['labels'].map((label, i) => ({label, value: infos['data'][i]}));
    combined.sort((a, b) => b.value - a.value);

    const gradient_colors = combined.map((_, i, arr) => {
        const t = arr.length > 1 ? i / (arr.length - 1) : 0;
        const r = Math.round(54 + t * (13 - 54));
        const g = Math.round(188 + t * (96 - 188));
        const b = Math.round(238 + t * (128 - 238));
        return `rgb(${r}, ${g}, ${b})`;
    });

    const data = {
        labels: combined.map(item => item.label),
        datasets: [{
            axis: 'y',
            label: '',
            data: combined.map(item => item.value),
            fill: false,
            backgroundColor: gradient_colors,
            borderWidth: 0,
            borderRadius: 6,
        }]
    };
    const config = {
        type: 'bar',
        data,
        options: {
            indexAxis: 'y',
            layout: {
                padding: { right: 30 }
            },
            plugins: {
                legend: { display: false },
                datalabels: {
                    anchor: "end",
                    align: "right",
                    font: { size: 13 },
                    color: "#1E293B"
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    border: { display: false },
                    ticks: { stepSize: 1 }
                },
                y: {
                    grid: { display: false },
                    border: { width: 2, color: '#E2E8F0' },
                },
            },
        }
    };
    mountChart(element, config)
}

function insert_radar_chart(element, infos) {
    const data = {
        labels: infos['labels'],
        datasets: [{
            label: '',
            fill: true,
            data: infos['data'],
            backgroundColor: PRIMARY_PALETTE[1] + '33',
            borderColor: PRIMARY_PALETTE[1],
            pointBackgroundColor: PRIMARY_PALETTE[1],
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: PRIMARY_PALETTE[1]
        }]
    };
    const config = {
        type: 'radar',
        data: data,
        options: {
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            const label = tooltipItem.label || '';
                            const value = tooltipItem.raw || '';

                            return `${label}: ${value}`;
                        }
                    },
                }
            },
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    beginAtZero: false,
                    pointLabels: {
                        font: {
                            size: 11
                        },

                    }
                }
            }
        },
    }
    mountChart(element, config)
}

/**
 * Gráfico de barras agrupadas para comparação entre dois anos (duas séries).
 * Espera infos = {labels, series: [{label, data}], onClick}
 */
export function insert_compare_bar_chart(element, infos) {
    const labels = infos['labels'] || [];
    if (!element || !labels.length) {
        destroyChart(element);
        return;
    }
    const series = infos['series'] || [];
    const group_colors = [PRIMARY_PALETTE[0], PRIMARY_PALETTE[1], PRIMARY_PALETTE[2], PRIMARY_PALETTE[3]];
    const onClick = infos['onClick'] || null;
    const config = {
        type: 'bar',
        data: {
            labels,
            datasets: series.map((s, i) => ({
                label: s.label,
                data: s.data,
                backgroundColor: group_colors[i % group_colors.length],
                borderColor: group_colors[i % group_colors.length],
                borderRadius: 6,
                maxBarThickness: 26,
            })),
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: onClick ? (evt, elements) => {
                if (elements.length > 0) onClick(labels[elements[0].index]);
            } : undefined,
            onHover: (event, elements) => {
                event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: { usePointStyle: true, boxWidth: 8 }
                },
                datalabels: {
                    anchor: "end",
                    align: "top",
                    font: { size: 12 },
                    color: "#1E293B"
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { display: false },
                    border: { display: false },
                    ticks: { stepSize: 1 }
                },
                x: {
                    grid: { display: false },
                    border: { width: 2, color: '#E2E8F0' },
                    ticks: { autoSkip: false }
                },
            },
        }
    };
    mountChart(element, config)
}

export function insert_cloud_word_chart(element, infos) {
    const onClick = infos['onClick'] || null;
    const onDblClick = infos['onDblClick'] || null;
    const wordLabels = infos['labels'] || [];
    const wordItems = infos['wordItems'] || null;
    const realCounts = infos['counts'] || null;
    if (!element || !wordLabels.length) {
        destroyChart(element);
        return;
    }

    // Fix: dimensiona o canvas com as dimensões reais do container pai antes
    // de desenhar. Sem isso a nuvem renderizava em um canvas 0x0 (em branco).
    const parent = element && element.parentElement ? element.parentElement : null;
    const clearCanvas = () => {
        const ctx = element && element.getContext ? element.getContext('2d') : null;
        if (ctx) ctx.clearRect(0, 0, element.width, element.height);
    };
    const sizeCanvas = () => {
        if (!parent) return;
        const rect = parent.getBoundingClientRect ? parent.getBoundingClientRect() : null;
        const width = rect && rect.width > 0 ? rect.width : (parent.offsetWidth || 600);
        const height = rect && rect.height > 0 ? rect.height : (parent.offsetHeight || 320);
        if (element.width !== Math.round(width)) element.width = Math.round(width);
        if (element.height !== Math.round(height)) element.height = Math.round(height);
        clearCanvas();
    };

    sizeCanvas();
    clearCanvas();

    const config = {
        type: "wordCloud",
        data: {
            labels: wordLabels,
            datasets: [
                {
                    label: '',
                    data: infos['data'],
                    // Ajusta a nuvem aos limites do canvas (escala proporcional
                    // sem cortar palavras nas bordas).
                    fit: true,
                },
            ],
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            // Margem de segurança em volta do desenho: nenhuma palavra encosta
            // na borda do card (.nuvem_palavras).
            layout: {
                padding: 16,
            },
            onClick: onClick ? (evt, elements) => {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    const item = wordItems ? wordItems[idx] : {text: wordLabels[idx], paper_ids: []};
                    onClick(item);
                }
            } : undefined,
            onHover: (event, elements) => {
                event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            const idx = tooltipItem.dataIndex;
                            const count = realCounts ? realCounts[idx] : tooltipItem.raw;
                            const unit = count === 1 ? ' artigo' : ' artigos';
                            return tooltipItem.label + ': ' + count + unit;
                        }
                    },
                    // Tooltip próprio, fixado ao cursor e limitado aos limites do
                    // card: nunca é cortado nas bordas nem sobreposto ao centro.
                    external: (context) => {
                        const { chart, tooltip } = context;
                        const card = element && element.closest ? element.closest('.graph-card') : null;
                        if (!card) return;
                        let tooltipEl = card.querySelector('.wordcloud-tooltip');
                        if (!tooltipEl) {
                            tooltipEl = document.createElement('div');
                            tooltipEl.className = 'wordcloud-tooltip';
                            card.appendChild(tooltipEl);
                        }
                        if (!tooltip.opacity || !tooltip.dataPoints || !tooltip.dataPoints.length) {
                            tooltipEl.style.opacity = '0';
                            tooltipEl.style.pointerEvents = 'none';
                            return;
                        }
                        const idx = tooltip.dataPoints[0].dataIndex;
                        const count = realCounts ? realCounts[idx] : null;
                        const label = wordLabels[idx] || '';
                        const unit = count === 1 ? ' artigo' : ' artigos';
                        tooltipEl.textContent = '';
                        const strong = document.createElement('b');
                        strong.textContent = label;
                        tooltipEl.appendChild(strong);
                        if (count !== null) {
                            const value = document.createElement('span');
                            value.textContent = count + unit;
                            tooltipEl.appendChild(value);
                        }

                        const cardRect = card.getBoundingClientRect();
                        const canvasRect = chart.canvas.getBoundingClientRect();
                        const caretX = tooltip.caretX || 0;
                        const caretY = tooltip.caretY || 0;
                        const margin = 10;
                        const relLeft = canvasRect.left - cardRect.left + caretX;
                        const relTop = canvasRect.top - cardRect.top + caretY;
                        let left = relLeft + margin + 6;
                        let top = relTop - tooltipEl.offsetHeight - margin;
                        if (top < margin) top = relTop + margin;
                        left = Math.max(margin, Math.min(left, cardRect.width - tooltipEl.offsetWidth - margin));
                        top = Math.max(margin, Math.min(top, cardRect.height - tooltipEl.offsetHeight - margin));
                        tooltipEl.style.left = left + 'px';
                        tooltipEl.style.top = top + 'px';
                        tooltipEl.style.pointerEvents = 'none';
                        tooltipEl.style.opacity = '1';
                    }
                },
                datalabels: false
            },
            elements: {
                word: {
                    font: {
                        family: "'Sofia Sans', sans-serif",
                    },
                    color: (ctx) => {
                        const colors = [PRIMARY_PALETTE[0], PRIMARY_PALETTE[1], PRIMARY_PALETTE[2], '#1E293B'];
                        return colors[ctx.index % colors.length];
                    },
                    padding: 6,
                }
            }
        },
    }

    const chart = mountChart(element, config)
    // Recupera o item clicado (palavra + ids) para o duplo-clique abrir o modal.
    attachDoubleClick(element, chart, onDblClick, (idx) => (wordItems ? wordItems[idx] : { text: wordLabels[idx], paper_ids: [] }));
}

export function insert_brazil_map_chart(element, infos) {
    if (!element) return;
    const onClick = infos['onClick'] || null;
    const onDblClick = infos['onDblClick'] || null;
    loadGeoJSON().then(geoJson => {
        if (!brazil_geoJSON) {
            console.warn('Mapa indisponível: GeoJSON não carregado.');
            return;
        }
        const states = topojson.feature(brazil_geoJSON, brazil_geoJSON.objects.states).features;
        const data = {
            labels: states.map(s => s.properties.name),
            datasets: [
                {
                    label: 'Estados',
                    outline: states, // features dos estados brasileiros
                    data: states.map((f) => ({
                        feature: f,
                        value: infos[f.properties.name] || 0,
                    })),
                }
            ]
        };
        // Contorno sutil + hover com borda fina de destaque.
        data.datasets[0].borderWidth = 0.75;
        data.datasets[0].borderColor = 'rgba(255, 255, 255, 0.85)';
        data.datasets[0].hoverBorderColor = '#0D6080';
        data.datasets[0].hoverBorderWidth = 2;

        // Configuração PADRÃO do chartjs-chart-geo: sem projeção manual.
        // O auto-fit nativo calcula escala/centro a partir do bounding box
        // das features — nada de bounding box/radianos/memoização próprios,
        // que transladavam o desenho para fora do canvas e travavam a thread.
        const config = {
            type: ChoroplethController.id,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                onClick: onClick ? (evt, elements) => {
                    if (elements.length > 0) {
                        const idx = elements[0].index;
                        const stateName = states[idx].properties.name;
                        onClick(stateName);
                    }
                } : undefined,
                onHover: (event, elements) => {
                    event.native.target.style.cursor = (elements && elements.length > 0) ? 'pointer' : 'default';
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    datalabels: false,
                    tooltip: {
                        callbacks: {
                            label: function (tooltipItem) {
                                const raw = tooltipItem.raw || {};
                                const sigla = raw.feature
                                    ? (raw.feature.properties.name || raw.feature.properties.sigla || raw.feature.id)
                                    : (tooltipItem.label || '');
                                const full = STATE_FULL_NAMES[sigla] || sigla;
                                const count = raw.value || 0;
                                return `${full} (${sigla}): ${count} artigo${count === 1 ? '' : 's'}`;
                            }
                        },
                    }
                },
                scales: {
                    projection: {
                        axis: 'x',
                        projection: 'geoMercator',
                        // Sem projectionScale/projectionOffset: auto-fit nativo
                    },
                    color: {
                        axis: 'x',
                        // Régua nativa desativada: os números sobrepunham-se no canto
                        // inferior. A legenda agora é HTML/CSS própria abaixo do mapa.
                        display: false,
                        quantize: 5,
                        // O chartjs-chart-geo passa o valor JÁ normalizado [0,1]
                        // ao interpolate — gradiente suave do tom claro ao navy.
                        interpolate: (value) => interpolateHex(
                            '#E2E8F0',
                            '#003358',
                            Math.max(0, Math.min(1, Number(value) || 0))
                        ),
                    }
                },
            }
        };

        const chart = mountChart(element, config, ChoroplethChart);
        attachDoubleClick(element, chart, onDblClick, (idx) => states[idx].properties.name);

        // Legenda HTML/CSS abaixo do mapa: mantém os rótulos min/max sincronizados
        // com o conjunto filtrado (estado com mais/menos artigos).
        const setLegendText = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.textContent = text;
        };
        const stateCounts = states.map((f) => infos[f.properties.name] || 0);
        const defined = stateCounts.length ? stateCounts : [0];
        const minState = Math.min(...defined);
        const maxState = Math.max(...defined);
        setLegendText('map-legend-min', `Menos artigos (${Math.max(1, minState)})`);
        setLegendText('map-legend-max', `Mais artigos (${Math.max(1, maxState)})`);
    })
}

window.insert_horizontal_bar_chart = insert_horizontal_bar_chart;
window.insert_horizontal_bar_categories = insert_horizontal_bar_categories;
window.insert_line_chart = insert_line_chart;
window.insert_area_chart = insert_area_chart;
window.insert_doughnut_chart = insert_doughnut_chart;
window.insert_cloud_word_chart = insert_cloud_word_chart;
window.insert_brazil_map_chart = insert_brazil_map_chart;
window.insert_radar_chart = insert_radar_chart;
window.insert_vertical_bar_chart = insert_vertical_bar_chart;
