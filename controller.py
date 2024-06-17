import numpy as np

from goal import Goal
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator
from action_handler import ActionHandler


class Controller:
    """ A class that controls the flow of data.

    Attributes:
        prediction_model: (PredictionModel)             instance for calculating trajectories
        probability_evaluator: (ProbabilityEvaluator)   instance for evaluating probability
        action_handler: (ActionHandler)                 instance for manipulating the goal
    """

    def __init__(self, df, MIN_DIST, MIN_PROG, MIN_VAR, MAX_VAR):
        """ Constructor for the Controller class.

        :param df: (dataframe)                      dataframe with goal positions and goal id
        :param MIN_DIST: (float)                    minimum distance to use lower boundary
        :param MIN_PROG: (float)                    minimum prediction progression as lower boundary
        :param MIN_VAR: (float)                     lower limit for variance in normal distribution
        :param MAX_VAR: (float)                     upper limit for variance in normal distribution
        """
        goal_data = process_df(df)
        self.goals = [Goal(number, position) for number, position in goal_data]
        self.prediction_model = PredictionModel(self.goals, MIN_DIST, MIN_PROG)
        self.probability_evaluator = ProbabilityEvaluator(self.goals, MIN_VAR, MAX_VAR)
        self.action_handler = ActionHandler(self.goals)

    def process_data(self, data):
        """ Distributes incoming data. Data contains [0]-> time, [1]-> hand wrist position
            and [2],[3]... -> actions from database.

        :param data: (List[int, NDArray[np.float64], Dataframe])     data to be processed
        """

        # handle action TODO: fix database implementation after update
        for d in data[2:]:
            self.action_handler.handle_action(d)

        if len(data) < 2:
            return

        # calculate predicted direction
        self.prediction_model.update(data[1])

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
    """ Processes dataframe """
    data = []
    for index, row in df.iterrows():
        data.append((int(row['ID']), np.array([row['x'], row['y'], row['z']])))

    assert len(data) > 0, 'the list of goal can not be empty'
    return data
