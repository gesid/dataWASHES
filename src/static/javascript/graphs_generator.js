function insert_horizontal_bar_chart(element, infos) {
    const labels = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];
    const data = {
      labels: labels,
      datasets: [{
        axis: 'y',
        label: '',
        data: [65, 59, 80, 81, 56, 55, 40, 32, 32],
        fill: false,
        backgroundColor: 'rgba(5, 149, 253)',
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
                      callback: function(value, index, ticks) {
                          const valuesToShow = [0, 10, 20, 30, 60, 80];
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
                  }
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
              data:  [35, 19, 40, 31, 96, 25, 30, 42, 12],
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