"""Import Modules."""
import jinja2
import os
from pprint import PrettyPrinter
import requests

from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim
from io import BytesIO

# ##############################################################################
# SETUP
# ##############################################################################
app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv('API_KEY')

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('data'),
])
app.jinja_loader = my_loader

pp = PrettyPrinter(indent=4)


# ##############################################################################
# HELPER FUNCTIONS
# ##############################################################################


def get_min_temp(results):
    """Return the minimum temp for the given hourly weather objects."""
    return min([hour['temp'] for hour in results])


def get_max_temp(results):
    """Return the maximum temp for the given hourly weather objects."""
    return max([hour['temp'] for hour in results])


def get_lat_lon(zip):
    """Get latitude and longitude from a given city."""
    geolocator = Nominatim(user_agent='Weather Application')
    location = geolocator.geocode(f"{zip}, USA")
    if location is not None:
        return location.latitude, location.longitude
    return 0, 0


def get_letter_for_units(units):
    """Return a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'


def write_hourly_results_to_file(results, filename):
    time_list = []
    temp_list = []

    for hour in results:
        time = datetime.fromtimestamp(hour['dt']).strftime('%-I:%M %p')
        time_list.append(time)
        temp_list.append(hour['temp'])

    try:
        f = open(filename, 'w')
        f.write(f"{time_list}\n{temp_list}")
        f.close()
    except:
        pass


# ##############################################################################
# ROUTES
# ##############################################################################


@app.errorhandler(404)
def page_not_found(e):
    """Display page not found."""
    print(e)
    return render_template('404.html')


@app.errorhandler(500)
def error(e):
    """Display internal error page."""
    print(e)
    return render_template('500.html')


@app.route('/')
def home():
    """Display the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)


@app.route('/results')
def results():
    """Display results for current weather conditions."""
    zip = request.args.get('zip')
    units = request.args.get('units')

    url = 'https://api.openweathermap.org/data/2.5/onecall'

    latitude, longitude = get_lat_lon(zip)

    params = {
        "lat": latitude,
        "lon": longitude,
        "units": units,
        "appid": API_KEY
    }

    result_json = requests.get(url, params=params).json()
    current = result_json['current']
    minutes = result_json['minutely']
    hours = result_json['hourly']
    days = result_json['daily']

    minute_list = []
    hour_list = []
    day_list = []

    for minute in minutes:
        minute_list.append(
            datetime.fromtimestamp(minute['dt']).strftime('%-I:%M %p')
        )

    for hour in hours:
        hour_list.append(
            datetime.fromtimestamp(hour['dt']).strftime('%B %d, %-I:%M %p')
        )

    for day in days:
        day_list.append(
            datetime.fromtimestamp(day['dt']).strftime('%A, %B %d, %Y')
        )

    # pp.pprint(result_json)

    context = {
        'date': datetime.fromtimestamp(current['dt'])
        .strftime('%A, %B %d, %Y'),
        'zip': zip,
        'description': current['weather'][0]['description'],
        'temp': current['temp'],
        'humidity': current['humidity'],
        'wind_speed': current['wind_speed'],
        'sunrise': datetime.fromtimestamp(current['sunrise'])
        .strftime('%I:%M %p'),
        'sunset': datetime.fromtimestamp(current['sunset'])
        .strftime('%I:%M %p'),
        'units_letter': get_letter_for_units(units),
        'icon': current['weather'][0]['icon'],
        'minute_list': minute_list,
        'minutes': minutes,
        'hour_list': hour_list,
        'hours': hours,
        'day_list': day_list,
        'days': days,
    }

    return render_template('results.html', **context)


@app.route('/historical_results')
def historical_results():
    """Display historical weather forecast for a given day."""
    zip = request.args.get('zip')
    date = request.args.get('date')
    units = request.args.get('units')
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    date_in_seconds = date_obj.strftime('%s')

    latitude, longitude = get_lat_lon(zip)

    url = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'
    params = {
        "lat": latitude,
        "lon": longitude,
        "units": units,
        "dt": date_in_seconds,
        "appid": API_KEY
    }

    result_json = requests.get(url, params=params).json()

    # pp.pprint(result_json)

    result_current = result_json['current']
    result_hourly = result_json['hourly']

    write_hourly_results_to_file(result_hourly, "static/data.txt")

    context = {
        'zip': zip,
        'date': date_obj,
        'lat': latitude,
        'lon': longitude,
        'units': units,
        'units_letter': get_letter_for_units(units),
        'description': result_current['weather'][0]['description'],
        'temp': result_current['temp'],
        'min_temp': get_min_temp(result_hourly),
        'max_temp': get_max_temp(result_hourly),
        'icon': result_current['weather'][0]['icon'],
        'result_hourly': result_hourly
    }

    return render_template('historical_results.html', **context)


if __name__ == '__main__':
    app.run()
