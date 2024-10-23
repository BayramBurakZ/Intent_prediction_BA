import sys

import pandas
import pandas as pd
from data_handler import DataHandler
from data_handler import ActionData


class ActionHandler:
    """ A class that handles actions. """

    def __init__(self, data_handler: DataHandler, ACTION_HANDLER_PARAMS: tuple[bool, str]) -> None:
        """
        Parameters:
            data_handler (DataHandler): An instance for handling the data during runtime.
            ACTION_HANDLER_PARAMS (tuple):
                [0] Boolean flag for Task (bool): True for assemble_actions and False for dismantling.
                [1] hand (str): Hand that is being tracked.
        """
        self.data_handler = data_handler
        self.possible_goals = self.data_handler.possible_goals

        self.is_assembly = ACTION_HANDLER_PARAMS[0]
        self.tracked_hand = ACTION_HANDLER_PARAMS[1]

    def handle_action(self, action_df: pd.DataFrame) -> None:
        """
        Updates all goals and handles actions from the database.

        Parameters:
            action_df (pandas.DataFrame): A DataFrame containing data for current action from the database.
            Each DataFrame includes the following columns:
                - time
                - hand
                - action_id
                - possible_actions
        """
        action = self.convert_action(action_df)

        # Check if it is a future action.
        if action.time <= self.data_handler.timestamp:
            print(f"{action.type} action at: {action.time} from: {action.hand} hand to goal: {action.target}")
            self.data_handler.add_action(action)

            # Handle the observed relevant action when assembling or dismantling
            if action.is_relevant:
                removed = self.remove_goal(action.target)

                # Exit when no more goals are active.
                if len(self.data_handler.all_goals) < 1:
                    sys.exit(1)

                # Switch to all goals when possible goals are empty.
                if len(self.possible_goals) < 1:
                    self.possible_goals[:] = self.possible_goals[:] = self.data_handler.all_goals.copy()

                if removed:
                    msg = f"Deactivating :  {action.target}"
                    if action.is_tracked_hand:
                        msg += " <----- IS tracked hand."
                    else:
                        msg += " <----- NOT tracked hand."

                    print_boxed_message_1(msg)

        else:
            # Handle future actions.
            self.data_handler.set_future_tracked_target(action)

            if (action.possible_targets is not None and len(self.possible_goals) > 0 and
                    any(goal.num == action.target for goal in self.data_handler.all_goals)):

                # Reduce goal amount with possible actions.
                unique_targets = list(set([action.target] + action.possible_targets))
                self.possible_goals[:] = (filter(lambda g: g.num in unique_targets, self.data_handler.all_goals))
                targets = [t.num for t in self.possible_goals]

                msg = (f" Reduced to {len(self.possible_goals)} possible targets: {targets} ===> {action.target} going "
                       f"to be picked at {action.time} <===")

            else:
                msg = "Corrupt database line for possible future goals. Falling back to all goals with "

                if action.target in self.data_handler.all_goals:
                    msg += f"future target: {action.target}."
                else:
                    msg += "no future target."

                # Switch to all goals when action is faulty.
                self.possible_goals[:] = self.data_handler.all_goals.copy()

            print_boxed_message_2(msg)

    def convert_action(self, action: pandas.DataFrame) -> ActionData:
        """
        Converts actions from database (dataframe) to ActionData (dataclass).

        action (pandas.DataFrame): Action to be converted.
        return: Action as ActionData object.
        """
        time = int(action['time'])
        hand = action['hand']

        action_tuple = parse_action_string_to_tuples(action['action_id'])[0]
        action_type = action_tuple[0]
        target = action_tuple[1]

        relevant_action_type = 'pick' if self.is_assembly else 'place'
        is_relevant = (action_type == relevant_action_type)
        is_tracked = (hand == self.tracked_hand)

        if pd.notna(action['possible_actions']):
            possible_actions_tuple = parse_action_string_to_tuples(action['possible_actions'])
            if all(action_str == action_type for action_str, _ in possible_actions_tuple):
                possible_targets = [action_int for _, action_int in possible_actions_tuple]
                return ActionData(time, hand, action_type, target, is_relevant, is_tracked, possible_targets)

        return ActionData(time, hand, action_type, target, is_relevant, is_tracked)

    def remove_goal(self, goal_id: int) -> bool:
        """
        Removes goal from possible and all actions.

        goal_id (int): Goal id to be removed.
        return: True if it is successfully removed. False otherwise.
        """
        bad_db_entry = True
        for index, g in enumerate(self.possible_goals):
            if g.num == goal_id:
                # Remove the goal from the active goals list
                self.possible_goals.pop(index)

        for index, g in enumerate(self.data_handler.all_goals):
            if g.num == goal_id:
                # Remove the goal from the active goals list
                self.data_handler.all_goals.pop(index)
                return True

        if bad_db_entry:
            print(f"Goal ID:{goal_id} is not in the list of all goals.")
            return False


def parse_action_string_to_tuples(action_string: str) -> list:
    """
    Splits the action string from the database into tuples, with actions being either 'pick' or 'place'.

    The observed action format is "action_goalID_tokenID".
    Other actions format is "action_goalID_TokenID,pick_goalID_TokenID,...".

    Parameters:
        action_string (str): The action string.

    Returns:
        list: A list of tuples containing the action and goal ID.
    """

    components = action_string.split(',')
    result = []

    for component in components:
        parts = component.split('_')
        if len(parts) >= 2:
            try:
                # The first part is the action, the second part is the goal id
                action = parts[0]
                number = int(parts[1])
                result.append((action, number))
            except ValueError:
                print('corrupted database (other_)action')
                continue

    return result


def print_boxed_message_1(message: str):
    border = "+" + "-" * (len(message) + 10) + "+"
    print(border)
    print(f"|  {message}  |")
    print(border)


def print_boxed_message_2(message: str):
    border = "+" + "#" * (len(message) + 10) + "#"
    print(border)
    print(f"|  {message}  |")
    print(border)
