import queue
import threading
import time

import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self, path_goals, path_trajectories, path_actions=r'data/db_actions/action_empty.csv',
                 rt_result=False):

        # minimum distance between samples to start calculating (in meters)
        MIN_DIST = 0.01 # in meters
        MIN_PROG = 0.2

        # variance boundaries for normal distribution
        MIN_VAR, MAX_VAR = 0.0625, 0.125  # (1/16), (1/8)

        # use database of study
        USE_DB = False

        # all goal positions and ids are saved in csv->(ID, x, y, z)
        df_goals = pd.read_csv(path_goals)

        # CSV with timestamp and coordinates of hand wrist
        df_trajectories = pd.read_csv(path_trajectories)

        # CSV with actions from database
        df_actions = pd.read_csv(path_actions) if USE_DB else None

        self.rt_result = rt_result
        self.data_queue = queue.Queue()
        self.data_emitter = DataEmitter(self.data_queue, df_trajectories, df_actions, USE_DB)
        self.controller = Controller(df_goals, MIN_DIST, MIN_PROG, MIN_VAR, MAX_VAR)

    def run(self):

        producer_thread = threading.Thread(target=self.data_emitter.emit_data)
        producer_thread.daemon = True  # to close thread with sys.exit
        producer_thread.start()

        results = []
        while True:
            try:
                data = self.data_queue.get()

                if data == -1:  # stop when no more data
                    break

                result = self.controller.process_data(data)

                if result is not None:
                    results.append(result)

                    if self.rt_result:
                        print(result)  # time, ids, probabilities, samples, distances, angles, uncategorized

            except queue.Empty:
                print("wait for data...")
                time.sleep(0.2)

        return results


if __name__ == "__main__":
    # all goal positions and ids are saved in csv->(ID, x, y, z)
    path_goals = r'data/test_data/test_goal/3_6.csv'

    # CSV with timestamp and coordinates of hand wrist
    path_trajectories = r'data/test_data/test_trajectory/3_6_1_11.csv'

    # CSV with actions from database
    path_actions = r'data/study/db_actions/action_31612_0.csv'

    main = Main(path_goals, path_trajectories, path_actions, True)
    results = main.run()
