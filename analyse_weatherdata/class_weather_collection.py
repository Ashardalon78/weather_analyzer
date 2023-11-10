import pathlib
import numpy as np
import pandas as pd
from analyse_weatherdata.class_weather_data import WeatherData

class WeatherCollection():
    quantities = ['temperature_2m_mean', 'temperature_2m_max', 'temperature_2m_min',
                  'rain_sum', 'snowfall_sum', 'windspeed_10m_max', 'shortwave_radiation_sum']

    def __init__(self):
        self.all_raw = []

    def append_data(self, filepath: str | pathlib.Path):
        wd = WeatherData(filepath)
        self.all_raw.append({})

        for quantity in self.quantities:
            self.all_raw[-1][quantity] = wd.df_monthly[quantity]

    def calc_raw_average(self):
        self.avg_raw = {}
        for quantity in self.quantities:
            data4avg = []
            for location in self.all_raw:
                data4avg.append(location[quantity])
            self.avg_raw[quantity] = pd.Series(np.mean(data4avg,axis=0), index=data4avg[0].index)
