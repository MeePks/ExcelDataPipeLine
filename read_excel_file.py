import pandas as pd
from configparser import ConfigParser

#Loading config file
config=ConfigParser()
config.read('config.ini')

#Excel config
path=config['excel']['path']
sheet=config['excel']['sheetname']
table_start_row=config.getint('excel','table_start_row')
table1_columns = list(map(int, config.get('excel', 'table1_columns').split(',')))
table2_columns = list(map(int, config.get('excel', 'table2_columns').split(',')))

def clean_column_name(column_name):
    parts = column_name.split(' ',)
    capitalized_parts = [part[0].upper()+part[1:] for part in parts]
    return ''.join(capitalized_parts)


def read_tables_from_excel():
    #read excel file and extract table
    excel_full_df=pd.read_excel(path,sheet_name=sheet,header=None)
    table_end_row=len(excel_full_df)-2   #determing end row by decrementing two from the dataframelength due to trend in data in excel 


    #extracting table1 i.e. EU data
    table1=excel_full_df.iloc[table_start_row:table_end_row,table1_columns]
    header_row = table1.iloc[0]
    table1.columns = header_row
    table1.columns = [clean_column_name(col) for col in table1.columns]
    table1 = table1[1:]

    #extracting table2 i.e. NA data
    table2=excel_full_df.iloc[table_start_row:table_end_row,table2_columns]
    header_row = table1.iloc[0]
    table2.columns = header_row
    table2 = table1[1:]

    return(table1,table2)

