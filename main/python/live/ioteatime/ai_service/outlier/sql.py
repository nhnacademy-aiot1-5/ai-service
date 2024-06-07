import configparser as parser

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

properties = parser.ConfigParser()
properties.read('./config.ini')

database_user = properties['SQL']['database_user']
database_password = properties['SQL']['database_password']
host_address = properties['SQL']['host_address']
database_name = properties['SQL']['database_name']

db_connection_url = f'mysql+pymysql://{database_user}:{database_password}@{host_address}/{database_name}'
engine = create_engine(db_connection_url)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def query(query):
    try:
        session = Session()
        result = pd.read_sql(query, con=session.bind).copy()
    finally:
        Session.remove()

    return result
