from dataclasses import dataclass, asdict
from typing import Literal
import numpy as np

from goal import Goal


# NOTE: This FILE been added after Tests.

@dataclass
class ActionData:
    """ Dataclass for action from database.
    time: Timestamp of action.
    hand: Hand that is used for action.
    type: Action type 'pick' or 'place'.
    target: Goal that is targeted.
    is_relevant: Whether action is relevant for assembly or dismantle.
    is_tracked_hand: True if the hand is tracked hand. False otherwise.
    possible_targets: All possible targets for this action.
    """
    time: int
    hand: Literal["right", "left", "robot"]
    type: Literal["pick", "place"]
    target: int

    is_relevant: bool
    is_tracked_hand: bool

    possible_targets: list[int] = None


class DataHandler:
    """ A class that handles data during runtime.

        Attributes:
        all_goals (list[Goal]): A list of all goals.
        use_database (bool): Indicates whether database (action) is being used.
        timestamp (int): The current timestamp of measurement.
        calculated (bool): A flag indicating if the prediction model has been calculated.
        curr_p (np.ndarray): The current hand wrist position in the prediction model.
        prev_p (np.ndarray): The previous hand wrist position in the prediction model.
        curr_dp (np.ndarray): The current derivative (direction) of hand wrist position in the prediction model.
        prev_dp (np.ndarray): The previous derivative (direction) of hand wrist position in the prediction mode
        possible_goals (list[Goal]): A copy of all_goals, used for filtering and possible future goals.
        actions (list): A list of actions at a timestamp.
        future_action (Any): The future action for look ahead.
    """

    def __init__(self, goals_all: list[Goal], use_database: bool = False):
        self.all_goals = goals_all
        self.use_database = use_database

        self.timestamp = None

        # prediction model:
        self.calculated = False
        self.curr_p = None
        self.prev_p = None
        self.prev_dp = None
        self.curr_dp = None

        # action handler:
        self.possible_goals = goals_all.copy()
        self.actions = []
        self.future_action = None

    def set_pm_data(self,
                    calculated: bool,
                    prev_p: np.ndarray,
                    curr_p: np.ndarray,
                    prev_dp: np.ndarray,
                    curr_dp: np.ndarray
                    ) -> None:
        """ Sets data from prediction model. """
        self.calculated = calculated
        self.curr_p = curr_p
        self.prev_p = prev_p
        self.prev_dp = prev_dp
        self.curr_dp = curr_dp

    def add_action(self, actions: ActionData) -> None:
        self.actions.append(asdict(actions))

    def set_future_tracked_target(self, action: ActionData) -> None:
        self.future_action = asdict(action)

    def get_goals(self) -> list[Goal]:
        if self.use_database:
            return self.possible_goals
        else:
            return self.all_goals

    def get_result(self) -> dict:
        """ Packages all results in python standard objects.

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

        goals_dict = Goal.goals_list_to_dict(self.get_goals())
        timestamp = self.timestamp
        hand_position = self.curr_p.tolist()

        num_prob_pairs = [(num, goal_data["probability"]) for num, goal_data in goals_dict.items()]
        uncat_prob = calculate_uncategorized_probability(goals_dict)
        top_3 = calculate_top3(goals_dict, uncat_prob)
        over_60 = calculate_over_60(top_3)

        return {
            "goals": goals_dict,
            "time": timestamp,
            "hand_position": hand_position,
            "num_prob_pairs": num_prob_pairs,
            "uncat_prob": uncat_prob,
            "top_3": top_3,
            "over_60_and_distance": over_60,
            "actions": self.actions,
            "future_action": self.future_action
        }


def calculate_uncategorized_probability(goals: dict) -> float:
    """ Calculates and returns the probability of uncategorized goal (or probability of no goal). """
    all_probabilities = [goal_data["probability"] for goal_data in goals.values()]
    return max(0, round(100 - sum(all_probabilities), 2))


def calculate_top3(goals: dict, uncategorized_probability: float) -> list[tuple[str, float, float]]:
    """ Calculates the top three highes probabilities.
     return (list[tuple[str, float, float]]): Between 1 and 3 elements with id, probability and distance (in meters).
     """
    probabilities = [(str(key), goal_data["probability"], goal_data["distance"])
                     for key, goal_data in goals.items()]
    probabilities.append(("U", uncategorized_probability, 0))
    probabilities_sorted = sorted(probabilities, key=lambda x: x[1], reverse=True)
    return [item for item in probabilities_sorted if item[1] > 0.0][:3]


def calculate_over_60(top_3: list[tuple[str, float, float]]) -> tuple[str, float, float] | None:
    """ Returns a goal when reached over 60% probability with id, probability and distance."""
    if top_3 and top_3[0][1] > 60.0:
        return top_3[0]
    return None
