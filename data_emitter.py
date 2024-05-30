import sys
import time

import numpy as np


class DataEmitter:
    # TODO: preprocess Database to csv data
    def __init__(self, data_queue, df_trajectories, df_actions):

        self.data_queue = data_queue
        self.df_trajectories = df_trajectories
        self.df_actions = df_actions
        self.use_database = False

    def emit_data(self):
        timestamps_csv = self.df_trajectories['time'].values
        timestamps_db = self.df_actions['time'].values
        timestamps_db = [int(element) for element in timestamps_db]

        time_step = 10  # 17 ~ 60hz, 100 = 10hz
        current_time = timestamps_csv[0]
        current_index = 0
        db_index = 0

        # current_time = 19480
        # current_index = (self.df_csv['time'] >= current_time).idxmax()
        # db_index = (self.df_db['time'] >= current_time).idxmax()

        while current_index < len(timestamps_csv):
            data = []

            # select next highest timestamp with simulated time
            if current_time >= timestamps_csv[current_index]:
                # select data
                row = self.df_trajectories.iloc[current_index]
                ts = int(row['time'])
                coordinates = np.array([row['x'], row['y'], row['z']])

                data.append(ts)
                data.append(coordinates)
                current_index += 1

                if current_time >= timestamps_db[0] and self.use_database:
                    timestamps_db.pop(0)
                    row = self.df_actions.iloc[db_index]
                    db_index += 1
                    data.append(row)

                self.data_queue.put(data)  # save in queue

            current_time += time_step

            # wait for "time_step" amount of milliseconds to simulate real time
            time.sleep(time_step * 1 / 1000)

        sys.exit("EXIT: CSV finished")
