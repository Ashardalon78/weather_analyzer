import requests
import json
import pathlib
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

class WeatherData():
    def __init__(self, ini=None, name=None):
        if ini is not None:
            self.set_data_collection(ini, name=name)
        else:
            self.data_collection = {}

        self.time_series_analyses = {}

####################
#private methods
####################

    def _generate_api_url(self, lat: str, lon: str, start_date: str, end_date: str) -> str:
        req_url = f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}'\
            f'&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min'\
            f',temperature_2m_mean,rain_sum,snowfall_sum,windspeed_10m_max,shortwave_radiation_sum&timezone=GMT'

        return req_url

    def _get_data_from_api(self, req_url: str) -> None:
        print('api_call')
        req = requests.get(url=req_url)
        self.data_collection = req.json()

    def _get_data_from_json(self, filepath: str | pathlib.Path) -> None:
        if isinstance(filepath, str):
            filepath = pathlib.Path(filepath)
        with open(filepath, 'r') as ifile:
            self.data_collection = json.load(ifile)

    def _save_data_to_json(self, filepath: str | pathlib.Path) -> None:
        if isinstance(filepath, str):
            filepath = pathlib.Path(filepath)
        with open (filepath, 'w') as ofile:
            json.dump(self.data_collection, ofile)

    def _generate_outfile_name(self, coordlist: list | tuple, cityname: str = None) -> pathlib.Path:
        if cityname is None:
            coordlist = [item.replace('.','-') for item in coordlist]
            filename = ('json_data/Weather_data' + '_' + '_'.join(coordlist) + '.json')
        else:
            filename = ('json_data/Weather_data_' + cityname + '.json')

        return pathlib.Path(filename)

    def _data_collection_to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.data_collection['daily'])

    def _transform_daily_to_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        df_resamp = df.set_index('time')
        df_resamp.index = pd.to_datetime(df_resamp.index)

        return df_resamp.resample('1M').mean()

    def _decompose_timeseries(self, key: str, period: int = 12) -> 'DecomposeResult':
        print(f'Calculating time series for {key} with period={period}')
        series = self.df_monthly[key]
        result = seasonal_decompose(series, model='additive', period=period)

        return result

####################
#public wrappers
####################

    def extract_all_time_series_components(self):
        self.time_series_components = {}
        components = ('observed', 'seasonal', 'trend', 'resid')
        self.time_series_components = dict_of_dfs = {comp: pd.DataFrame() for comp in components}

        for key, ts in self.time_series_analyses.items():
            #self.time_series_components[key] = {}
            for comp in components:
                #self.time_series_components[key][comp] = getattr(ts, comp)
                self.time_series_components[comp][key] = getattr(ts, comp)

    def set_data_collection(self, ini: str | pathlib.Path | list | tuple, name: str = None):
        if isinstance(ini, list) or isinstance(ini, tuple):
            if len(ini) == 4:
                req_url = self._generate_api_url(*ini)
                self._get_data_from_api(req_url)

                fileout = self._generate_outfile_name(ini, cityname=name)
                self._save_data_to_json(fileout)

        elif isinstance(ini, str) or isinstance(ini, pathlib.Path):
            self._get_data_from_json(ini)

        else:
            self.data_collection = {}

        if 'reason' in self.data_collection.keys(): print(self.data_collection['reason'])
        #else: print(self.data_collection.keys())
        if 'daily' in self.data_collection.keys():
            #self.data_collection['df_all'] = self._data_collection_to_dataframe()
            self.df_all = self._data_collection_to_dataframe()
            self.df_all.dropna(inplace=True)

            self.df_monthly = self._transform_daily_to_monthly(self.df_all)

    def calculate_all_time_series(self, period: int = 60):
        for colname in self.df_monthly.columns:
            time_series = self._decompose_timeseries(colname, period=period)
            self.time_series_analyses[colname] = time_series
