import configparser as parser

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine

properties = parser.ConfigParser()
properties.read('./config.ini')

database_user = properties['SQL']['database_user']
database_password = properties['SQL']['database_password']
host_address = properties['SQL']['host_address']
database_name = properties['SQL']['database_name']

db_connection_url = f'mysql+pymysql://{database_user}:{database_password}@{host_address}/{database_name}'
engine = create_engine(db_connection_url)

def query(query):
    result = pd.read_sql(query, con=engine)

    return result

def insert(df, table):
    with engine.connect() as con:
        df.to_sql(
            name = table,
            con = con,
            if_exists = 'replace',
            index=False
        )

def append(df, table):
    with engine.connect() as con:
        df.to_sql(
            name = table,
            con = con,
            if_exists = 'append',
            index=False
        )

def backup(from_t, to_t):
    try:
        query_str = f"select * from {from_t}"
        df_backup = query(query_str)
        insert(df_backup, to_t)
    except sqlalchemy.exc.ProgrammingError:
        pass
