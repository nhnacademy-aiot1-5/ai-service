from sqlalchemy import create_engine
import pandas as pd
import pymysql

database_user = 'nhn_academy_21'
database_password = '*L]RAMG*8NYJnCKK'
host_address = '133.186.244.96'
database_name = 'nhn_academy_21'

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

def backup(from_t, to_t):
    query_str = f"select * from {from_t}"
    df_backup = query(query_str)
    insert(df_backup, to_t)
