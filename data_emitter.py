import time

import numpy as np
import pandas as pd


class DataEmitter:
    # TODO: consider calculations for both hand to run in parallel
    def __init__(self, data_queue):
        #path = r'data/test_trajectories/test1.csv'
        path = r'data/right_hand/right_9.csv'
        self.df = pd.read_csv(path)
        self.data_queue = data_queue

    def emit_data(self):
        timestamps = self.df['time'].values
        time_step = 1  # TODO: change this if it takes too much resources
        # current_time = timestamps[0]
        current_time = 19480
        current_index = 0

        while current_index < len(timestamps):

            # select next highest timestamp with simulated time
            if current_time >= timestamps[current_index]:
                # select data
                row = self.df.iloc[current_index]
                ts = int(row['time'])
                coordinates = np.array([[row['x']], [row['y']], [row['z']]])

                self.data_queue.put([ts, coordinates])  # save in queue
                current_index += 1

            current_time += time_step

            # wait for "time_step" amount of milliseconds to simulate real time
            time.sleep(time_step / 1000)
