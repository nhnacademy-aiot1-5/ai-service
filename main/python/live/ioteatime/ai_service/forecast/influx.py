import configparser as parser
from datetime import datetime, timedelta

import pandas as pd
from influxdb_client import InfluxDBClient

from . import sql

properties = parser.ConfigParser()
properties.read('./config.ini')

url = properties['INFLUX']['url']
token = properties['INFLUX']['token']

def df_org():
    df_org = sql.query(f'select * from organizations')
    df = pd.DataFrame(columns=['organization_id', 'organization_name', 'client', 'start_time', 'end_time'])

    for i in (0, len(df)):
        org = df_org.loc[i, 'name']
        df.loc[i, 'organization_id'] = df_org.loc[i, 'organization_id']
        df.loc[i, 'organization_name'] = org

        client = InfluxDBClient(url=url, token=token, org=org)
        df.loc[i, 'client'] = client

        query = f'from(bucket: "{org}") |> range(start: 0) |> limit(n:1)'
        result = client.query_api().query(org=org, query=query)

        earliest_time = result[0].records[0].get_time().date()
        df.loc[i, 'start_time'] = earliest_time.isoformat() + 'T00:00:00Z'

        yesterday_midnight = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0) - timedelta(days = 1)
        df.loc[i, 'end_time'] = yesterday_midnight.isoformat() + 'Z'
    return df
