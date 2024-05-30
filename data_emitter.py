import os
import time

import numpy as np


class DataEmitter:
    # TODO: preprocess Database to csv data
    def __init__(self, data_queue, df_trajectories, df_actions, USE_DB):

        self.data_queue = data_queue
        self.df_trajectories = df_trajectories
        self.df_actions = df_actions
        self.USE_DB = USE_DB

    def emit_data(self):
        timestamps_traj = self.df_trajectories['time'].values.tolist()
        timestamps_action = self.df_actions['time'].values
        timestamps_action = [int(element) for element in timestamps_action]

        start_time, end_time = 0, 999
        current_time = start_time
        time_step = 1  # 17 ~ 60hz, 100 = 10hz
        speed = 0.1  # 0.1 (fast) < 1.0 (normal) < 10.0 (slow)

        curr_traj_index, curr_action_index = 0, 0
        max_index1 = None

        while current_time < end_time - time_step:
            data = []
            current_time += time_step

            # check list of trajectories
            while curr_traj_index < len(timestamps_traj) and timestamps_traj[curr_traj_index] <= current_time:
                max_index1 = curr_traj_index
                curr_traj_index += 1

            # skip trajectories between time steps
            if max_index1 is not None:
                row = self.df_trajectories.iloc[curr_traj_index]
                ts = int(row['time'])
                coordinates = np.array([row['x'], row['y'], row['z']])
                data.append(ts)
                data.append(coordinates)
                max_index1 = None

            # check list of actions
            if self.USE_DB:
                while curr_action_index < len(timestamps_action) and timestamps_action[
                    curr_action_index] <= current_time:
                    row = self.df_actions.iloc[curr_action_index]
                    data.append(row)
                    curr_action_index += 1

            # no more data end program
            if curr_traj_index >= len(timestamps_traj):
                break

            self.data_queue.put(data)  # save in queue

            # wait for "time_step" amount of milliseconds to simulate real time
            time.sleep(time_step * speed / 1000)

        os._exit(0)
