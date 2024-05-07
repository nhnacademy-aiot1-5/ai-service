from . import sql
from . import redis_r as redis
from . import train
from . import outlier
from . import electricity
import configparser as parser

properties = parser.ConfigParser()
properties.read('./config.ini')

def set_outlier():
    df = electricity.get_hourly_electricity()
    df_hourly_outlier = outlier.find_hourly_outlier(df)

    outlier_table = properties['TABLE']['outlier']
    redis.set(outlier_table, df_hourly_outlier)

def forecast(param_grid):
    hourly_predict = properties['TABLE']['hourly_predict']
    hourly_backup = properties['TABLE']['hourly_backup']
    sql.backup(hourly_predict, hourly_backup)

    daily_backup = properties['TABLE']['daily_predict']
    daily_predict = properties['TABLE']['daily_backup']
    sql.backup(daily_predict, daily_backup)

    df_train = electricity.get_hourly_usage()
    df_train = outlier.set_outlier(df_train)

    model = train.run(df_train, param_grid)

    df_forecast_d = train.daily_forecast(model, 24*30, '1h')
    sql.insert(df_forecast_d, daily_predict)

    df_forecast_h = train.forecast(model, 24*3, '1h')
    sql.insert(df_forecast_h, hourly_predict)
