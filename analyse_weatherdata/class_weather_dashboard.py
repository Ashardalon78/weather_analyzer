import pandas as pd
import panel as pn
import holoviews as hv
import hvplot.pandas
import requests
import datetime
import pathlib
import os
from analyse_weatherdata.class_weather_data import WeatherData
from analyse_weatherdata.class_weather_collection import WeatherCollection
from data_management.class_sarima_analyser import WeatherSarimaAnalyser

pn.extension()

class WeatherDashboard():
    def __init__(self):
        self.end_date = datetime.datetime.today() - datetime.timedelta(days=7)
        self.end_date = self.end_date.strftime('%Y-%m-%d')
        self._get_cities_dict()
        self.main_widget()

    def main_widget(self):
        #self.lat_input = pn.widgets.TextInput(name='Latitude', placeholder='Enter latitude here...')
        button_get_data = pn.widgets.Button(name='Get Data', button_type='primary')
        button_get_data.on_click(self._get_data)
        self.dropdown_cities = pn.widgets.Select(name='Select city', options=self.cities_dict)

        self.template = pn.template.FastListTemplate(
            title='Weather Data',
        )

        self.column1 = pn.Column(self.dropdown_cities, button_get_data)
        self.template.main.append(self.column1)
        self.row1 = pn.Row(pn.Row())
        self.template.main.append(self.row1)
        self.row2 = pn.Row(pn.Row())
        self.template.main.append(self.row2)
        #self.template.show()

    def _get_data(self, event):
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='1'))
        #self.wd = WeatherData([self.lat_input.value, self.lon_input.value, '1950-01-01', self.end_date])
        self.wd = WeatherData(self.dropdown_cities.value)
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='2'))
        self.wd.calculate_all_time_series(period=60)
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='3'))
        self.wd.extract_all_time_series_components()
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='4'))

        self.wc = WeatherCollection()
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='5'))
        self.wc.append_data(self.dropdown_cities.value)
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='6'))
        self.wc.calc_raw_average()
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='7'))

        self.wsa = WeatherSarimaAnalyser(self.wc.avg_raw)
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='8'))
        #self.wsa.load_best_sarima_config(f'data_management/best_models/best_sarima_models.json')
        self.wsa.load_best_sarima_config(pathlib.Path('data_management')
                                         .joinpath('best_models').joinpath('best_sarima_models.json'))
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='9'))
        self.serve_data()

    def _get_cities_dict(self):
        dir_path = pathlib.Path('data_management').joinpath('json_data')
        self.cities_dict = {}

        for file_path in os.listdir(dir_path):
            full_path = pathlib.Path(dir_path).joinpath(file_path)
            if os.path.isfile(full_path) and file_path.endswith('json'):
                tmp1 = file_path.split('_')
                city = tmp1[-2]
                country = tmp1[-1].split('.')[0]
                city_country = f'{city}_{country}'
                self.cities_dict[city_country] = full_path

    def serve_data(self):
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='10'))
        symbols = list(self.wd.time_series_analyses.keys())
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='11'))
        self.dropdown_quantities = pn.widgets.Select(name='Select plot quantity', options=symbols)
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='12'))

        button_predict = pn.widgets.Button(name='Predict', button_type='primary')
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='13'))
        button_predict.on_click(self._get_prediction)
        self.row1[0] = pn.Row(pn.widgets.StaticText(value='14'))
        #self.row1[0] = pn.Row(self.dropdown_quantities, button_predict)

    def serve_data_old(self):
        #idf = self.wd.time_series_components['trend'].interactive()
        #idf = hv.Curve(self.wd.time_series_components['trend'], ['temperature_2m_mean']).opts(width=600, height=400)
        self.data1_element = hv.Curve(self.wd.time_series_components['trend']['temperature_2m_mean']).opts(width=600, height=400)
        #print(self.wd.time_series_components['trend'].index)

        data2_element = hv.Curve(self.wd.time_series_components['trend']['temperature_2m_max'])
        #combined_plot = (idf + data2_element).cols(1)

        symbols = list(self.wd.time_series_analyses.keys())
        select = pn.widgets.Select(name='Select plot quantity', options=symbols)

        #weather_pipeline = (idf[select])
        weather_pipeline = self.data1_element #* data2_element
        #weather_plot = weather_pipeline.hvplot()
        self.weather_plot = weather_pipeline

        #self.row2[0] = pn.Column(select, weather_plot.panel())

        button_predict = pn.widgets.Button(name='Predict', button_type='primary')
        button_predict.on_click(self._get_prediction)
        self.row1[0] = pn.Column(select, button_predict, self.weather_plot)

    def _get_prediction(self, event):
        try:
            model_fit, y_pred, y_forec = self.wsa._sarima_forecast(self.wc.avg_raw[self.dropdown_quantities.value],
                                                            self.wsa.best_configs[self.dropdown_quantities.value])
            best_pd_fc = pd.concat([y_pred, y_forec])
            best_dec = self.wd.decompose_timeseries(best_pd_fc, period=60)
            data2_element = hv.Curve(best_dec.trend)
        except:
            data2_element = hv.Curve(pd.Series())

        data1_element = hv.Curve(self.wd.time_series_components['trend'][self.dropdown_quantities.value]).opts(
            width=600, height=400)

        weather_pipeline = data1_element * data2_element
        self.weather_plot = weather_pipeline
        self.row2[0] = pn.Column(self.weather_plot)