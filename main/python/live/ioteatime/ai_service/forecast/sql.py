import configparser as parser

import pandas as pd
import sqlalchemy
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
        result = pd.read_sql(query, con=session).copy()
    finally:
        Session.remove()

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

def save(df, table, organization_id, channel_id):
    df['organization_id'] = organization_id
    df['channel_id'] = channel_id
    append(df, table)

def backup(from_t, to_t):
    try:
        query_str = f"select * from {from_t}"
        df_backup = query(query_str)
        insert(df_backup, to_t)
    except sqlalchemy.exc.ProgrammingError:
        pass
