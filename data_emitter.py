import time

import numpy as np


class DataEmitter:
    """ A class that represents a data emitter """

    def __init__(self, data_queue, df_trajectories, df_actions, DATA_EMITTER_PARAMS):
        """
        Parameters:
            data_queue (queue.Queue): The queue that stores the data to be processed.
            df_trajectories (pandas.DataFrame): DataFrame containing trajectory data.
            df_actions (pandas.DataFrame): DataFrame containing action data.
            DATA_EMITTER_PARAMS (tuple):
                [0]Boolean flag to enable or disable the use of the database.
                [1]Standard deviation of noise to be added
        """

        self.data_queue = data_queue
        self.df_trajectories = df_trajectories
        self.df_actions = df_actions
        self.USE_DB = DATA_EMITTER_PARAMS[0]
        self.NOISE_SD = DATA_EMITTER_PARAMS[1]

    def emit_data(self):
        """
        Streams data from DataFrames at specified intervals to simulate real-time measurements or to quickly process
        data for testing purposes.
        """
        # data to be used
        timestamps_traj = self.df_trajectories['time'].values.tolist()
        timestamps_action = self.df_actions['time'].values.tolist() if self.USE_DB else []

        # parameters for real time emitting
        start_time, end_time = 0, 50000
        curr_time = start_time
        time_step = 100  # 17 ~ 60hz, 100 = 10hz
        speed = 0.001  # 0.1 (fast) < 1.0 (normal) < 10.0 (slow)

        curr_traj_index, curr_action_index = 0, 0

        # emit data until end of data or end time is reached
        while curr_time < end_time - time_step and curr_traj_index < len(timestamps_traj):
            data = []
            curr_time += time_step

            # find the closest trajectory index to current time (can skip rows)
            while curr_traj_index < len(timestamps_traj) and timestamps_traj[curr_traj_index] <= curr_time:
                curr_traj_index += 1

            row = self.df_trajectories.iloc[curr_traj_index - 1]

            timestamp = int(row['time'])
            data.append(timestamp)

            coordinates = np.array([row['x'], row['y'], row['z']]) + add_noise(std_dev=self.NOISE_SD, size=3)
            data.append(coordinates)

            # check list of actions without skipping rows
            if self.USE_DB:
                while curr_action_index < len(timestamps_action) and timestamps_action[curr_action_index] <= curr_time:
                    action_row = self.df_actions.iloc[curr_action_index]
                    data.append(action_row)
                    curr_action_index += 1

            self.data_queue.put(data)  # save in queue

            # wait for certain amount of milliseconds to simulate real time
            time.sleep(time_step * speed / 1000)

        self.data_queue.put(-1)


def add_noise(mean=0.0, std_dev=0.01, size=1):
    """
    Adds Gaussian noise to the input values.

    The global root-mean-square error with wearable sensors and tracking cameras (such as Hololens 2) ranges from
    0.01 meters (with correction techniques) to 0.0375 meters (without correction techniques), according to
    Contreras-González et al., 2020 and Soares et al., 2021.

    Parameters:
        mean (float): The mean of the Gaussian noise in meters.
        std_dev (float): The standard deviation of the Gaussian noise in meters.
        size (int): The number of noise values to generate.

    Returns:
        numpy.ndarray: The generated Gaussian noise values.
    """

    return np.random.normal(mean, std_dev, size)
