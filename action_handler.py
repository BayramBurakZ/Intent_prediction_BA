class ActionHandler:
    """ A class that handles actions. """

    def __init__(self, goals):
        """ :param goals: (List)    List of goal instances """
        self.goals = goals

    def handle_action(self, action):
        """ Updates all goals and handles actions from database. columns: time, hand, action_id, other_actions
        :param action: (dataframe)  actions from database
        """
        # handle actions from db
        action_tuple = (parse_action_string_to_tuples(action['action_id']))[0]

        if action_tuple[0] == 'pick':
            self.deactivate_goal(action_tuple[1])

        # TODO "other actions" ... if database is cleaned

    def deactivate_goal(self, num):
        print("deactivating: " + str(num))
        for g in self.goals:
            if g.num == num:
                g.active = False
                self.goals.remove(g)
                break
                # TODO ADD deactivate List

    def activate_goal(self, num):
        for g in self.goals:
            if g.num == num:
                g.active = True


def parse_action_string_to_tuples(action_string):
    """ Splits the action string from database into tuples with action being either pick or place.
    observed action: "action_goalID_tokenID"
    other actions: "action_goalID_TokenID,pick_goalID_TokenID,..."

    :param action_string: (str)     action string
    :return: (tuple)                a tuple with action and goal id
    """
    components = action_string.split(',')
    result = []

    for component in components:
        parts = component.split('_')
        if len(parts) >= 2:
            # The first part is the action, the second part is the goal id
            action = parts[0]
            try:
                number = int(parts[1])
                result.append((action, number))
            except ValueError:
                print("corrupted database (other_)action")
                continue

    return result
