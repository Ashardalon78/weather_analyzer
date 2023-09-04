import panel as pn
import hvplot.pandas
import requests
import datetime
from analyse_weatherdata.class_weather_data import WeatherData

pn.extension()

class WeatherDashboard():
    def __init__(self):
        self.end_date = datetime.datetime.today() - datetime.timedelta(days=7)
        self.end_date = self.end_date.strftime('%Y-%m-%d')
        self.main_widget()

    def main_widget(self):
        self.lat_input = pn.widgets.TextInput(name='Latitude', placeholder='Enter latitude here...')
        self.lon_input = pn.widgets.TextInput(name='Longitude', placeholder='Enter longitude here...')
        button_get_data = pn.widgets.Button(name='Get Data', button_type='primary')
        button_get_data.on_click(self._get_data)

        self.template = pn.template.FastListTemplate(
            title='Weather Data',
        )
        self.row1 = pn.Row(self.lat_input, self.lon_input)
        self.column1 = pn.Column(self.row1, button_get_data)
        self.template.main.append(self.column1)
        self.row2 = pn.Row(pn.Row())
        self.template.main.append(self.row2)
        self.template.show()

    def _get_data(self, event):

        req_url = f'https://archive-api.open-meteo.com/v1/archive?latitude={self.lat_input.value}' \
                  f'&longitude={self.lon_input.value}&start_date=1950-01-01&end_date={self.end_date}' \
                  f'&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,rain_sum' \
                  f',snowfall_sum,windspeed_10m_max,shortwave_radiation_sum&timezone=GMT'

        req = requests.get(url=req_url)
        self.data_dict = req.json()

        self.wd = WeatherData([self.lat_input.value, self.lon_input.value, '1950-01-01', self.end_date])
        self.wd.calculate_all_time_series(period=120)
        self.wd.extract_all_time_series_components()

        self.serve_data()

    def serve_data(self):
        idf = self.wd.time_series_components['trend'].interactive()
        symbols = list(self.wd.time_series_analyses.keys())
        select = pn.widgets.Select(name='Select plot quantity', options=symbols)

        weather_pipeline = (idf[select])
        weather_plot = weather_pipeline.hvplot()

        self.row2[0] = pn.Column(select, weather_plot.panel())
