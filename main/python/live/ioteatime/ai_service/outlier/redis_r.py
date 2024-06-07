import configparser as parser
import json
import logging

import redis

properties = parser.ConfigParser()
properties.read('./config.ini')

host = properties['REDIS']['host']
port = properties['REDIS']['port']
db = properties['REDIS']['db']

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('ioteatime.log')
log.addHandler(handler)

r = redis.Redis(host=host, port=port, db=db)

def set(name, dict_value):
    try:
        r.set(name, json.dumps(dict_value), ex=60 * 60 * 24)
    except TypeError:
        log.warning(f"Failed to serialize {dict_value} to JSON.")
    except redis.ConnectionError:
        log.warning("Failed to connect to Redis.")
