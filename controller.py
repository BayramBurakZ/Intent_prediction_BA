from goal import Goal
from action_handler import ActionHandler
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator

import numpy as np


class Controller:
    """ A class that controls the flow of data.

    Attributes:
        prediction_model: (PredictionModel)             instance for calculating trajectories
        probability_evaluator: (ProbabilityEvaluator)   instance for evaluating probability
        action_handler: (ActionHandler)                 instance for manipulating the goal
        animated_plots: (AnimatedPlots)                 instance for animating data
    """

    def __init__(self, df, min_dist, min_prog, min_var, max_var, activate_plotter):
        """ Constructor for the Controller class.

        :param df: (dataframe)                      dataframe with goal positions and goal id
        :param min_dist: (float)                    minimum distance to use lower boundary
        :param min_prog: (float)                    minimum prediction progression as lower boundary
        :param min_var: (float)                     lower limit for variance in normal distribution
        :param max_var: (float)                     upper limit for variance in normal distribution
        :param activate_plotter: (bool)             activates the real time plotter
        """
        goal_data = process_df(df)
        self.goals = [Goal(number, position) for number, position in goal_data]
        self.prediction_model = PredictionModel(self.goals, min_dist, min_prog)
        self.probability_evaluator = ProbabilityEvaluator(self.goals, min_var, max_var)
        self.action_handler = ActionHandler(self.goals)

        # live visualization with real time plotter (optional) #TODO massive performance problems when plotting
        # self.animated_plots = AnimatedPlots(self.goals_position)

        """if activate_plotter:
            self.animated_plots.animate()"""

    def process_data(self, data):
        """ Distributes incoming data. Data contains [0]-> time, [1]-> hand wrist position
            and [2] -> actions from database.

        :param data: (List[int, NDArray[np.float64], Dataframe)     data to be processed
        """
        # TODO: catch bad data

        # calculate predicted direction
        self.prediction_model.update(data[1])

        # calculate the probability of predicted direction
        self.probability_evaluator.update()

        # handle action
        if len(data) > 2:
            self.action_handler.handle_action(data[2])

        probabilities = [round(g.prob_total*100, 2) for g in self.goals]
        uncat_goal = round(max(1 - sum(probabilities), 0) * 100, 2)
        print("time: ", data[0], " probability: ", probabilities, " uncategorized goal: ", uncat_goal)


def process_df(df):
    """ Processes dataframe """
    data = []
    for index, row in df.iterrows():
        data.append((row['ID'], np.array([row['x'], row['y'], row['z']])))

    assert len(data) > 0, "the list of goal can not be empty"
    return data
