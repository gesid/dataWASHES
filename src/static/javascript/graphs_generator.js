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

Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

const PRIMARY_PALETTE = ['#0EA5E9', '#2563EB', '#7C3AED', '#059669', '#F59E0B', '#64748B'];

const BRAZIL_GEOJSON_PATH = 'static/javascript/geo_info_Brazil/br-states.min.json'
let brazil_geoJSON = null

async function loadGeoJSON() {
    if (!brazil_geoJSON) {
        const file = await fetch(BRAZIL_GEOJSON_PATH)
        brazil_geoJSON = await file.json()
    }
}

function insert_horizontal_bar_chart(element, infos) {
    const labels = infos['labels'];
    let color = [PRIMARY_PALETTE[0]]
    if (infos['rank']) {
        let rank_color = PRIMARY_PALETTE[0]
        let week_color = PRIMARY_PALETTE[0] + '66'
        for (let i = 1; i < infos['labels'].length; i++) {
            if (i <= 2)
                color.push(rank_color)
            else
                color.push(week_color)
        }
    }
    const ticks_data = new Set(infos['data'])
    const onClick = infos['onClick'] || null;
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
            layout: {
                padding: {
                    right: 30
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
    new Chart(element, config)
}

function insert_vertical_bar_chart(element, infos) {
    const labels = infos['labels'];
    const count = labels.length;
    const color = labels.map((_, i) => {
        const t = count > 1 ? i / (count - 1) : 0;
        const r = Math.round(14 + t * (37 - 14));
        const g = Math.round(165 + t * (99 - 165));
        const b = Math.round(233 + t * (235 - 233));
        return `rgb(${r}, ${g}, ${b})`;
    });
    const ticks_data = new Set(infos['data'])
    const onClick = infos['onClick'] || null;
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
    new Chart(element, config)
}

function insert_line_chart(element, infos) {
    const line_colors = [PRIMARY_PALETTE[1], PRIMARY_PALETTE[0]]
    const fill_colors = [PRIMARY_PALETTE[1] + '20', PRIMARY_PALETTE[0] + '20']
    const onClick = infos['onClick'] || null;
    const langs = infos['langs'];
    const years = infos['labels'];
    const rawData = infos['data'];
    const data = {
        labels: years,
        datasets: langs.map((language, index) => ({
            label: language,
            data: rawData.map(d => d[language] || 0),
            fill: true,
            backgroundColor: fill_colors[index % fill_colors.length],
            borderColor: line_colors[index % line_colors.length],
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2.5,
            pointBackgroundColor: line_colors[index % line_colors.length],
        }))
    };
    const config = {
        type: 'line',
        data,
        options: {
            onClick: onClick ? (evt, elements) => {
                if (elements.length > 0) {
                    const el = elements[0];
                    const yearLabel = years[el.index];
                    const lang = langs[el.datasetIndex];
                    onClick(yearLabel, lang);
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
                },
                y: {
                    grid: {
                        display: false
                    },
                    border: {
                        display: false,
                    },
                    ticks: {
                        display: false,
                    }
                },
            },
        }
    };
    new Chart(element, config)
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
    new Chart(element, config)
}

function insert_horizontal_bar_categories(element, infos) {
    const combined = infos['labels'].map((label, i) => ({label, value: infos['data'][i]}));
    combined.sort((a, b) => b.value - a.value);

    const gradient_colors = combined.map((_, i, arr) => {
        const t = arr.length > 1 ? i / (arr.length - 1) : 0;
        const r = Math.round(14 + t * (37 - 14));
        const g = Math.round(165 + t * (99 - 165));
        const b = Math.round(233 + t * (235 - 233));
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
    new Chart(element, config)
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
    new Chart(element, config)
}

function insert_cloud_word_chart(element, infos) {
    const onClick = infos['onClick'] || null;
    const wordLabels = infos['labels'];
    const wordItems = infos['wordItems'] || null;
    const realCounts = infos['counts'] || null;
    const config = {
        type: "wordCloud",
        data: {
            labels: wordLabels,
            datasets: [
                {
                    label: '',
                    data: infos['data'],
                },
            ],
        },
        options: {
            responsive: false,
            maintainAspectRatio: true,
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
                    }
                },
                datalabels: false
            },
            elements: {
                word: {
                    fontFamily: 'sans-serif',
                    color: (ctx) => {
                        const colors = [PRIMARY_PALETTE[0], PRIMARY_PALETTE[1], PRIMARY_PALETTE[2], '#1E293B'];
                        return colors[ctx.index % colors.length];
                    },
                    padding: 5,
                }
            }
        },
    }

    new Chart(element, config)
}

function insert_brazil_map_chart(element, infos) {
    const onClick = infos['onClick'] || null;
    loadGeoJSON().then(geoJson => {
        const states = topojson.feature(brazil_geoJSON, brazil_geoJSON.objects.states).features;
        const data = {
            labels: states.map(s => s.properties.name),
            datasets: [
                {
                    label: 'Publicações',
                    data: states.map((d) => ({feature: d, value: infos[d.properties.name] || 0})),
                }
            ]
        };

        const containerWidth = element.parentElement.offsetWidth;
        const containerHeight = element.parentElement.offsetHeight;
        const projectionOffset = [containerWidth / 2 + 40, -containerHeight / 2 + 80];
        const config = {
            type: ChoroplethController.id,
            data: data,
            options: {
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
                                const value = tooltipItem.raw || '';
                                if (value.value === 1) {
                                    return `${value.feature.properties.name}: ${value.value} artigo`;
                                }
                                return `${value.feature.properties.name}: ${value.value} artigos`;
                            }
                        },
                    }
                },
                scales: {
                    projection: {
                        axis: 'x',
                        projection: 'geoMercator',
                        projectionScale: 8,
                        projectionOffset: projectionOffset,
                    },
                    color: {
                        axis: 'x',
                        legend: {
                            position: 'center-right',
                        },
                    }
                },
            }
        };

        new ChoroplethChart(element.getContext('2d'), config);
    })
}

window.insert_horizontal_bar_chart = insert_horizontal_bar_chart;
window.insert_horizontal_bar_categories = insert_horizontal_bar_categories;
window.insert_line_chart = insert_line_chart;
window.insert_doughnut_chart = insert_doughnut_chart;
window.insert_cloud_word_chart = insert_cloud_word_chart;
window.insert_brazil_map_chart = insert_brazil_map_chart;
window.insert_radar_chart = insert_radar_chart;
window.insert_vertical_bar_chart = insert_vertical_bar_chart;
