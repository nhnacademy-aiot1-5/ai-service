from influxdb_client import InfluxDBClient
from datetime import datetime
import configparser as parser

properties = parser.ConfigParser()
properties.read('../config.ini')

url = properties['INFLUX']['url']
token = properties['INFLUX']['token']
org = properties['INFLUX']['org']
bucket = properties['INFLUX']['bucket']

client = InfluxDBClient(url=url, token=token, org=org)

query = f'from(bucket: "{bucket}") |> range(start: 0) |> limit(n:1)'
result = client.query_api().query(org=org, query=query)

earliest_time = result[0].records[0].get_time().date()
start_time = earliest_time.isoformat() + 'T00:00:00Z'

yesterday_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
end_time = yesterday_midnight.isoformat() + 'Z'