import queue
import threading
import time

import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self):
        # all goal positions and ids are saved in csv->(ID, x, y, z)
        path = r'data/goals/goals_test1.csv'
        df = pd.read_csv(path)


        # minimum distance between samples to start calculating (in meters)
        sample_min_distance = 0.05
        min_predicted_prog = 0.15

        # boundaries for normal distribution
        min_variance, max_variance = 0.0625, 0.03125
        #min_variance, max_variance = 0.125, 0.03125

        # activate real time plotter
        activate_plotter = False

        self.controller = Controller(df, sample_min_distance, min_variance, max_variance,
                                     activate_plotter, min_predicted_prog)
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
