import sys
from typing import Optional
import numpy as np
import pandas as pd

import noise_reducer
from data_handler import DataHandler
from action_handler import ActionHandler
from goal import Goal
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator

from utilities import prediction_plotter


class Controller:
    """
    A class that controls the flow of data.

    Attributes:
        goals (list[Goals]): A list of instances of the Goals class.
        data_handler (DataHandler): An instance for handling the data during runtime.
        noise_reducer (NoiseReducer): An instance of one of the three noise reducer classes.
        prediction_model (PredictionModel): An instance for calculating trajectories.
        probability_evaluator (ProbabilityEvaluator): An instance for evaluating probability.
        action_handler (ActionHandler): An instance for manipulating the goals.
    """

    def __init__(self,
                 df: pd.DataFrame,
                 use_database: bool,
                 NOISE_REDUCER_PARAMS: tuple[int, float],
                 MODEL_PARAMS: tuple[float, float],
                 PROBABILITY_PARAMS: tuple[float, float, float],
                 ACTION_HANDLER_PARAMS: tuple[bool, str]
                 ) -> None:
        """
        Parameters:
            df (pandas.DataFrame): DataFrame containing the positions and IDs of the goals.
            use_database (bool): True when database (action) is used. False otherwise.
            NOISE_REDUCER_PARAMS (tuple): A tuple specifying
                [0] noise_reducer_type (int): The type of noise reduction technique to apply.
                [1] window_size_or_alpha (float): The window size or alpha value associated with the noise reducer.
            MODEL_PARAMS (tuple): A tuple specifying
                [0] min_distance (float): The minimum distance at which to begin calculations.
                [1] min_progression (float): The minimum progression along the predicted trajectory.
            PROBABILITY_PARAMS (tuple): A tuple specifying
                [0] variance_lower_limit (float): The lower bound for variance in the normal distribution.
                [1] variance_upper_limit (float): The upper bound for variance in the normal distribution.
                [2] omega (float): A parameter used in the cost function to adjust probabilities.
            ACTION_HANDLER_PARAMS (tuple):
                [0] is_assemble (bool): True for assemble_actions and False for dismantling.
                [1] hand (str): Hand that is being tracked.
        """

        goal_data = process_goal_df(df)
        self.goals = [Goal(number, position) for number, position in goal_data]

        self.data_handler = DataHandler(self.goals, use_database)
        self.prediction_model = PredictionModel(self.data_handler, MODEL_PARAMS)
        self.probability_evaluator = ProbabilityEvaluator(self.data_handler, PROBABILITY_PARAMS)
        self.action_handler = ActionHandler(self.data_handler, ACTION_HANDLER_PARAMS)
        self.noise_reducer = select_noise_reducer(NOISE_REDUCER_PARAMS)

    def process_data(self, data: list) -> Optional[dict]:
        """
        Distributes incoming data. The data contains the following:
            [0] -> timestamp.
            [1] -> hand wrist position.

            if available:
                [2], [3], [4], ... -> actions from the database.
                [-1] -> future action.

        Parameters:
            data (list): A list containing:
                (int): Time value.
                (numpy.ndarray): Hand wrist position as a NumPy array of float64.
                (pandas.DataFrame): Actions from the database.

        Return:
            Output (dict): Only python standard that contains:
            - 'goals' (dict): All goals and its attributes.
            - 'timestamp' (int): Timestamp of measurement.
            - 'hand_position' (list): Measured hand position.
            - 'num_prob_pairs' (list[tuple[float, float]): Goal id and probability pairs.
            - 'uncat_prob' (float): Probability of uncategorized goal (no goal).
            - 'top_3' (list[tuple[int, float, float]]): Top 3 highest probabilities with id, probability, distance.
            - 'over_60_and_distance' (tuple[int, float]): Goal id that has over 60% probability with distance in m.
            - 'actions' (dict): All actions for this timestamp with its attributes.
            - 'future_action' (dict): Future action with its attributes.
        """

        if is_bad_data(data):
            return None

        self.data_handler.timestamp = data[0]
        hand_position = data[1]

        self.data_handler.actions = []  # Reset actions for this measurement.
        for d in data[2:]:
            self.action_handler.handle_action(d)

        if len(self.goals) <= 0:
            sys.exit(1)  # Exit when there are no longer goals

        stabilized_coordinates = hand_position  # Default value
        if self.noise_reducer:
            self.noise_reducer.add(hand_position)
            noise_reduction_result = self.noise_reducer.get()
            if noise_reduction_result is not None:
                stabilized_coordinates = noise_reduction_result  # stabilized value

        # calculate predicted direction
        self.prediction_model.update(stabilized_coordinates)

        # Skip measurements when no prediction is calculated.
        if not self.data_handler.calculated:
            # NOTE: This has been added after Tests.
            return None

        self.data_handler.hand_position = stabilized_coordinates

        # calculate the probability of predicted direction
        self.probability_evaluator.update()

        self.data_handler.calculated = False
        return self.data_handler.get_result()


def process_goal_df(df: pd.DataFrame) -> list:
    """ Processes goal Dataframe. """
    data = []
    for index, row in df.iterrows():
        data.append((int(row['ID']), np.array([float(row['x']), float(row['y']), float(row['z'])])))

    assert len(data) > 0, 'the list of goal can not be empty'
    return data


def select_noise_reducer(settings: tuple[int, float]) -> Optional[noise_reducer]:
    """ Select the appropriate strategy to smooth data and reduce noise. """
    noise_reducers = {
        0: None,
        1: noise_reducer.SimpleMovingAverage,
        2: noise_reducer.WeightedMovingAverage,
        3: noise_reducer.ExponentialMovingAverage
    }

    try:
        if settings[0] == 0:
            return None
        return noise_reducers[settings[0]](settings[1])
    except KeyError:
        raise ValueError('Undefined noise settings!')


def is_bad_data(data: list) -> bool:
    """
        Checks if the provided data is invalid based on specific conditions.

        Conditions:
        - data must have at least two elements.
        - data[0] must be an integer.
        - data[1] must be a numpy array with size of 3 and all elements of type float.

        Returns:
        - bool: True if any of the conditions are not met. False if all conditions are satisfied
    """

    if len(data) < 2:
        return True

    if not isinstance(data[0], int):
        return True

    if (not isinstance(data[1], np.ndarray) or
            not np.issubdtype(data[1].dtype, np.floating) or
            data[1].shape[0] != 3):
        return True

    return False
