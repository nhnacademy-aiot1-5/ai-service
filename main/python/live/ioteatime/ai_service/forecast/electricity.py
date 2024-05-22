import pandas as pd

from . import sql


def find_channels(id):
    channels = []
    df_sensors = sql.query(f'select sensor_id from modbus_sensors where organization_id={id}')
    df_places = sql.query(f'select place_id, place_name from places where organization_id={id}')

    for i in range(len(df_sensors)):
        df_channel = sql.query(f"select channel_id, place_id, channel_name from channels where sensor_id={df_sensors.sensor_id.loc[i]}")

        for i in range(0, len(df_places)):
            df_channel = df_channel.replace({'place_id':df_places.place_id.loc[i]}, df_places.place_name.loc[i])

        df_channel.columns = ['id', 'place', 'channel']
        channels.insert(i,df_channel)

    return channels

def query_kwh_all(org, window_period):
    query = f'from(bucket: "{org.organization_name}") \
          |> range(start: {org.start_time}, stop: {org.end_time}) \
          |> filter(fn: (r) => r["type"] == "main")\
          |> filter(fn: (r) => r["phase"] == "kwh")\
          |> filter(fn: (r) => r["description"] == "sum")\
          |> aggregateWindow(every: {window_period}, fn: last, createEmpty: false)\
          |> group(columns: ["_time"]) \
          |> sum()\
          |> group(mode: "by")'

    return query

def query_kwh(org, window_period, place, type):
    query = f'from(bucket: "{org.organization_name}") \
          |> range(start: {org.start_time}, stop: {org.end_time}) \
          |> filter(fn: (r) => r["place"] == "{place}")\
          |> filter(fn: (r) => r["type"] == "{type}")\
          |> filter(fn: (r) => r["phase"] == "kwh")\
          |> filter(fn: (r) => r["description"] == "sum")\
          |> aggregateWindow(every: {window_period}, fn: last, createEmpty: false)'

    return query

def get_kwh(org, query):
    result = org.client.query_api().query(org=org.organization_name, query=query)
    json_data = [{"time": record.get_time(), "value": record.get_value()} for record in result[0]]
    df_json = pd.DataFrame(json_data)

    df = pd.DataFrame()
    df['ds'] = pd.to_datetime(df_json['time']).dt.tz_localize(None) + pd.Timedelta(hours = 8)
    df['y'] = pd.to_numeric(df_json['value'])
    return df



# 전력 사용량
def format_w(df):
    df_usage = pd.DataFrame(columns=['ds', 'y'])

    k=0
    for i in range(0, df.shape[0]-1):
        if df.ds[i+1] - df.ds[i] != pd.Timedelta(hours=1):
            pass
        else:
            df_usage.loc[k] = [df.ds[i], df.y[i+1] - df.y[i]]
            k=k+1

    return df_usage

def find_outlier(df, idx):
    df = df.sort_values(by=idx)

    q1 = df.iloc[int(len(df)*(1/4))-1][idx]
    q3 = df.iloc[int(len(df)*(3/4))-1][idx]
    iqr = q3-q1
    min = q1-1.5*iqr
    max = q3+1.5*iqr

    return min, max

def set_outlier(df, value):
    floor = round(value[0],2)
    cap = round(value[1],2)

    if (floor == cap):
        cap += 0.1

    df['floor'] = floor
    df['cap'] = cap

    return df
