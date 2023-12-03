#import pandas as pd
#import matplotlib.pyplot as plt

from analyse_weatherdata.class_weather_dashboard import WeatherDashboard
#from analyse_weatherdata.class_weather_data import WeatherData
#from analyse_weatherdata.class_weather_collection import WeatherCollection
#from data_management.class_sarima_analyser import WeatherSarimaAnalyser

#if __name__ == '__main__':
weather_dashboard = WeatherDashboard()
weather_dashboard.template.servable()

    # wd = WeatherData('data_management/json_data/Weather_data_Hargeisa_Somaliland.json')
    # wd.calculate_all_time_series()
    #
    # wc = WeatherCollection()
    # wc.append_data('data_management/json_data/Weather_data_Hargeisa_Somaliland.json')
    # wc.calc_raw_average()
    #
    # wsa = WeatherSarimaAnalyser(wc.avg_raw)
    # wsa.load_best_sarima_config(f'data_management/best_models/best_sarima_models.json')
    #
    # model_fit, y_pred, y_forec = wsa.sarima_forecast(wc.avg_raw['temperature_2m_mean'],wsa.best_configs['temperature_2m_mean'])
    # best_pd_fc = pd.concat([y_pred, y_forec])
    # best_dec = wd.decompose_timeseries(best_pd_fc, period=60)
    #
    # plt.plot(wd.time_series_analyses['temperature_2m_mean'].trend)
    # plt.plot(best_dec.trend)
    # plt.show()

    #wd = WeatherData(['20.0', '10.0', '1950-01-01', '2023-09-01'])
