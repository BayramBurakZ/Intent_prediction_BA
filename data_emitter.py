import time

import numpy as np
import pandas as pd
from sqlalchemy import create_engine


class DataEmitter:
    # TODO: consider calculations for both hand to run in parallel
    def __init__(self, data_queue):
        # CSV with timestamp and coordinates of hand wrist
        path_csv = r'data/right_hand/right_9.csv'
        self.df_csv = pd.read_csv(path_csv)
        self.data_queue = data_queue

        # Database with actions
        path_db = r'data/study_db/Log_data_with_token_shapes.db'
        table_name = 'new_table'
        column_name1 = 'participant_id'
        column_name2 = 'trial'
        filter_value1 = '31612'
        filter_value2 = '0'

        engine = create_engine(f"sqlite:///{path_db}")
        query = f"SELECT * FROM {table_name} WHERE {column_name1} = {filter_value1} AND {column_name2} = {filter_value2}"
        self.df_db = pd.read_sql_query(query, con=engine)
        self.df_db = self.df_db[['time', 'hand', 'action_id', 'other_actions']]

    def emit_data(self):
        timestamps_csv = self.df_csv['time'].values
        timestamps_db = self.df_db['time'].values
        time_step = 1  # TODO: change this if it takes too much resources

        #current_time = timestamps_csv[0]
        current_time = 19480
        #current_index = 0
        db_index = 0
        current_index = (self.df_csv['time'] >= current_time).idxmax()

        while current_index < len(timestamps_csv):

            data = []

            # select next highest timestamp with simulated time
            if current_time >= timestamps_csv[current_index]:
                # select data
                row = self.df_csv.iloc[current_index]
                ts = int(row['time'])
                coordinates = np.array([row['x'], row['y'], row['z']])

                data.append(ts)
                data.append(coordinates)
                current_index += 1

                if current_time >= timestamps_db[0]:
                    row = self.df_db.iloc[db_index]
                    db_index += 1
                    data.append(row)


                self.data_queue.put(data)  # save in queue

            current_time += time_step

            # wait for "time_step" amount of milliseconds to simulate real time
            time.sleep(time_step / 1000)
