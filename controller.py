from goal import Goal
from action_handler import ActionHandler
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator
from real_time_plotter import AnimatedPlots

import numpy as np


class Controller:
    """ A class that controls the flow of data.

    Attributes:
        prediction_model: (PredictionModel)             instance for calculating trajectories
        probability_evaluator: (ProbabilityEvaluator)   instance for evaluating probability
        action_handler: (ActionHandler)                 instance for manipulating the goal
        animated_plots: (AnimatedPlots)                 instance for animating data
    """

    def __init__(self, df, MIN_DIST, MIN_PROG, MIN_VAR, MAX_VAR, PLOTTER_ENABLED):
        """ Constructor for the Controller class.

        :param df: (dataframe)                      dataframe with goal positions and goal id
        :param MIN_DIST: (float)                    minimum distance to use lower boundary
        :param MIN_PROG: (float)                    minimum prediction progression as lower boundary
        :param MIN_VAR: (float)                     lower limit for variance in normal distribution
        :param MAX_VAR: (float)                     upper limit for variance in normal distribution
        :param PLOTTER_ENABLED: (bool)              enables the real time plotter
        """
        goal_data = process_df(df)
        self.goals = [Goal(number, position) for number, position in goal_data]
        self.prediction_model = PredictionModel(self.goals, MIN_DIST, MIN_PROG)
        self.probability_evaluator = ProbabilityEvaluator(self.goals, MIN_VAR, MAX_VAR)
        self.action_handler = ActionHandler(self.goals)

        # live visualization with real time plotter (optional) #TODO massive performance problems when plotting
        self.animated_plots = AnimatedPlots()
        self.PLOTTER_ENABLED = PLOTTER_ENABLED

        if PLOTTER_ENABLED:
            self.animated_plots.animate()

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

        # TODO somewhere here bug
        probabilities = [round(g.prob_total*100, 2) for g in self.goals]
        uncat_goal = round(max(1 - sum(probabilities), 0) * 100, 2)
        print("time: ", data[0], " probability: ", probabilities, " uncategorized goal: ", uncat_goal)

        if self.PLOTTER_ENABLED:
            self.animated_plots.update_data([self.goals, ])


def process_df(df):
    """ Processes dataframe """
    data = []
    for index, row in df.iterrows():
        data.append((row['ID'], np.array([row['x'], row['y'], row['z']])))

    assert len(data) > 0, "the list of goal can not be empty"
    return data

