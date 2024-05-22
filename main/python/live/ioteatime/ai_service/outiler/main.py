import configparser as parser
from datetime import datetime
import pandas as pd

from . import sql
from . import influx
from . import redis_r as redis

properties = parser.ConfigParser()
properties.read('./config.ini')

outlier_table = properties['TABLE']['outlier']

def run(id):
    df_places = sql.query(f'select place_name from places where organization_id={id}')

    for i in range(0, len(df_places)):
        df = get_hourly_electricity(get_query('1h', df_places.place_name[i]))
        df_hourly_outlier = find_hourly_outlier(df, df_places.place_name[i])
        redis.set(df_places.place_name[i], df_hourly_outlier)

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

    json_data = [{"time": record.get_time(), "value": record.get_value()} for record in result[0]]
    df_json = pd.DataFrame(json_data)

    df = pd.DataFrame()
    df['ds'] = pd.to_datetime(df_json['time']).dt.tz_localize(None) + pd.Timedelta(hours = 8)
    df['y'] = pd.to_numeric(df_json['value'])

    return df

def find_hourly_outlier(df, place):
    df_result = pd.DataFrame(columns=[place])

    for i in range(0, 24):
        df_hourly = df[(pd.DatetimeIndex(df.ds).hour == i)]
        value = find_outlier(df_hourly, 'y')

        data = {
            place: {
                'updated_at': str(datetime.now().date()),
                'min': round(value[0], 2),
                'max': round(value[1], 2),
            }
        }

        df_result.loc[i] = data

    return df_result

def find_outlier(df, idx):
    df = df.sort_values(by=idx)

    q1 = df.iloc[int(len(df)*(1/4))-1][idx]
    q3 = df.iloc[int(len(df)*(3/4))-1][idx]
    iqr = q3-q1
    min = q1-1.5*iqr
    max = q3+1.5*iqr

    return min, max
