const openForecast = (forecast, e) => {
  // Get all elements with class="tabcontent" and hide them
  const tabcontent = document.getElementsByClassName('tabcontent')
  for (const content of tabcontent) {
    content.style.display = 'none'
  }

  // Get all elements with class="tablinks" and remove the class "active"
  const tablinks = document.getElementsByClassName('tablinks')
  for (const link of tablinks) {
    link.className = link.className.replace(' active', '')
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(forecast).style.display = 'block'
  e.currentTarget.className += ' active'
}

const current = document.getElementById('currentTab')
const minute = document.getElementById('minuteTab')
const hourly = document.getElementById('hourlyTab')
const daily = document.getElementById('dailyTab')

current.addEventListener('click', openForecast.bind(null, 'Current'))
minute.addEventListener('click', openForecast.bind(null, 'Minute'))
hourly.addEventListener('click', openForecast.bind(null, 'Hourly'))
daily.addEventListener('click', openForecast.bind(null, 'Daily'))

current.click()
