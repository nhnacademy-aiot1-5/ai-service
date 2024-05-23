import configparser as parser
import io

import pandas as pd
import redis

properties = parser.ConfigParser()
properties.read('./config.ini')

host = properties['REDIS']['host']
port = properties['REDIS']['port']
password = properties['REDIS']['password']
db = properties['REDIS']['db']

r = redis.Redis(host=host, port=port, password=password, db=db)

def set(name, df):
    r.set(name, df.to_json())

def hset(key, field, value):
    r.hset(key, field, value)

def get_df(name):
    result = get(name)
    if result is None:
        return pd.DataFrame()

    return pd.read_json(io.StringIO(result.decode()))

def get(name):
    return r.get(name)
