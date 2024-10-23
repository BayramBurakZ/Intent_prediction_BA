import time
import queue
import pandas as pd
import numpy as np


class DataEmitter:
    """ A class that represents a data emitter """

    def __init__(self,
                 data_queue: queue.Queue,
                 df_trajectories: pd.DataFrame,
                 df_actions: pd.DataFrame,
                 DATA_EMITTER_PARAMS: tuple[bool, float, int, int, int, float, str, bool]
                 ) -> None:
        """
        Parameters:
            data_queue (queue.Queue): The queue that stores the data to be processed.
            df_trajectories (pandas.DataFrame): DataFrame containing trajectory data.
            df_actions (pandas.DataFrame): DataFrame containing action data.
            DATA_EMITTER_PARAMS (tuple):
                [0] Boolean flag to enable or disable the use of the database.
                [1] Standard deviation of noise to be added
                [2] Start time
                [3] End time
                [4] Time step (17 ~ 60hz, 100 = 10hz)
                [5] Real time speed (0.1 (fast) < 1.0 (normal) < 10.0 (slow))
                [6] String identifier of tracked hand, relevant of the set of next goals
                [7] Boolean flag indicating assembly/disassembly
        """

        self.data_queue = data_queue
        self.df_trajectories = df_trajectories
        self.df_actions = df_actions
        self.USE_DB = DATA_EMITTER_PARAMS[0]
        self.NOISE_SD = DATA_EMITTER_PARAMS[1]
        self.START_TIME = DATA_EMITTER_PARAMS[2]
        self.END_TIME = DATA_EMITTER_PARAMS[3]
        self.TIME_STEP = DATA_EMITTER_PARAMS[4]
        self.SPEED = DATA_EMITTER_PARAMS[5]
        self.TRACKED_HAND = DATA_EMITTER_PARAMS[6]
        self.IS_ASSEMBLY = DATA_EMITTER_PARAMS[7]

    def emit_data(self) -> None:
        """
        Streams data from DataFrames at specified intervals to simulate real-time measurements or to quickly process
        data for testing purposes.
        """
        # data to be used
        timestamps_traj = self.df_trajectories['time'].values.tolist()
        timestamps_action = self.df_actions['time'].values.tolist() if self.USE_DB else []

        # parameters for real time emitting
        start_time, end_time = self.START_TIME, self.END_TIME
        curr_time = start_time
        time_step = self.TIME_STEP
        speed = self.SPEED
        curr_traj_index, curr_action_index = 0, -1
        next_action_index = -1

        # emit data until end of data or end time is reached
        while curr_time < end_time - time_step and curr_traj_index < len(timestamps_traj):
            data = []
            curr_time += time_step
            same_data = True

            # Find the next trajectory index that is after the current time
            for index in range(curr_traj_index, len(timestamps_traj)):
                if timestamps_traj[index] > curr_time:
                    break

                curr_traj_index = index + 1
                same_data = False

            if same_data:
                continue

            row = self.df_trajectories.iloc[curr_traj_index - 1]
            data.append(int(row['time']))

            coordinates = np.array([float(row['x']), float(row['y']), float(row['z'])]) + add_noise(
                std_dev=self.NOISE_SD, size=3)
            data.append(coordinates)

            # Check list of actions without skipping rows
            if self.USE_DB and (next_action_index == -1 or timestamps_action[curr_action_index] <= data[0]):
                for index in range(curr_action_index + 1, len(timestamps_action)):
                    # add all actions up to current timestamp

                    if timestamps_action[index] > data[0]:
                        if next_action_index <= curr_action_index:
                            relevant_action_type = 'pick' if self.IS_ASSEMBLY else 'place'

                            # find next action of tracked hand to get goals
                            for index2 in range(curr_action_index + 1, len(timestamps_action)):
                                hand = self.df_actions['hand'][index2]
                                action_type = self.df_actions['action_id'][index2].split("_")[0]
                                if hand == self.TRACKED_HAND and action_type == relevant_action_type:
                                    data.append(self.df_actions.iloc[index2])
                                    next_action_index = index2
                                    break
                        break

                    data.append(self.df_actions.iloc[index])
                    curr_action_index = index

            self.data_queue.put(data)  # save in queue

            # wait for certain amount of milliseconds to simulate real time
            time.sleep(time_step * speed / 1000)

        self.data_queue.put(-1)


def add_noise(mean: float = 0.0, std_dev: float = 0.0, size: int = 1) -> float:
    """
    Adds Gaussian noise to the input values.

    Parameters:
        mean (float): The mean of the Gaussian noise in meters.
        std_dev (float): The standard deviation of the Gaussian noise in meters.
        size (int): The number of noise values to generate.

    Returns:
        numpy.ndarray: The generated Gaussian noise values.
    """

    return np.random.normal(mean, std_dev, size)
