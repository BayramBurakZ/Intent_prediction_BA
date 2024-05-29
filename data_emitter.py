import sys
import time

import numpy as np
import pandas as pd
from sqlalchemy import create_engine


class DataEmitter:
    # TODO: preprocess Database to csv data
    def __init__(self, data_queue):
        # CSV with timestamp and coordinates of hand wrist
        path_csv = r'data/right_hand/right_9.csv'
        self.df_csv = pd.read_csv(path_csv)
        self.data_queue = data_queue

        # CSV with actions from database
        path_db = r'data/db_actions/action_31612_0.csv'
        self.df_db = pd.read_csv(path_db)

        self.use_database = False

    def emit_data(self):
        timestamps_csv = self.df_csv['time'].values
        timestamps_db = self.df_db['time'].values
        timestamps_db = [int(element) for element in timestamps_db]

        time_step = 200
        current_time = timestamps_csv[0]
        #current_time = 19480
        current_index = 0
        db_index = 0
        #current_index = (self.df_csv['time'] >= current_time).idxmax()

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

                if current_time >= timestamps_db[0] and self.use_database:
                    timestamps_db.pop(0)
                    row = self.df_db.iloc[db_index]
                    db_index += 1
                    data.append(row)

                self.data_queue.put(data)  # save in queue

            current_time += time_step

            # wait for "time_step" amount of milliseconds to simulate real time
            time.sleep(time_step * 1 / 1000)

        sys.exit("EXIT: CSV finished")
