import pandas as pd

from . import sql
from . import redis_r as redis
from . import train
from . import outlier
from . import electricity
from . import influx
import configparser as parser

properties = parser.ConfigParser()
properties.read('./config.ini')

hourly_predict = properties['TABLE']['hourly_predict']
hourly_backup = properties['TABLE']['hourly_backup']
daily_backup = properties['TABLE']['daily_backup']
daily_predict = properties['TABLE']['daily_predict']
outlier_table = properties['TABLE']['outlier']

def set_outlier():
    df_org = influx.df_org()
    for i in range (0, len(df_org)):
        df = electricity.get_hourly_electricity(df_org.loc[i], '1h')
        df_hourly_outlier = outlier.find_hourly_outlier(df)
        df_hourly_outlier['organization_id'] = df_org['organization_id'][i]
        redis.set(outlier_table, df_hourly_outlier)

def backup():
    df_init = pd.DataFrame(columns=['organization_id', 'channel_id', 'time', 'kwh'])

    sql.backup(hourly_predict, hourly_backup)
    sql.insert(df_init, hourly_predict)

    sql.backup(daily_predict, daily_backup)
    sql.insert(df_init, daily_predict)

def forecast(param_grid):
    df_org = influx.df_org()
    for i in range (0, len(df_org)):
        usage_forecast(param_grid, df_org.loc[i])


def usage_forecast(param_grid, org):
    organization_id = org.organization_id
    channels = electricity.find_channels(organization_id)

    for channel in channels:
        for idx in range(0, len(channel)):
            if channel.channel.loc[idx] == 'main':
                result = electricity.query_all(org, '1h', 'kwh', 'sum', 'last')
            else:
                result = electricity.query(org, '1h', channel.place.loc[idx], channel.channel.loc[idx], 'kwh', 'sum', 'last')

            df_usage = electricity.format(result)
            df_usage = electricity.get_usage(df_usage)

            outlier_value = outlier.find_outlier(df_usage, 'y')
            df_train = outlier.set_outlier(df_usage, outlier_value)

            if (df_train.y.loc[0] == df_train.y.loc[len(df_train)-1]):
                df_forecast = train.constant(df_train.y.loc[0])
                df_forecast['organization_id'] = organization_id
                df_forecast['channel_id'] = channel.id.loc[idx]
                sql.append(df_forecast, daily_predict)
                continue

            model = train.run(org, df_train, param_grid)

            df_daily_forecast = train.daily_forecast(model, 24*30, '1h', outlier_value)
            df_daily_forecast['organization_id'] = organization_id
            if (channel.channel.loc[idx] == 'main'):
                df_daily_forecast['channel_id'] = -1
            else:
                df_daily_forecast['channel_id'] = channel.id.loc[idx]
            sql.append(df_daily_forecast, daily_predict)

            df_hourly_forecast = train.hourly_forecast(model, 24*3, '1h', outlier_value)
            df_hourly_forecast['organization_id'] = organization_id
            if (channel.channel.loc[idx] == 'main'):
                df_hourly_forecast['channel_id'] = -1
            else:
                df_hourly_forecast['channel_id'] = channel.id.loc[idx]
            sql.append(df_hourly_forecast, hourly_predict)