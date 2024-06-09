import sys
import time

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# Database with actions
path_db = r'../data/db_study/Log_data_with_token_shapes.db'
table_name = 'new_table'
column_name1 = 'participant_id'
column_name2 = 'trial'
filter_value1 = '31612'
filter_value2 = '0'

engine = create_engine(f"sqlite:///{path_db}")
query = f"SELECT * FROM {table_name} WHERE {column_name1} = {filter_value1} AND {column_name2} = {filter_value2}"
df_db = pd.read_sql_query(query, con=engine)
df_db = df_db[['time', 'hand', 'action_id', 'other_actions']]

db_action_run = filter_value1 + "_" + filter_value2

df_db.to_csv(r'..\data\db_actions\action_'+ db_action_run+'.csv', index=False)