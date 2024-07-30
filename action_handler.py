import pandas as pd


class ActionHandler:
    """ A class that handles actions. """

    def __init__(self, goals, ACTION_HANDLER_PARAMS):
        """
        Parameters:
            goals (list): A list of goal instances.
            ACTION_HANDLER_PARAMS (tuple):
                [0] Boolean flag for Task: True for assembly and False for dismantling.
                [1] Hand that is being tracked.
        """

        self.goals = goals
        self.inactive_goals = []

        self.is_assembly = ACTION_HANDLER_PARAMS[0]
        self.tracked_hand = ACTION_HANDLER_PARAMS[1]

    def handle_action(self, action):
        """
        Updates all goals and handles actions from the database.

        Parameters:
            action (pandas.DataFrame): A DataFrame containing data for current action from the database.
            Each DataFrame includes the following columns:
                - time
                - hand
                - action_id
                - other_actions
        """
        # handle actions from db
        action_tuple = parse_action_string_to_tuples(action['action_id'])[0]
        print(
            f'{action_tuple[0]} action at: {action['time']} from: {action['hand']} hand to goal: {action_tuple[1]} '
            f'with other actions: {action['other_actions']}')

        # Handle the observed action 'pick' when assembling
        if self.is_assembly and action_tuple[0] == 'pick':
            self.deactivate_goal(action_tuple[1])
            if action['hand'] == self.tracked_hand:
                print('#############################################################################################')

        # Handle the observed action 'place' when dismantling
        if not self.is_assembly and action_tuple[0] == 'place':
            self.deactivate_goal(action_tuple[1])
            if action['hand'] == self.tracked_hand:
                print('#############################################################################################')

        # handle other (possible) actions by modifying the active list.
        if pd.notna(action['other_actions']):
            other_actions_tuple = parse_action_string_to_tuples(action['other_actions'])
            self.update_goal_lists_with_other_actions(other_actions_tuple)

    def deactivate_goal(self, num):
        print("deactivating: " + str(num))
        for index, g in enumerate(self.goals):
            if g.num == num:
                # Remove the goal from the active goals list
                temp = self.goals.pop(index)
                # Add the goal to the inactive goals list
                self.inactive_goals.append(temp)
                break

    def update_goal_lists_with_other_actions(self, actions):
        """
        Updates the lists of active and inactive goals based on specified actions. Actions are referring to goals and
        only possible ones should remain in active list.

        Parameters:
            actions (list): A list of tuples where each tuple contains an action ('pick') or ('place')
                            as first element and a goal_id (int) indicating the goal to be moved to active goals.

        """
        if ((self.is_assembly and any(a[0] == "place" for a in actions)) or
                (not self.is_assembly and any(a[0] == "pick" for a in actions))):
            return  # Exit for not relevant actions

        # Convert lists to dictionaries for easier/faster lookup and sorting.
        inactive_dict = {goal.num: goal for goal in self.goals + self.inactive_goals}
        active_dict = {}

        # Process the actions
        for action, goal_id in actions:
            # Move goal from inactive to active if it exists
            if goal_id in inactive_dict:
                active_dict[goal_id] = inactive_dict.pop(goal_id)
            else:
                print(f'Warning: Goal ID {goal_id} not found in the inactive list.')

        # Convert dictionaries back to sorted lists
        self.goals[:] = sorted(active_dict.values(), key=lambda goal: goal.num)
        self.inactive_goals[:] = sorted(inactive_dict.values(), key=lambda goal: goal.num)

    def activate_goal(self, num):
        # TODO: delete this function if executed run by run
        print('activating: ' + str(num))

        for i, goal in enumerate(self.inactive_goals):
            if goal.num == num:
                inserted = False

                for j, active_goal in enumerate(self.goals):
                    if goal.num < active_goal.num:
                        self.goals.insert(j, goal)
                        inserted = True
                        break

                if not inserted:
                    self.goals.append(goal)  # If it's the largest ID, append at the end
                self.inactive_goals.pop(i)  # Remove from inactive list
                break


def parse_action_string_to_tuples(action_string):
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
