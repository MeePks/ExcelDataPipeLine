import pandas as pd
import read_excel_file as ref
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from configparser import ConfigParser
import matplotlib.pyplot as plt

config=ConfigParser()
config.read('config.ini')

server=config['sql']['server']
database='test'

def sql_connection(server,database):
    try:
        connection_string = f'mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
        engine=create_engine(connection_string)
        print(f'Conneted to : {server}')
        return engine
    except:
        print(f"Error Connecting to the {server}: {database}")


# Convert to DataFrame
engine=sql_connection(server,database)
query='''
select b.TableName,IndexName,IL.NoOfRecords LogRecordCount,b.RowCounts TableRecordCount,IL.NoOfRecords - b.RowCounts Diff
from  (SELECT
  t.Name                                       AS TableName,
  Max(i.Name)									   AS IndexName,
  p.Rows                                       AS RowCounts,
  SUM(a.total_pages) * 8                       AS TotalSpaceKB,
  SUM(a.used_pages) * 8                        AS UsedSpaceKB,
  (SUM(a.total_pages) - SUM(a.used_pages)) * 8 AS UnusedSpaceKB --select 'Drop table dbo.' +t.name
FROM
  sys.tables t
  INNER JOIN sys.indexes i ON t.object_id = i.object_id
  INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
  INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
    LEFT OUTER JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE
  t.Name NOT LIKE 'dt%'
  AND t.is_ms_shipped = 0
  AND i.object_id > 255
  AND t.name like '%NA%'
GROUP BY
  t.Name, s.Name, p.Rows

) b 
left join amazon..__InventoryLogs IL
on IL.FileName=b.TableName
order by b.TableName
'''
df = pd.read_sql_query(query,engine)


# Plotting the data
fig, ax = plt.subplots(figsize=(10, 6))

# Bar width
bar_width = 0.35

# X-axis locations for groups
r1 = range(len(df))
r2 = [x + bar_width for x in r1]

# Create bars with vibrant colors
bars1 = ax.bar(r1, df['LogRecordCount'], color='#1f77b4', width=bar_width, edgecolor='grey', label='LogRecordCount')
bars2 = ax.bar(r2, df['TableRecordCount'], color='#ff7f0e', width=bar_width, edgecolor='grey', label='TableRecordCount')

# Adding labels
ax.set_xlabel('TableName', fontweight='bold')
ax.set_ylabel('Record Count', fontweight='bold')
ax.set_title('Comparison of LogRecordCount vs. TableRecordCount', fontweight='bold', fontsize=14)
ax.set_xticks([r + bar_width/2 for r in range(len(df))])
ax.set_xticklabels(df['TableName'], rotation=45, ha='right', fontsize=10)

# Adding legend
ax.legend()

# Adding data labels to bars
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:,}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, color='black')

add_labels(bars1)
add_labels(bars2)

# Adjust layout for better fit
plt.tight_layout()

# Show the plot
plt.show()
