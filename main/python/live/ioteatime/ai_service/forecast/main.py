import configparser as parser
import datetime
import logging

import numpy as np
import pandas as pd

from . import electricity
from . import influx
from . import sql
from . import train

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('ioteatime.log')
log.addHandler(handler)

properties = parser.ConfigParser()
properties.read('./config.ini')

hourly_backup = properties['TABLE']['hourly_backup']
hourly_predict = properties['TABLE']['hourly_predict']
daily_backup = properties['TABLE']['daily_backup']
daily_predict = properties['TABLE']['daily_predict']

def backup():
    df_init = pd.DataFrame(columns=['organization_id', 'channel_id', 'time', 'kwh', 'bill'])
    df_init = df_init.astype({
        'organization_id': np.int32,
        'channel_id': np.int32,
        'time': 'datetime64[ns]',
        'kwh': np.float64,
        'bill': np.int64})

    sql.backup(hourly_predict, hourly_backup)
    sql.insert(df_init, hourly_predict)

    sql.backup(daily_predict, daily_backup)
    sql.insert(df_init, daily_predict)

def run(param_grid):
    log.info("테이블 초기화 시작" + str(datetime.datetime.now()))
    backup()
    log.info("테이블 초기화 완료" + str(datetime.datetime.now()))
    log.info("채널별 예측 시작" + str(datetime.datetime.now()))
    channel_forecast(param_grid)
    log.info("채널별 예측 완료" + str(datetime.datetime.now()))
    log.info("총 전력량 예측 시작(시간별)" + str(datetime.datetime.now()))
    all_forecast(hourly_predict)
    log.info("총 전력량 예측 완료(시간별)" + str(datetime.datetime.now()))
    log.info("총 전력량 예측 시작(일별)" + str(datetime.datetime.now()))
    all_forecast(daily_predict)
    log.info("총 전력량 예측 완료(일별)" + str(datetime.datetime.now()))

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

                if (channel_id < 0) : continue

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
    result.kwh = result.kwh.round(2)

    sql.append(result, table)

