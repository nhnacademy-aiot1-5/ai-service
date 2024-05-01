import redis
import pandas as pd

host = '133.186.244.96'
port=6379
password="*N2vya7H@muDTwdNMR!"
db = 40

r = redis.Redis(host=host, port=port, password=password, db=db)

def set(name, df):
    r.set(name, df.to_json())

def get_df(name):
    result = get(name)
    return pd.read_json(result.decode())

def get(name):
    return r.get(name)