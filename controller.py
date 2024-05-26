import numpy as np
import logging

from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator


class Controller:
    """ A class that controls the flow of data.

    Attributes:
        sample_distance: (float)                        minimum distance between samples to calculate prediction
        prediction_model: (PredictionModel)             the prediction model
        probability_evaluator: (ProbabilityEvaluator)   the probability evaluator

    """

    def __init__(self, all_goal_positions, sample_distance=0.01):
        """ Initializes the DataProcessor object.

        :param all_goal_positions: (List[NDArray[np.float64]])  coordinates of all goals
        :param sample_distance: (float)     minimum distance between samples to calculate prediction
        """
        assert len(all_goal_positions) > 0, "the list of goal can not be empty"
        assert all(goal.shape == (3, 1) for goal in all_goal_positions), "goal vectors must have the shape (3,1) "

        logging.basicConfig(filename=r'./data/logs/reached_goals.log', level=logging.INFO,
                            format='%(asctime)s %(message)s')
        self.sample_distance = sample_distance
        self.prediction_model = PredictionModel(all_goal_positions)
        self.probability_evaluator = ProbabilityEvaluator(len(all_goal_positions))

    def process_data(self, data):
        """ Processes the incoming data.

        :param data: (List[int, NDArray[np.float64]])  data to be processed
        """


        if is_bad_data(data):
            print("skipped bad data")
            return

        t_current = data[0]
        p_current = data[1]
        p_previous = self.prediction_model.p_current

        # only calculate after minimum distance between measurements is reached
        if euclidean_distance(p_previous, p_current) < self.sample_distance:
            return

        direction_vectors = self.prediction_model.calculate_predicted_direction(p_current, t_current)
        self.probability_evaluator.evaluate_angles(self.prediction_model.dp_current, direction_vectors)
        print(
            f"Timestamp: {data[0]}, probability: {tr(self.probability_evaluator.probability_goals), round(self.probability_evaluator.probability_uncategorized * 100, 2)}")
        reached_goal(p_current, self.prediction_model.goal_positions, t_current)


def tr(g):
    return [round(x * 100, 2) for x in g]


def euclidean_distance(column_vector1, column_vector2):
    """ Calculates the Euclidean distance between two vectors. """
    return np.linalg.norm(column_vector1 - column_vector2)


def is_bad_data(data):
    """ checks for bad data """
    if data[0] < 0 or not isinstance(data[0], int):
        return True

    # TODO: catch bad coordinates earlier!
    """
    if all(not isinstance(item, float) for item in data[1].flatten().tolist()):
        return True"""

    return False


def reached_goal(p_current, goals, timestamp):
    for i in range(len(goals)):
        if euclidean_distance(p_current, goals[i]) < 0.1:
            logging.info(f"Timestamp: {timestamp} goal: {i}" )
            print(f"Timestamp: {timestamp}", "goal:", i)
