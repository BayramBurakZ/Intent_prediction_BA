from process_data import DataProcessor
from data_emitter import DataEmitter

import time
import queue
import threading
import pandas as pd
import numpy as np


class Main:
    def __init__(self):
        path = r'data/goals/goals.csv'
        df = pd.read_csv(path)
        coordinates = []
        for index, row in df.iterrows():
            coordinates.append(np.array([[row['x']], [row['y']], [row['z']]]))

        self.processor = DataProcessor(coordinates)
        self.data_queue = queue.Queue()
        self.data_emitter = DataEmitter(self.data_queue)



    def run(self):
        producer_thread = threading.Thread(target=self.data_emitter.emit_data)
        producer_thread.start()

        while True:
            try:
                data = self.data_queue.get()
                self.processor.process_data(data)
            except queue.Empty:
                print("wait for data...")
                time.sleep(0.2)



if __name__ == "__main__":
    main = Main()
    main.run()


