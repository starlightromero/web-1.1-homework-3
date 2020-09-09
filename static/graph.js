/*  global
    fetch
*/

let timeArray
let tempArray
let maxTemp
let minTemp

async function fetchText () {
  const response = await fetch('static/data.txt')
  const data = await response.text()
  const dataArray = data.split('\n')
  timeArray = dataArray[0].substring(1, dataArray[0].length - 2).replace(/["']/g, '').split(', ')
  tempArray = dataArray[1].substring(1, dataArray[1].length - 2).split(', ')
  tempArray = tempArray.map(Number)
  maxTemp = Math.max(...tempArray)
  minTemp = Math.min(...tempArray)

  const ctx = document.getElementById('tempChart').getContext('2d')
  const tempChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timeArray,
      datasets: [{
        label: 'Temperature',
        data: tempArray,
        backgroundColor: '#FF5100',
        borderColor: '#FF5100',
        borderWidth: 1
      }]
    },
    options: {
      legend: {
        labels: {
          fontColor: '#fff'
        }
      },
      scales: {
        yAxes: [{
          gridLines: {
            color: '#F79061'
          },
          ticks: {
            beginAtZero: false,
            suggestedMin: minTemp,
            suggestedMax: maxTemp,
            fontColor: '#fff'
          }
        }],
        xAxes: [{
          gridLines: {
            color: '#F79061'
          },
          ticks: {
            fontColor: '#fff'
          }
        }]
      }
    }
  })
}

fetchText()
