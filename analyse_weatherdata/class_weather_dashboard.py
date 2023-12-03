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
        #self.wd = WeatherData([self.lat_input.value, self.lon_input.value, '1950-01-01', self.end_date])
        #print('Dropdown', self.dropdown_cities.value)
        self.wd = WeatherData(self.dropdown_cities.value[0])
        self.wd.calculate_all_time_series(period=60)
        self.wd.extract_all_time_series_components()

        self.wc = WeatherCollection()
        self.wc.append_data(self.dropdown_cities.value[0])
        self.wc.calc_raw_average()

        self.wsa = WeatherSarimaAnalyser(self.wc.avg_raw)
        #self.wsa.load_best_sarima_config(f'data_management/best_models/best_sarima_models.json')
        try:
            self.wsa.load_best_sarima_config(pathlib.Path('data_management')
                                            .joinpath('best_models').joinpath('best_sarima_models.json'))
        except Exception as error:
            errtxt = f'{type(error)} {error}'
            self.row1[0] = pn.Row(pn.widgets.StaticText(value=errtxt))

        self.wd.load_sarima_forecast_from_disk(self.dropdown_cities.value[1])

        # filepath = pathlib.Path(f'best_models/fitted_models/prediction_{city_country}.json')
        # with open(filepath, 'w') as ofile:
        #     json.dump(best_fits, ofile)

        self.serve_data()

    def _get_cities_dict(self):
        dir_path = pathlib.Path('data_management').joinpath('json_data')
        dir_path_forecasts = pathlib.Path('data_management').joinpath('best_models').joinpath('fitted_models')
        self.cities_dict = {}

        for file_path in os.listdir(dir_path):
            full_path = pathlib.Path(dir_path).joinpath(file_path)
            if os.path.isfile(full_path) and file_path.endswith('json'):
                tmp1 = file_path.split('_')
                city = tmp1[-2]
                country = tmp1[-1].split('.')[0]
                city_country = f'{city}_{country}'
                #self.cities_dict[city_country] = full_path
                full_path_forecast = dir_path_forecasts.joinpath(f'prediction_{city_country}.json')
                self.cities_dict[city_country] = [full_path, full_path_forecast]

    def serve_data(self):
        symbols = list(self.wd.time_series_analyses.keys())
        self.dropdown_quantities = pn.widgets.Select(name='Select plot quantity', options=symbols)

        button_predict = pn.widgets.Button(name='Predict', button_type='primary')
        #button_predict.on_click(self._get_prediction)
        button_predict.on_click(self._load_prediction)
        self.row1[0] = pn.Row(self.dropdown_quantities, button_predict)

    def serve_data_old(self):
        idf = self.wd.time_series_components['trend'].interactive()

        #data2_element = hv.Curve(self.wd.time_series_components['trend']['temperature_2m_max'])
        #combined_plot = (idf + data2_element).cols(1)

        symbols = list(self.wd.time_series_analyses.keys())
        select = pn.widgets.Select(name='Select plot quantity', options=symbols)

        weather_pipeline = (idf[select])
        #weather_pipeline = self.data1_element #* data2_element
        weather_plot = weather_pipeline.hvplot().opts(width=600, height=400)
        #self.weather_plot = weather_pipeline

        self.row2[0] = pn.Column(select, weather_plot.panel())

        #button_predict = pn.widgets.Button(name='Predict', button_type='primary')
        #button_predict.on_click(self._get_prediction)
        #self.row1[0] = pn.Column(select, button_predict, self.weather_plot)

    def _get_prediction(self, event):
        try:
            model_fit, y_pred, y_forec = self.wsa.sarima_forecast(self.wc.avg_raw[self.dropdown_quantities.value],
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

    def _load_prediction(self, event):
        data1_element = hv.Curve(self.wd.time_series_components['trend'][self.dropdown_quantities.value].dropna()).opts(
            width=600, height=400)

        index = self.wd.forecast_collection[self.dropdown_quantities.value]['Time']
        index = [datetime.datetime.strptime(dt, '%Y-%m-%d') for dt in index]
        best_dec = pd.Series(self.wd.forecast_collection[self.dropdown_quantities.value]['Values'], index=index)
        data2_element = hv.Curve(best_dec)

        weather_pipeline = data1_element * data2_element
        self.weather_plot = weather_pipeline
        self.row2[0] = pn.Column(self.weather_plot)