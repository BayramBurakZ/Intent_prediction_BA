class ActionHandler:
    """ A class that handles actions. """

    def __init__(self, goals):
        """
        Parameters:
            goals (list): A list of goal instances.
        """

        self.goals = goals
        self.inactive_goals = []

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
        action_tuple = (parse_action_string_to_tuples(action['action_id']))[0]
        print(
            f'{action_tuple[0]} action at: {action['time']} from: {action['hand']} for goal: {action_tuple[1]} with '
            f'other actions: {action['other_actions']}')

        if action_tuple[0] == 'pick':
            self.deactivate_goal(action_tuple[1])



    def deactivate_goal(self, num):
        print("deactivating: " + str(num))
        for g in self.goals:
            if g.num == num:
                temp = self.goals.pop(g)
                self.inactive_goals.append(temp)
                break

    def update_goal_lists_with_other_actions(self, actions):
        """
        Updates the lists of active and inactive goals based on specified actions.

        Parameters:
            actions (list of tuple): A list of tuples where each tuple contains an action ('pick')
                                     and a goal_id (int) indicating the goal to be moved to active goals.

        """
        # Convert lists to dictionaries for easier/faster lookup and sorting
        active_dict = {goal.id: goal for goal in self.goals}
        inactive_dict = {goal.id: goal for goal in self.inactive_goals}

        for action, goal_id in actions:
            if action == 'pick':
                # If the goal is in inactive goals, move it to active goals
                if goal_id in inactive_dict:
                    goal = inactive_dict.pop(goal_id)
                    active_dict[goal_id] = goal

                # If the goal is not in either list, it is a new goal
                elif goal_id not in active_dict:
                    print(f'Warning: Goal ID {goal_id} not found in either active or inactive goals.')
                    # raise ValueError(f"Goal ID {goal_id} not found in either active or inactive goals.")

        # Remaining goals in inactive_dict are those that were not picked
        inactive_dict.update({goal.id: goal for goal in self.goals if goal.id not in active_dict})

        # Convert dictionaries back to sorted lists and sort them by id
        self.goals[:] = sorted(active_dict.values(), key=lambda goal: goal.id)
        self.inactive_goals[:] = sorted(inactive_dict.values(), key=lambda goal: goal.id)

    def activate_goal(self, num):
        print('activating: ' + str(num))

        for i, goal in enumerate(self.inactive_goals):
            if goal.id == num:
                inserted = False

                for j, active_goal in enumerate(self.goals):
                    if goal.id < active_goal.id:
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
