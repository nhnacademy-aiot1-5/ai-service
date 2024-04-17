from flask import Flask
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta

from prophet import Prophet
import pandas as pd
import calendar

app = Flask(__name__)

url = "http://133.186.251.19:8086/"
token = "-IuLBpzhNRQ2JHqame4zACsJaXziyTsqQonaqTuOx9gdlQPYtMCSd1R0VuqikVrG9o6eR931y2eqyFPMWS2Mgw=="
org = "ioteatime"
bucket = "ioteatime"

client = InfluxDBClient(url=url, token=token, org=org)

from datetime import datetime, timedelta


def query_energy_data():
    window_period = '24h'

    query = f'from(bucket: "{bucket}") \
                    |> filter(fn: (r) => r["description"] == "w")\
                    |> filter(fn: (r) => r["phase"] == "total")\
                    |> aggregateWindow(every: {window_period}, fn: sum, createEmpty: true)\
                    |> yield(name: "_time")'

    start_day = client.query_api().query(org=org, query=query)

    yesterday_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days = 1)
    end_day = yesterday_midnight.isoformat() + 'Z'

    result = client.query_api().query(org=org, query=query)
    count = len(result)

    if count > 15:
        query = f'from(bucket: "{bucket}") \
                |> range(start: {start_day}, stop: {end_day}) \
                |> filter(fn: (r) => r["description"] == "w")\
                |> filter(fn: (r) => r["phase"] == "total")\
                |> filter(fn: (r) => r["description"] == "w")\
                |> aggregateWindow(every: {window_period}, fn: sum, createEmpty: true)\
                |> yield(name: "_value")'

        result = client.query_api().query(org=org, query=query)

        data = [{"time": record.get_time(), "value": record.get_value()} for record in result[0]]

        print("influx predict", result)

        return data

@app.route('/')
def calculate():
    json_data = query_energy_data()

    print("electricity data : ", json_data)

    df = pd.DataFrame(json_data)
    df['floor'] = 0
    df['ds'] = pd.to_datetime(df['time']).dt.tz_localize(None)
    df['y'] = pd.to_numeric(df['value'])

    model = Prophet()
    model.add_country_holidays(country_name='KR')
    model.fit(df)

    now = datetime().now()

    left_days = calendar.monthrange(now.year, now.month)[1] - now.day

    future = model.make_future_dataframe(periods=left_days, freq='24h')

    forecast = model.predict(future)
    forecast['ds'] = pd.to_datetime(forecast['ds'], origin='unix', unit='ms')

    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

    return json_data


if __name__ == '__main__':
    app.run()
