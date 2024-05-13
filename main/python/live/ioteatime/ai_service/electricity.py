import pandas as pd
from . import influx
from . import sql

def query_all(window_period, phase, description, fn):
    return f'from(bucket: "{influx.bucket}") \
          |> range(start: {influx.start_time}, stop: {influx.end_time}) \
          |> filter(fn: (r) => r["type"] == "main")\
          |> filter(fn: (r) => r["phase"] == "{phase}")\
          |> filter(fn: (r) => r["description"] == "{description}")\
          |> aggregateWindow(every: {window_period}, fn: {fn}, createEmpty: false)\
          |> group(columns: ["_time"]) \
          |> sum()\
          |> group(mode: "by")'

def query(window_period, place, type, phase, description, fn):
    return f'from(bucket: "{influx.bucket}") \
          |> range(start: {influx.start_time}, stop: {influx.end_time}) \
          |> filter(fn: (r) => r["place"] == "{place}")\
          |> filter(fn: (r) => r["type"] == "{type}")\
          |> filter(fn: (r) => r["phase"] == "{phase}")\
          |> filter(fn: (r) => r["description"] == "{description}")\
          |> aggregateWindow(every: {window_period}, fn: {fn}, createEmpty: false)'

def get(query):
    result = influx.client.query_api().query(org=influx.org, query=query)

    json_data = [{"time": record.get_time(), "value": record.get_value()} for record in result[0]]
    df_json = pd.DataFrame(json_data)

    df = pd.DataFrame()
    df['ds'] = pd.to_datetime(df_json['time']).dt.tz_localize(None) + pd.Timedelta(hours = 8)
    df['y'] = pd.to_numeric(df_json['value'])

    return df

def find_channels():
    channels = []
    organization_id = sql.query(f'select organization_id from organizations where name="nhnacademy"').organization_id.loc[0]
    df_sensors = sql.query(f'select sensor_id from modbus_sensors where organization_id={organization_id}')
    df_places = sql.query(f'select place_id, place_name from places where organization_id={organization_id}')

    for i in range(len(df_sensors)):
        df_channel = sql.query(f"select channel_id, place_id, channel_name from channels where sensor_id={df_sensors.sensor_id.loc[i]}")

        for i in range(0, len(df_places)):
            df_channel = df_channel.replace({'place_id':df_places.place_id.loc[i]}, df_places.place_name.loc[i])

        df_channel.columns = ['id', 'place', 'channel']
        channels.insert(i,df_channel)

    return channels

# 전력 사용량
def get_usage(df):
    df_usage = pd.DataFrame(columns=['ds', 'y'])

    k=0
    for i in range(0, df.shape[0]-1):
        if df.ds[i+1] - df.ds[i] != pd.Timedelta(hours=1):
            pass
        else:
            df_usage.loc[k] = [df.ds[i], df.y[i+1] - df.y[i]]
            k=k+1

    return df_usage

# 시간별 w 평균
def get_hourly_electricity(window_period):
    query = query_all(window_period, 'total', 'w', 'mean')

    return get(query)