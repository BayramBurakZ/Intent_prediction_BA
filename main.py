import queue
import threading
import time

import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self):
        # all goal positions and ids are saved in csv->(ID, x, y, z)
        path = r'data/goals/goal_test1.csv'
        df = pd.read_csv(path)

        # threshold to (de)activate goals
        goal_threshold = 1.1

        # minimum distance between samples to start calculating (in meters)
        sample_min_distance = 0.001

        # boundaries for normal distribution
        min_variance, max_variance = 0.0625, 0.125

        # activate real time plotter
        activate_plotter = False

        self.controller = Controller(df, goal_threshold, sample_min_distance, min_variance, max_variance,
                                     activate_plotter)
        self.data_queue = queue.Queue()
        self.data_emitter = DataEmitter(self.data_queue)

    def run(self):

        producer_thread = threading.Thread(target=self.data_emitter.emit_data)
        producer_thread.daemon = True  # so we can close thread with sys.exit
        producer_thread.start()

        while True:
            try:
                data = self.data_queue.get()
                self.controller.process_data(data)
            except queue.Empty:
                print("wait for data...")
                time.sleep(0.2)


if __name__ == "__main__":
    main = Main()
    main.run()
