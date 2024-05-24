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
    backup()
    channel_forecast(param_grid)
    all_forecast(hourly_predict)
    all_forecast(daily_predict)

def channel_forecast(param_grid):
    df_org = influx.df_org()
    for i in range (0, len(df_org)):
        org = df_org.loc[i]
        channels = electricity.find_channels(org.organization_id)
        for channel in channels:
            for i in range(0, len(channel)):
                channel_id = channel.id.loc[i]
                place = channel.place.loc[i]
                channel_name = channel.channel.loc[i]

                query = electricity.get_query(org, '1h', place, channel_name)

                train.forecast(param_grid, org, query, channel_name, channel_id)


def all_forecast(table):
    query = f'SELECT d.organization_id, -1 as channel_id, d.time, SUM(d.kwh) as kwh \
             FROM `{table}` AS d \
             INNER JOIN `channels` AS c \
             ON d.channel_id = c.channel_id \
             WHERE c.channel_name = \'main\' \
             GROUP BY d.organization_id, d.time'

    result = sql.query(query)
    sql.append(result, table)

