import pandas as pd
import math
from . import influx

def get(window_period, type, phase, description, fn):
    query = f'from(bucket: "{influx.bucket}") \
          |> range(start: {influx.start_time}, stop: {influx.end_time}) \
          |> filter(fn: (r) => r["type"] == "{type}")\
          |> filter(fn: (r) => r["phase"] == "{phase}")\
          |> filter(fn: (r) => r["description"] == "{description}")\
          |> aggregateWindow(every: {window_period}, fn: {fn}, createEmpty: false)\
          |> group(columns: ["_time"]) \
          |> sum()\
          |> group(mode: "by")'

    result = influx.client.query_api().query(org=influx.org, query=query)

    json_data = [{"time": record.get_time(), "value": record.get_value()} for record in result[0]]
    df_json = pd.DataFrame(json_data)

    df = pd.DataFrame()
    df['ds'] = pd.to_datetime(df_json['time']).dt.tz_localize(None)
    df['y'] = pd.to_numeric(df_json['value'])

    return df

# 전력 사용량
def get_hourly_usage():
    df = get('1h', 'main', 'kwh', 'sum', 'last')
    df_usage = pd.DataFrame(columns=['ds', 'y'])

    k = 0

    for i in range(0, df.shape[0]-1):
        if df.ds[i+1] - df.ds[i] != pd.Timedelta(hours=1):
            pass
        else:
            hour_value = math.floor(df.y[i+1] - df.y[i] * 10) / 10
            df_usage.loc[k] = [df.ds[i], hour_value]
            k = k + 1

    return df_usage

# 시간별 w 평균
def get_hourly_electricity():
    return get('1h', 'main', 'total', 'w', 'mean')