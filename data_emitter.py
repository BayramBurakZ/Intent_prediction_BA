import os
import time

import numpy as np


class DataEmitter:
    def __init__(self, data_queue, df_trajectories, df_actions, use_db):

        self.data_queue = data_queue
        self.df_trajectories = df_trajectories
        self.df_actions = df_actions
        self.use_db = use_db

    def emit_data(self):
        timestamps_traj = self.df_trajectories['time'].values.tolist()
        if self.use_db:
            timestamps_action = self.df_actions['time'].values
            timestamps_action = [int(element) for element in timestamps_action]

        start_time, end_time = 0, 50000
        current_time = start_time
        time_step = 25  # 17 ~ 60hz, 100 = 10hz
        speed = 0.1  # 0.1 (fast) < 1.0 (normal) < 10.0 (slow)

        curr_traj_index, curr_action_index = 0, 0
        max_index = None

        while current_time < end_time - time_step and curr_traj_index < len(timestamps_traj):
            data = []
            current_time += time_step

            # find the closest trajectory index to current time (can skip rows)
            for index, timestamp in enumerate(timestamps_traj[curr_traj_index:], start=curr_traj_index):
                if timestamp > current_time:
                    break
                max_index = index
                curr_traj_index = index + 1

            row = self.df_trajectories.iloc[max_index]
            ts = int(row['time'])

            #def add_noise(x):return np.random.normal(x, 0.005)

            coordinates = np.array([row['x'], row['y'], row['z']])
            data.append(ts)
            data.append(coordinates)
            max_index = None

            # check list of actions without skipping rows
            if self.use_db:
                for index, timestamp in enumerate(timestamps_action[curr_action_index:], start=curr_action_index):
                    if timestamp > current_time:
                        break
                    row = self.df_actions.iloc[index]
                    data.append(row)
                    curr_action_index = index + 1

            self.data_queue.put(data)  # save in queue

            # wait for "time_step" amount of milliseconds to simulate real time
            time.sleep(time_step * speed / 1000)

        self.data_queue.put(-1)
        #os._exit(0)