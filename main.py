import queue
import threading
import time

import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self, path_goals, path_trajectories, path_actions=r'data/db_actions/action_empty.csv'):
        # minimum distance between samples to start calculating (in meters)
        MIN_DIST = 0.04
        MIN_PROG = 0.2

        # variance boundaries for normal distribution
        # MIN_VAR, MAX_VAR = 0.0625, 0.03125
        MIN_VAR, MAX_VAR = 0.125, 0.0625

        # activate real time plotter
        PLOTTER_ENABLED = False
        USE_DB = False

        # all goal positions and ids are saved in csv->(ID, x, y, z)
        df_goals = pd.read_csv(path_goals)

        # CSV with timestamp and coordinates of hand wrist
        df_trajectories = pd.read_csv(path_trajectories)

        # CSV with actions from database
        df_actions = pd.read_csv(path_actions) if USE_DB else None

        self.controller = Controller(df_goals, MIN_DIST, MIN_PROG, MIN_VAR, MAX_VAR, PLOTTER_ENABLED)
        self.data_queue = queue.Queue()
        self.data_emitter = DataEmitter(self.data_queue, df_trajectories, df_actions, USE_DB)

    def run(self):

        producer_thread = threading.Thread(target=self.data_emitter.emit_data)
        producer_thread.daemon = True  # to close thread with sys.exit
        producer_thread.start()

        results = []
        while True:
            try:
                data = self.data_queue.get()
                if data == -1:
                    break
                temp = self.controller.process_data(data)

                if temp is not None:
                    results.append(temp)

            except queue.Empty:
                print("wait for data...")
                time.sleep(0.2)

        return results

if __name__ == "__main__":
    # all goal positions and ids are saved in csv->(ID, x, y, z)
    path_goals = r'data/test_data/test_goal/2_1.csv'

    # CSV with timestamp and coordinates of hand wrist
    path_trajectories = r'data/test_data/test_trajectory/start_middle/traj_gentle_g2_1_target_1.csv'

    # CSV with actions from database
    path_actions = r'data/study/db_actions/action_31612_0.csv'

    main = Main(path_goals, path_trajectories, path_actions)
    main.run()
