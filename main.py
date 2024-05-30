import queue
import threading
import time

import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self):
        # all goal positions and ids are saved in csv->(ID, x, y, z)
        path_goals = r'data/goals/goals_test3.csv'
        df_goals = pd.read_csv(path_goals)

        # CSV with timestamp and coordinates of hand wrist
        path_trajectories = r'data/test_trajectories/traj_test3.csv'
        df_trajectories = pd.read_csv(path_trajectories)

        # CSV with actions from database
        path_actions = r'data/db_actions/action_31612_0.csv'
        df_actions = pd.read_csv(path_actions)

        # minimum distance between samples to start calculating (in meters)
        MIN_DIST = 0.05
        MIN_PROG = 0.15

        # variance boundaries for normal distribution
        MIN_VAR, MAX_VAR = 0.0625, 0.03125
        #MIN_VAR, MAX_VAR = 0.125, 0.03125

        # activate real time plotter
        PLOTTER_ENABLED = False

        self.controller = Controller(df_goals, MIN_DIST, MIN_PROG, MIN_VAR, MAX_VAR, PLOTTER_ENABLED)
        self.data_queue = queue.Queue()
        self.data_emitter = DataEmitter(self.data_queue, df_trajectories, df_actions)

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
