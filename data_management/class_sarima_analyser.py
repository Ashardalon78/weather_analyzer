import json
import pathlib

import pandas as pd
import numpy as np

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.eval_measures import rmse

#from analyse_weatherdata.class_weather_data import WeatherData

class WeatherSarimaAnalyser():
    quantities = ['temperature_2m_mean', 'temperature_2m_max', 'temperature_2m_min',
                  'rain_sum', 'snowfall_sum', 'windspeed_10m_max', 'shortwave_radiation_sum']

    def __init__(self, data):
        self.avg_raw = data
    # def __init__(self, filenames: list[str | pathlib.Path]):
    #     wd = WeatherData()
    #     self.all_raw = []
    #
    #     for filename in filenames:
    #         self.all_raw.append({})
    #         wd.set_data_collection(filename)
    #
    #         for quantity in self.quantities:
    #             self.all_raw[-1][quantity] = wd.df_monthly[quantity]
    #
    #     self._calc_raw_average()

    # def _calc_raw_average(self):
    #     self.avg_raw = {}
    #     for quantity in self.quantities:
    #         data4avg = []
    #         for location in self.all_raw:
    #             data4avg.append(location[quantity])
    #         self.avg_raw[quantity] = pd.Series(np.mean(data4avg,axis=0), index=data4avg[0].index)

    def _sarima_configs(self) -> list[list[tuple[int,int,int],tuple[int,int,int,int]]]:
        model_configs = []
        p_params = [0, 1, 2]
        d_params = [0, 1]
        q_params = [0, 1, 2]
        P_params = [0, 1, 2]
        D_params = [0, 1]
        Q_params = [0, 1, 2]
        m_params = [12]

        for p in p_params:
            for d in d_params:
                for q in q_params:
                    for P in P_params:
                        for D in D_params:
                            for Q in Q_params:
                                for m in m_params:
                                    model_configs.append([(p, d, q), (P, D, Q, m)])
        #model_configs = [[(0, 1, 0), (0, 0, 0, 12)]]
        return model_configs

    def _sarima_forecast(self, train: pd.Series, cfg: list[list[tuple[int,int,int],tuple[int,int,int,int]]],
                         n_forecast_steps: int = 120) -> 'SARIMAXResultsWrapper, pd.Series, pd.Series':
        order, seasonal_order = cfg
        model = SARIMAX(train, order=order, seasonal_order=seasonal_order)
        model_fit = model.fit(disp=0)
        y_pred = model_fit.predict(0, len(train) - 1)
        y_forec = model_fit.predict(len(train), len(train) + n_forecast_steps)

        return model_fit, y_pred, y_forec

    # def sarima_forecast_with_best_config(self, ):
    #     filepath = pathlib.Path(f'best_models/best_sarima_models.json')
    #     with open(filepath, 'r') as ifile:
    #         best_configs = json.load(self.best_configs, ifile)

    def load_best_sarima_config(self, relpath: str):
        #filepath = pathlib.Path(f'best_models/best_sarima_models.json')
        filepath = pathlib.Path(relpath)
        with open(filepath, 'r') as ifile:
            self.best_configs = json.load(ifile)

    def sarima_grid_search(self, data: pd.Series, model_configs: list[tuple,tuple], n_forecast_steps: int = 120) -> 'list, list, list':
        # fitted_models = []
        predictions = []
        forecasts = []
        scores = []

        for cfg in model_configs:
            print(cfg)
            try:
                model_fit, pred, forec = self._sarima_forecast(data, cfg, n_forecast_steps)
                # fitted_models.append(model_fit)
                predictions.append(pred)
                forecasts.append(forec)
                scores.append(rmse(pred, data))
            except:
                print('Fit failed')
                # fitted_models.append(None)
                predictions.append(pd.Series(dtype='float64'))
                forecasts.append(pd.Series(dtype='float64'))
                scores.append(float('inf'))

        return predictions, forecasts, scores

    def find_best_sarima_params(self):
        self.best_configs = {}

        for quantity in self.quantities:
            raw = self.avg_raw[quantity].copy()

            model_configs = self._sarima_configs()

            predictions, forecasts, scores = self.sarima_grid_search(raw, model_configs)

            #best_pd = predictions[scores.index(min(scores))]
            #best_fc = forecasts[scores.index(min(scores))]
            self.best_configs[quantity] = model_configs[scores.index(min(scores))]
            #best_predictions_forecasts[quantity] = pd.concat([best_pd, best_fc])

        filepath = pathlib.Path(f'best_models/best_sarima_models.json')
        with open(filepath, 'w') as ofile:
            json.dump(self.best_configs, ofile)