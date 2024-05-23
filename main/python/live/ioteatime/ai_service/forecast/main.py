import configparser as parser

import pandas as pd

from . import electricity
from . import influx
from . import sql
from . import train

properties = parser.ConfigParser()
properties.read('./config.ini')

hourly_backup = properties['TABLE']['hourly_backup']
hourly_predict = properties['TABLE']['hourly_predict']
daily_backup = properties['TABLE']['daily_backup']
daily_predict = properties['TABLE']['daily_predict']

def backup():
    df_init = pd.DataFrame(columns=['organization_id', 'channel_id', 'time', 'kwh'])

    sql.backup(hourly_predict, hourly_backup)
    sql.insert(df_init, hourly_predict)

    sql.backup(daily_predict, daily_backup)
    sql.insert(df_init, daily_predict)

def run(param_grid):
    df_org = influx.df_org()
    for i in range (0, len(df_org)):
        usage_forecast(param_grid, df_org.loc[i])


def usage_forecast(param_grid, org):
    organization_id = org.organization_id
    channels = electricity.find_channels(organization_id)

    for channel in channels:
        for idx in range(0, len(channel)):
            if channel.channel.loc[idx] == 'main':
                query = electricity.query_kwh_all(org, '1h')
            else:
                query = electricity.query_kwh(org, '1h', channel.place.loc[idx], channel.channel.loc[idx])

            df_usage = electricity.get_kwh(org, query)
            if (df_usage.empty):
                continue

            df_usage = electricity.format_w(df_usage)

            outlier_value = electricity.find_outlier(df_usage, 'y')
            df_train = electricity.set_outlier(df_usage, outlier_value)

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
