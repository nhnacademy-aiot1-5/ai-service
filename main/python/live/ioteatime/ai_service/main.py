from . import sql
from . import redis_r as redis
from . import train
from . import outlier
from . import electricity
import configparser as parser

properties = parser.ConfigParser()
properties.read('./config.ini')

def set_outlier():
    df = electricity.get_hourly_electricity('main')
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

    df_train = electricity.get_total_hourly_usage('main')
    outlier_value = outlier.find_outlier(df_train, 'y')
    df_train = outlier.set_outlier(df_train, outlier_value)

    model = train.run(df_train, param_grid)

    df_forecast_d = train.daily_forecast(model, 24*30, '1h', outlier_value)
    sql.insert(df_forecast_d, daily_predict)

    df_forecast_h = train.forecast(model, 24*3, '1h', outlier_value)
    sql.insert(df_forecast_h, hourly_predict)

def channel_forecast(param_grid):
    daily_predict = properties['TABLE']['daily_backup']
    channels = electricity.find_channels()

    for channel in channels:
        print(channel)
        for idx in range(0, len(channel)):
            query = electricity.query('1h', channel.place.loc[idx], channel.channel.loc[idx], 'kwh', 'sum', 'last')

            df_train = electricity.get(query)
            df_train = electricity.get_channel_hourly_usage(df_train)

            outlier_value = outlier.find_outlier(df_train, 'y')
            df_train = outlier.set_outlier(df_train, outlier_value)

            if (df_train.y.loc[0] == df_train.y.loc[len(df_train)-1]):
                df_forecast = train.linear(df_train.y.loc[0])
                sql.insert(df_forecast, daily_predict)
                continue

            model = train.run(df_train, param_grid)

            df_forecast = train.daily_forecast(model, 24*30, '1h', outlier_value)
            sql.insert(df_forecast, daily_predict)