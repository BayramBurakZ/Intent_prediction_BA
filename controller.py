import numpy as np

import noise_reducer
from action_handler import ActionHandler
from goal import Goal
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator


class Controller:
    """
    A class that controls the flow of data.

    Attributes:
        goals (list[Goals]): A list of instances of the Goals class.
        noise_reducer (NoiseReducer): An instance of one of the three noise reducer classes.
        prediction_model (PredictionModel): An instance for calculating trajectories.
        probability_evaluator (ProbabilityEvaluator): An instance for evaluating probability.
        action_handler (ActionHandler): An instance for manipulating the goals.
    """

    def __init__(self, df, NOISE_REDUCER_SETTINGS, MIN_THRESHOLDS, VARIANCE_BOUNDS):
        """
        Parameters:
            df (pandas.DataFrame): DataFrame containing goal positions and goal IDs.
            NOISE_REDUCER_SETTINGS (tuple): A tuple specifying the type of noise reducer and its window size (or alpha).
            MIN_THRESHOLDS (tuple): A tuple specifying the minimum distance to start calculating and
                                    the minimum progression on the prediction trajectory.
            VARIANCE_BOUNDS (tuple): A tuple specifying the lower and upper limits for variance in the normal distribution.
        """

        goal_data = process_df(df)
        self.goals = [Goal(number, position) for number, position in goal_data]
        self.noise_reducer = select_noise_reducer(NOISE_REDUCER_SETTINGS)
        self.prediction_model = PredictionModel(self.goals, MIN_THRESHOLDS)
        self.probability_evaluator = ProbabilityEvaluator(self.goals, VARIANCE_BOUNDS)
        self.action_handler = ActionHandler(self.goals)

    def process_data(self, data):
        """
        Distributes incoming data. The data contains the following:
            [0] -> time
            [1] -> hand wrist position
            [2], [3], [4], ... -> actions from the database.

        Parameters:
            data (list): A list containing:
                int: Time value.
                numpy.ndarray: Hand wrist position as a NumPy array of float64.
                pandas.DataFrame: Actions from the database.
        """

        stabilized_coordinates = data[1]  # Default value
        if self.noise_reducer:
            self.noise_reducer.add(data[1])
            noise_reduction_result = self.noise_reducer.get()
            if noise_reduction_result is not None:
                stabilized_coordinates = noise_reduction_result  # stabilized value

        # handle action TODO: fix database implementation after update
        for d in data[2:]:
            self.action_handler.handle_action(d)

        if len(data) < 2:
            return

        # calculate predicted direction
        self.prediction_model.update(stabilized_coordinates)

        # calculate the probability of predicted direction
        self.probability_evaluator.update()

        ids = [g.num for g in self.goals]
        probabilities = [round(g.prob * 100, 2) for g in self.goals]
        samples = [g.sq for g in self.goals]
        distances = [round(g.dist, 2) for g in self.goals]
        angles = [round(g.angle, 2) for g in self.goals]
        uncategorized = round(max(1 - sum(probabilities), 0) * 100, 2)

        return data[0], ids, probabilities, samples, distances, angles, uncategorized


def process_df(df):
    data = []
    for index, row in df.iterrows():
        data.append((int(row['ID']), np.array([row['x'], row['y'], row['z']])))

    assert len(data) > 0, 'the list of goal can not be empty'
    return data


def select_noise_reducer(settings):
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
