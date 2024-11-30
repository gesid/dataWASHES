import {Chart, registerables} from "https://esm.sh/chart.js";
import {WordCloudController, WordElement} from "https://esm.sh/chartjs-chart-wordcloud";
import {
    topojson,
    ChoroplethController,
    GeoFeature,
    ProjectionScale,
    ColorScale,
} from "https://esm.sh/chartjs-chart-geo";

Chart.register(WordCloudController, WordElement, ChoroplethController, GeoFeature, ProjectionScale, ColorScale, ...registerables);

const BRAZIL_GEOJASON = "static/javascript/geo_info_Brazil/br-states.min.json"

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
            plugins: {
                legend: {
                    display: false
                },
            },
            scales: {
                x: {
                    grid: {
                        display: true
                    },
                    border: {
                        display: false,
                    },
                    ticks: {
                        callback: function (value, index, ticks) {
                            return ticks_data.has(value) ? value : null;
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
                    position: 'left'
                },
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
        labels: [
            'estatística descritiva',
            'regressão logística',
            'regressão linear',
            'análise de conteúdo',
            'análise de discurso',
            'análise temática',
            'Quantitativa',
            'Qualitativa',
        ],
        datasets: [{
            label: 'My First Dataset',
            data: [300, 250, 200, 140, 100, 100, 20, 50],
            backgroundColor: [
                '#003D6A',
                '#22CBE4',
                '#2662F0'
            ],
            hoverOffset: 4
        }]
    }
    const config = {
        type: 'doughnut',
        data: data,
        options: {
            cutout: '60%',
        },
    }
    new Chart(element, config)
}

function insert_radar_chart(element, infos) {
    const data = {
        labels: [
            'estatística descritiva',
            'regressão logística',
            'regressão linear',
            'análise de conteúdo',
            'análise de discurso',
            'análise temática',
            'Quantitativa',
            'Qualitativa',
        ],
        datasets: [{
            label: 'My First Dataset',
            fill: true,
            data: [300, 250, 100, 190, 120, 100, 150, 50],
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
            },
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
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
        type: 'wordCloud',
        data: {
            labels: infos['labels'],
            datasets: [
                {
                    label: 'Frequência',
                    data: infos['data'],
                },
            ],
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
            },
            elements: {
                word: {
                    fontFamily: 'sans-serif',
                    color: (ctx) => {
                        // Define uma cor para cada palavra com base no índice
                        const colors = ['#003D6A', '#22CBE4', '#2662F0', '#333333'];
                        return colors[ctx.index % colors.length];
                    },

                }
            }
        },
    }

    new Chart(element, config)
}

function insert_brazil_map_chart(element, infos) {
    fetch(BRAZIL_GEOJASON)
        .then(response => response.json())
        .then(geoJson => {
            const states = topojson.feature(geoJson, geoJson.objects.states).features;
            console.log(states)
            const data = {
                labels: states.map(s => s.properties.name),
                datasets: [
                    {
                        label: 'Publicações',
                        data: states.map((d) => ({feature: d, value: infos[d.properties.name] || 0})),
                    }
                ]
            };
            const config = {
                type: 'choropleth',
                data: data,
                options: {
                    plugins: {
                        legend: {
                            display: false
                        },
                    },
                    scales: {
                        projection: {
                            axis: 'x',
                            projection: 'geoMercator',
                            projectionScale: 8,
                            projectionOffset: [320, -100],
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

            new Chart(element, config);
        })
}

window.insert_horizontal_bar_chart = insert_horizontal_bar_chart;
window.insert_line_chart = insert_line_chart;
window.insert_doughnut_chart = insert_doughnut_chart;
window.insert_cloud_word_chart = insert_cloud_word_chart;
window.insert_brazil_map_chart = insert_brazil_map_chart;
window.insert_radar_chart = insert_radar_chart;
