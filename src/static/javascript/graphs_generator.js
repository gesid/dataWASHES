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
    let color = ['rgba(5, 149, 253)']
    if (infos['rank']) {
        let rank_color = color[0]
        let week_color = 'rgba(5, 149, 253, .5)'
        for (let i = 1; i < infos['labels'].length; i++) {
            if (i <= 2)
                color.push(rank_color)
            else
                color.push(week_color)
        }
    }
    const ticks_data = new Set(infos['data'])
    const data = {
        labels: labels,
        datasets: [{
            axis: 'y',
            label: '',
            data: infos['data'],
            fill: false,
            backgroundColor: color,
            borderWidth: 0,
        }]
    };
    const config = {
        type: 'bar',
        data,
        options: {
            indexAxis: 'y',
            layout: {
                padding: {
                    right: 30 // Ajuste esse valor para aumentar o espaço no topo
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                datalabels: {
                    anchor: "end",
                    align: "right",
                    font: {
                        //weight: "bold",
                        size: 14
                    },
                    color: "#000"
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
                        callback: function (value, index, ticks) {
                            //return ticks_data.has(value) ? value : null;
                        },
                        stepSize: 1,
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    border: {
                        width: 2,
                        color: 'rgb(0, 0, 0)'
                    },
                },
            },
        }
    };
    new Chart(element, config)
}

function insert_vertical_bar_chart(element, infos) {
    const labels = infos['labels'];
    let color = ['rgba(5, 149, 253)']
    if (infos['rank']) {
        let rank_color = color[0]
        let week_color = 'rgba(5, 149, 253, .5)'
        for (let i = 1; i < infos['labels'].length; i++) {
            if (i <= 2)
                color.push(rank_color)
            else
                color.push(week_color)
        }
    }
    const ticks_data = new Set(infos['data'])
    const data = {
        labels: labels,
        datasets: [{
            axis: 'y',
            label: '',
            data: infos['data'],
            fill: false,
            backgroundColor: color,
            borderWidth: 0,
        }]
    };
    const config = {
        type: 'bar',
        data,
        options: {
            layout: {
                padding: {
                    top: 30 // Ajuste esse valor para aumentar o espaço no topo
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                datalabels: {
                    anchor: "end",
                    align: "top",
                    font: {
                        //weight: "regular",
                        size: 14
                    },
                    color: "#000"
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
                        callback: function (value, index, ticks) {
                            //return ticks_data.has(value) ? value : null;
                        },
                        stepSize: 1,
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    border: {
                        width: 2,
                        color: 'rgb(0, 0, 0)'
                    },
                },
            },
        }
    };
    new Chart(element, config)
}

function insert_line_chart(element, infos) {
    const bg_colors = ['rgba(5, 149, 253)', '#2662F0']
    const data = {
        labels: infos['labels'],
        datasets: infos['langs'].map((language, index) => ({
            label: language,
            data: infos['data'].map(d => d[language] || 0),
            fill: false,
            backgroundColor: bg_colors[index % bg_colors.length],
            borderColor: bg_colors[index % bg_colors.length],
        }))
    };
    const config = {
        type: 'line',
        data,
        options: {
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
                        color: 'rgb(0, 0, 0)'
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
            backgroundColor: [
                "#003D6A",
                "#22CBE4",
                "#2662F0",
                "#005D94",
                "#1A9BC6",
                "#478BF4",
                "#004E7F",
                "#00A0C8",
                "#1E5FB8",
                "#3399FF",
                "#004B85",
                "#008DBD"
            ],
            hoverOffset: 6
        }]
    }
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            cutout: '60%',
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

function insert_radar_chart(element, infos) {
    const data = {
        labels: infos['labels'],
        datasets: [{
            label: '',
            fill: true,
            data: infos['data'],
            backgroundColor: 'rgba(38, 98, 240, .2)',
            borderColor: 'rgb(38, 98, 240)',
            pointBackgroundColor: '#2662F0',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#2662F0'
        }]
    }
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
                    pointLabels: { // Configurações dos rótulos das categorias
                        font: {
                            size: 11 // Define o tamanho da fonte (em pixels)
                        },

                    }
                }
            }
        },
    }
    new Chart(element, config)
}

function insert_cloud_word_chart(element, infos) {
    const config = {
        type: "wordCloud",
        data: {
            labels: infos['labels'],
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
            plugins: {
                legend: {
                    display: false
                },
                datalabels: false
            },
            elements: {
                word: {
                    fontFamily: 'sans-serif',
                    color: (ctx) => {
                        // Define uma cor para cada palavra com base no índice
                        const colors = ['#003D6A', '#22CBE4', '#2662F0', '#333333'];
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

        // Obtém as dimensões do contêiner
        const containerWidth = element.parentElement.offsetWidth;
        const containerHeight = element.parentElement.offsetHeight;
        // Calcula o deslocamento com base nas dimensões do contêiner
        const projectionOffset = [containerWidth / 2 + 40, -containerHeight / 2 + 80];
        console.log(projectionOffset)
        const config = {
            type: ChoroplethController.id,
            data: data,
            options: {
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
window.insert_line_chart = insert_line_chart;
window.insert_doughnut_chart = insert_doughnut_chart;
window.insert_cloud_word_chart = insert_cloud_word_chart;
window.insert_brazil_map_chart = insert_brazil_map_chart;
window.insert_radar_chart = insert_radar_chart;
window.insert_vertical_bar_chart = insert_vertical_bar_chart;