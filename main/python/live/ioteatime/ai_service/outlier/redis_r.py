import configparser as parser
import json

import redis

properties = parser.ConfigParser()
properties.read('./config.ini')

host = properties['REDIS']['host']
port = properties['REDIS']['port']
password = properties['REDIS']['password']
db = properties['REDIS']['db']

r = redis.Redis(host=host, port=port, password=password, db=db)

def set(name, dict):
    r.set(name, json.dumps(dict), ex=60*60*24)
