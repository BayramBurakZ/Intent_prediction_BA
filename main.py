import queue
import threading
import time

import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self, path_goals, path_trajectories, path_actions=r'data/db_actions/action_empty.csv',
                 rt_result=False):
        """
        Main class responsible for initializing file paths and parameters, as well as setting up data emitter and
         controller objects.

        Parameters:
            path_goals (str): The file path to the data file containing goal locations.
            path_trajectories (str): The file path to the data file containing hand wrist positions recorded over time.
            path_actions (str): The file path to the data file containing actions to be performed.
            rt_result (bool): A flag indicating whether to print the results of each iteration in real-time.
        """

        """
        Noise reducer type: None=0, SMA=1, WMA=2, EMA=3 ( 0 < alpha < 1 FOR EMA!)
        window: short: 5 to 10 | medium: 20 to 50 | long: 100 to 200
        
        NOISE_REDUCER_PARAMS (tuple): A tuple specifying
                [0] noise_reducer_type (int): The type of noise reduction technique to apply.
                [1] window_size_or_alpha (float): The window size or alpha value associated with the noise reducer.
        """
        NOISE_REDUCER_PARAMS = (0, 10)  # (NOISE_REDUCER, WINDOW_SIZE)

        """
        Minimum thresholds for prediction model calculations.
        standard values: (0.01,0.15)
        
        MODEL_PARAMS (tuple): A tuple specifying
                [0] min_distance (float): The minimum distance at which to begin calculations.
                [1] min_progression (float): The minimum progression along the predicted trajectory.
        """
        MODEL_PARAMS = (0.01, 0.15)  # (MIN_DIST, MIN_PROG)

        """
        Variance boundaries for normal distribution and weight for distance cost function for
        Standard values: (0.0625, 0.125, 1.0)
        
        PROBABILITY_PARAMS (tuple): A tuple specifying
                [0] variance_lower_limit (float): The lower bound for variance in the normal distribution.
                [1] variance_upper_limit (float): The upper bound for variance in the normal distribution.
                [2] omega (float): A parameter used in the cost function to adjust probabilities.
        """
        PROBABILITY_PARAMS = (0.0625, 0.125, 1.0)  # (MIN_VAR, MAX_VAR, OMEGA)

        """
        Emitter uses actions from database and standard deviation of noise to be added.
        DATA_EMITTER_PARAMS (tuple):
                [0] Boolean flag to enable or disable the use of the database.
                [1] Standard deviation of noise to be added
                [2] Start time
                [3] End time
                [4] Time step (17 ~ 60hz, 100 = 10hz)
                [5] Real time speed (0.001(fastest) < 0.1 (fast) < 1.0 (normal) < 10.0 (slow))
        """
        DATA_EMITTER_PARAMS = (False, 0.01, 0, 50000, 100, 0.001)

        """
        ACTION_HANDLER_PARAMS (tuple):
                [0] Boolean flag for Task: True for assembly and False for dismantling.
                [1] Hand that is being tracked.
        """
        ACTION_HANDLER_PARAMS = (True, 'right')

        # all goal positions and ids are saved in csv->(ID, x, y, z)
        df_goals = pd.read_csv(path_goals)

        # CSV with timestamp and coordinates of hand wrist
        df_trajectories = pd.read_csv(path_trajectories)

        # CSV with actions from database. None if database is disabled
        df_actions = pd.read_csv(path_actions) if DATA_EMITTER_PARAMS[0] else None

        self.rt_result = rt_result
        self.data_queue = queue.Queue()
        self.data_emitter = DataEmitter(self.data_queue, df_trajectories, df_actions, DATA_EMITTER_PARAMS)
        self.controller = Controller(df_goals, NOISE_REDUCER_PARAMS, MODEL_PARAMS, PROBABILITY_PARAMS,
                                     ACTION_HANDLER_PARAMS)

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
                        #print(result)  # time, ids, probabilities, samples, distances, angles, uncategorized
                        process_print_list(result)  # sorted and only time/frame, uncategorized, (id/probability)
            except queue.Empty:
                print("wait for data...")
                time.sleep(0.2)

        return results


def process_print_list(data):
    """ Prints sorted data for better readability."""

    # Extract the relevant parts from the data
    timestamps = data[0]
    uncat = data[-1]
    ids = data[1]
    prob = data[2]

    paired_elements = list(zip(ids, prob))

    # Sort the list of tuples by the second element (probabilities) in descending order
    sorted_paired_elements = sorted(paired_elements, key=lambda x: x[1], reverse=True)

    # Prepare the output in one line
    output = f"time: {timestamps}, frame:{int(timestamps / 40)}, uncat: {uncat}, " + ", ".join(
        f"({num}, {prob})" for num, prob in sorted_paired_elements)
    print(output)


if __name__ == "__main__":
    # all goal positions and ids are saved in csv->(ID, x, y, z)
    path_goals = r'data/study/goals/goals.csv'

    # CSV with timestamp and coordinates of hand wrist
    path_trajectories = r'data/study/right_hand/right_9.csv'

    # CSV with actions from database
    path_actions = r'data/test_data_study/test_action/31612_0_0.csv'

    main = Main(path_goals, path_trajectories, path_actions, True)
    results = main.run()
