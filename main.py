import queue
import threading
import time

import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self, path_goals, path_trajectories, path_actions=r'data/db_actions/action_empty.csv',
                 rt_result=False):

        # Noise reducer type: None=0, SMA=1, WMA=2, EMA=3 ( 0 < alpha < 1 FOR EMA!)
        # window: short: 5 to 10 | medium: 20 to 50 | long: 100 to 200
        NOISE_REDUCER_PARAMS = (1, 10)  # (NOISE_REDUCER, WINDOW_SIZE)

        # Minimum thresholds for calculations
        MODEL_PARAMS = (0.01, 0.2)  # (MIN_DIST, MIN_PROG)

        # Variance boundaries for normal distribution
        PROBABILITY_PARAMS = (0.0625, 0.125, 1.0)  # (MIN_VAR, MAX_VAR, OMEGA)

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
        self.controller = Controller(df_goals, NOISE_REDUCER_PARAMS, MODEL_PARAMS, PROBABILITY_PARAMS)

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
