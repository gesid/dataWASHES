const BRAZIL_GEOJASON = "static/javascript/geo_info_Brazil/br.json"

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
    const ticks_data = infos['data'].toSorted()
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
                            const valuesToShow = ticks_data;
                            return valuesToShow.includes(value) ? value : null;
                        }
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
    const labels = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];
    const data = {
        labels: labels,
        datasets: [
            {
                label: 'pt',
                data: [65, 59, 80, 81, 56, 55, 40, 32, 32],
                fill: false,
                backgroundColor: 'rgba(5, 149, 253)',
                borderColor: 'rgba(5, 149, 253)',
            },
            {
                label: 'en',
                data: [35, 19, 40, 31, 96, 25, 30, 42, 12],
                fill: false,
                backgroundColor: '#2662F0',
                borderColor: '#2662F0',
            }
        ]
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
            'Red',
            'Blue',
            'Yellow'
        ],
        datasets: [{
            label: 'My First Dataset',
            data: [300, 50, 100],
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
            cutout: '70%',
        },
    }
    new Chart(element, config)
}

function insert_cloud_word_chart(element, infos) {
    const config = {
        type: 'wordCloud',
        data: {
            // text
            labels: ['Hello', 'world', 'normally', 'you', 'want', 'more', 'words', 'than', 'this'],
            datasets: [
                {
                    label: 'DS',
                    data: [90, 80, 70, 60, 50, 40, 30, 20, 10],
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
            console.log(geoJson)
            const data = {
                labels: geoJson.features.map(f => f.id),
                datasets: [
                    {
                        label: 'Publicações',
                        data: geoJson.features.map(f => ({
                            feature: f.geometry,
                            value: Math.random() * 11
                        })),
                    }
                ]
            };
            console.log(data)

            const config = {
                type: 'choropleth',
                data: data,
                options: {
                    scales: {
                        xy: {
                            projection: 'geoMercator' // Projeção para mapas
                        }
                    },
                    plugins: {
                        legend: {display: false}
                    }
                }
            };

            new Chart(element, config);
        })
}
