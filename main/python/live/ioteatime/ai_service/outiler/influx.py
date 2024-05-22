import configparser as parser
from datetime import datetime, timedelta

from influxdb_client import InfluxDBClient

properties = parser.ConfigParser()
properties.read('./config.ini')

url = properties['INFLUX']['url']
token = properties['INFLUX']['token']
org = properties['INFLUX']['org']
bucket = properties['INFLUX']['bucket']

client = InfluxDBClient(url=url, token=token, org=org)
query = f'from(bucket: "{org}") |> range(start: 0) |> limit(n:1)'
result = client.query_api().query(org=org, query=query)

start_time = result[0].records[0].get_time().date().isoformat() + 'T00:00:00Z'
midnight = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0) - timedelta(days = 1)
end_time = midnight.isoformat() + 'Z'
