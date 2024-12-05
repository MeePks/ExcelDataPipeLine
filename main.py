import pandas as pd
import read_excel_file as ref
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from configparser import ConfigParser

config=ConfigParser()
config.read('config.ini')

server=config['sql']['server']
database=config['sql']['database']
table=config['sql']['table']

def sql_connection(server,database):
    try:
        connection_string = f'mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
        engine=create_engine(connection_string)
        print(f'Conneted to : {server}')
        return engine
    except:
        print(f"Error Connecting to the {server}: {database}")

engine=sql_connection(server,database)
#EU_table,NA_table=ref.read_tables_from_excel()
EU_table=ref.read_tables_from_excel()
EU_table.to_sql(table,engine,schema='dbo',if_exists='replace',index=False)
#NA_table.to_sql(table,engine,schema='dbo',if_exists='append',index=False)


    


