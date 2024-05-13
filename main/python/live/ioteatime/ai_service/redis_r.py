import redis
import pandas as pd
import configparser as parser

properties = parser.ConfigParser()
properties.read('./config.ini')

host = properties['REDIS']['host']
port = properties['REDIS']['port']
password = properties['REDIS']['password']
db = properties['REDIS']['db']

r = redis.Redis(host=host, port=port, password=password, db=db)

def set(name, df):
    r.set(name, df.to_json())

def get_df(name):
    result = get(name)

    return pd.read_json(result.decode())

def get(name):
    return r.get(name)