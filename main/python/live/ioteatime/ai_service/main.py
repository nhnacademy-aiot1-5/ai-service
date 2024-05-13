from . import sql
from . import redis_r as redis
from . import train
from . import outlier
from . import electricity
import configparser as parser

properties = parser.ConfigParser()
properties.read('./config.ini')

hourly_predict = properties['TABLE']['hourly_predict']
hourly_backup = properties['TABLE']['hourly_backup']
daily_backup = properties['TABLE']['daily_predict']
daily_predict = properties['TABLE']['daily_backup']
outlier_table = properties['TABLE']['outlier']

def set_outlier():
    df = electricity.get_hourly_electricity('1h')
    df_hourly_outlier = outlier.find_hourly_outlier(df)

    redis.set(outlier_table, df_hourly_outlier)

def backup():
    sql.backup(hourly_predict, hourly_backup)
    sql.backup(daily_predict, daily_backup)

def total_usage_forecast(param_grid):
    query = electricity.query_all('1h', 'kwh', 'sum', 'last')
    df_usage = electricity.get(query)
    df_usage = electricity.get_usage(df_usage)

    outlier_value = outlier.find_outlier(df_usage, 'y')
    df_train = outlier.set_outlier(df_usage, outlier_value)

    model = train.run(df_train, param_grid)

    df_daily_forecast = train.daily_forecast(model, 24*30, '1h', outlier_value)
    df_daily_forecast['channel_id'] = -1
    sql.insert(df_daily_forecast, daily_predict)

    df_hourly_forecast = train.hourly_forecast(model, 24*3, '1h', outlier_value)
    df_hourly_forecast['channel_id'] = -1
    sql.insert(df_hourly_forecast, hourly_predict)

def channel_usage_forecast(param_grid):
    channels = electricity.find_channels()

    for channel in channels:
        for idx in range(0, len(channel)):
            query = electricity.query('1h', channel.place.loc[idx], channel.channel.loc[idx], 'kwh', 'sum', 'last')
            df_usage = electricity.get(query)
            df_usage = electricity.get_usage(df_usage)

            outlier_value = outlier.find_outlier(df_usage, 'y')
            df_train = outlier.set_outlier(df_usage, outlier_value)

            if (df_train.y.loc[0] == df_train.y.loc[len(df_train)-1]):
                df_forecast = train.linear(df_train.y.loc[0])
                df_forecast['channel_id'] = channel.id.loc[idx]
                sql.append(df_forecast, daily_predict)
                continue

            model = train.run(df_train, param_grid)

            df_forecast = train.daily_forecast(model, 24*30, '1h', outlier_value)
            df_forecast['channel_id'] = channel.id.loc[idx]
            sql.append(df_forecast, daily_predict)