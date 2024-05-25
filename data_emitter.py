import time
import queue
import pandas as pd
import numpy as np
class DataEmitter:
    def __init__(self, data_queue, start_time):
        path = r'data/right_hand/right_9.csv'
        self.df = pd.read_csv(path)
        self.data_queue = data_queue
        self.start_time = start_time

    def emit_data(self):
        sampling_rate = 1

        start_time = time.time()
        current_time = start_time

        for index, row in self.df.iterrows():

            timestamp = row['time']
            coordinates = np.array([[row['x']], [row['y']], [row['z']]])

            while (time.time() - current_time) < sampling_rate:
                time.sleep(0.01)

            #elapsed_time = (time.time() - start_time) * 1000  # in milliseconds
            self.data_queue.put([coordinates,timestamp])
            current_time = time.time()


