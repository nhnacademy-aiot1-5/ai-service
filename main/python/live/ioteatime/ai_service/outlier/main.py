import configparser as parser
from datetime import datetime
import logging
import pandas as pd

from . import influx
from . import redis_r as redis
from . import sql

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('ioteatime.log')
log.addHandler(handler)

properties = parser.ConfigParser()
properties.read('./config.ini')

outlier_table = properties['TABLE']['outlier']

def run(id):
    df_places = sql.query(f'select place_name from places where organization_id={id}')
    log.info("outlier 계산 시작")
    outliers = find_outliers(df_places)
    log.info("outlier 계산 완료")

    log.info("redis 저장중")
    redis.set("outliers", outliers)
    log.info("redis 저장 완료")

def find_outliers(df_places):
    outliers = []

    for i in range(0, len(df_places)):
        place = df_places.place_name[i]

        if place == 'total' : continue

        df = get_hourly_electricity(get_query('5m', place))
        if df is None or len(df) == 0: continue
        values = find_values(df)

        outlier = {
            "place" : place,
            "values": values
        }

        outliers.append(outlier)

    return outliers

def find_values(df):
    values = []

    if datetime.now().weekday() < 6 : df_weekday = df[(pd.DatetimeIndex(df.ds).weekday < 5)]
    else : df_weekday = df[(pd.DatetimeIndex(df.ds).weekday > 4)]

    for i in range(0, 24):
        df_hourly = df_weekday[(pd.DatetimeIndex(df_weekday.ds).hour == i)]
        value = find_outlier(df_hourly, 'y')

        value = {
            'id' : i,
            'min': round(value[0], 2),
            'max': round(value[1], 2),
            'updated_at': str(datetime.now().date())
        }

        values.append(value)

    return values

def get_query(window_period, place):
    return f'from(bucket: "{influx.bucket}") \
          |> range(start: {influx.start_time}, stop: {influx.end_time}) \
          |> filter(fn: (r) => r["place"] == "{place}")\
          |> filter(fn: (r) => r["type"] == "main")\
          |> filter(fn: (r) => r["phase"] == "total")\
          |> filter(fn: (r) => r["description"] == "w")\
          |> aggregateWindow(every: {window_period}, fn: mean, createEmpty: false)'

def get_hourly_electricity(query):
    result = influx.client.query_api().query(org=influx.org, query=query)

    if result is None or len(result) == 0:
        return pd.DataFrame(columns=['ds', 'y'])

    json_data = [{"time": record.get_time(), "value": record.get_value()} for record in result[0]]
    df_json = pd.DataFrame(json_data)

    df = pd.DataFrame()
    df['ds'] = pd.to_datetime(df_json['time']).dt.tz_localize(None) + pd.Timedelta(hours = 8)
    df['y'] = pd.to_numeric(df_json['value'])

    return df

def find_outlier(df, idx):
    df = df.sort_values(by=idx)

    q1 = df.iloc[int(len(df)*(1/4))][idx]
    q3 = df.iloc[int(len(df)*(3/4))][idx]

    iqr = q3-q1

    min = q1-1.5*iqr
    max = q3+1.5*iqr

    if min < 0 : min = 0
    if max < 0 : max = 0

    return min, max
