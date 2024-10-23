import queue
import threading
import time
import pandas as pd

from controller import Controller
from data_emitter import DataEmitter


class Main:
    def __init__(self,
                 path_goals: str,
                 path_trajectories: str,
                 path_actions: str = r'data/db_actions/action_empty.csv',
                 rt_result: bool = False,
                 use_db: bool = False,
                 is_asemble: bool = True,
                 hand: str = 'right'
                 ) -> None:
        """
        Main class responsible for initializing file paths and parameters, as well as setting up data emitter and
         controller objects.

        Parameters:
            path_goals (str): The file path to the data file containing goal locations.
            path_trajectories (str): The file path to the data file containing hand wrist positions recorded over time.
            path_actions (str): The file path to the data file containing actions to be performed.
            rt_result (bool): A flag indicating whether to print the results of each iteration in real-time.
            use_db (bool): True if database (actions) are used. False otherwise.
            is_asemble (bool): True if assemble task is chosen. False otherwise.
            hand (str): Whether 'left' or 'right' hand is being tracked.
        """
        # all goal positions and ids are saved in csv->(ID, x, y, z)
        df_goals = pd.read_csv(path_goals)

        # CSV with timestamp and coordinates of hand wrist
        df_trajectories = pd.read_csv(path_trajectories)

        # CSV with actions from database. None if database is disabled
        df_actions = pd.read_csv(path_actions) if use_db else None

        """
                Parameters for action handler.

                ACTION_HANDLER_PARAMS (tuple):
                        [0] Boolean flag for Task: True for assemble_actions and False for dismantling.
                        [1] Hand that is being tracked.
        """
        ACTION_HANDLER_PARAMS = (is_asemble, hand)

        """
        Noise reducer type: None=0, SMA=1, WMA=2, EMA=3 (for EMA: 0 < alpha < 1)
        window: short: 5 to 15 | medium: 15 to 30 | long: 30 to 50
        Best: (2, 10) for generated | (2, 25) for recorded 
        
        NOISE_REDUCER_PARAMS (tuple): A tuple specifying
                [0] noise_reducer_type (int): The type of noise reduction technique to apply.
                [1] window_size_or_alpha (float): The window size or alpha value associated with the noise reducer.
        """
        NOISE_REDUCER_PARAMS = (2, 25)  # (NOISE_REDUCER, WINDOW_SIZE)

        """
        Minimum thresholds for prediction model calculations.
        Best: (0.025, 0.0) for generated | (0.01, 0.15) for recorded
        
        MODEL_PARAMS (tuple): A tuple specifying
                [0] min_distance (float): The minimum distance at which to begin calculations.
                [1] min_progression (float): The minimum progression along the predicted trajectory. (0 < prog < 1)
        """
        MODEL_PARAMS = (0.01, 0.15)  # (MIN_DIST, MIN_PROG)

        """
        Variance boundaries for normal distribution and weight for distance cost function for
        Best: (0.005, 0.85, 0.25) for generated | (0.005, 0.85, 4.0) to reduce false-positive results for recoded.
        
        PROBABILITY_PARAMS (tuple): A tuple specifying
                [0] variance_lower_limit (float): The lower bound for variance in the normal distribution.
                [1] variance_upper_limit (float): The upper bound for variance in the normal distribution.
                [2] omega (float): A variable > 1 used in the distance cost function to adjust probabilities. 
        """
        PROBABILITY_PARAMS = (0.005, 0.85, 4.0)  # (MIN_VAR, MAX_VAR, OMEGA)

        """
        Emitter uses actions from database and standard deviation of noise to be added.
        DATA_EMITTER_PARAMS (tuple):
                [0] Boolean flag to enable or disable the use of the database.
                [1] Standard deviation of noise to be added
                [2] Start time (at beginning of hand wrist recording)
                [3] End time (at end of hand wrist recording)
                [4] Time step (17 ~ 60hz, 100 = 10hz)
                [5] Real time speed (0.001(fastest) < 0.1 (fast) < 1.0 (normal) < 10.0 (slow))
                [6] String identifier of tracked hand, relevant of the set of next goals
                [7] Boolean flag indicating assembly/disassembly
        """
        DATA_EMITTER_PARAMS = (
            use_db, 0.00, df_trajectories['time'].iloc[0], df_trajectories['time'].iloc[-1], 17, 0.001, hand,
            is_asemble)

        self.rt_result = rt_result
        self.data_queue = queue.Queue()
        self.data_emitter = DataEmitter(self.data_queue, df_trajectories, df_actions, DATA_EMITTER_PARAMS)
        self.controller = Controller(df_goals, use_db, NOISE_REDUCER_PARAMS, MODEL_PARAMS, PROBABILITY_PARAMS,
                                     ACTION_HANDLER_PARAMS)

    def run(self):

        producer_thread = threading.Thread(target=self.data_emitter.emit_data)
        producer_thread.daemon = True  # to close thread with sys.exit
        producer_thread.start()

        results = []
        while True:
            try:
                data = self.data_queue.get()
                if data == -1:  # stop when no more data
                    break

                """Note: The output uses only Python standard objects and no program-specific objects."""
                result = self.controller.process_data(data)

                if result is not None:
                    results.append(result)

                    if self.rt_result:
                        print_result(result, print_only_top3)

            except queue.Empty:
                print("wait for data...")
                time.sleep(0.2)

        # Thread returns ALL collected results after finishing. (for testing)
        return results


def print_result(r: dict, only_top3: bool = True) -> None:
    msg = f"Time: {r['time']} | Amount: {len(r['goals'])} | -:- | "

    if only_top3:
        # removed third element (distance) of tuple for better readability.
        top3_id_prob = [(tup[0], tup[1]) for tup in r['top_3']]
        msg += f"Top3 (ID->Prob): {top3_id_prob} | -:- | \t\t\t"
    else:
        msg += f"Uncat: {r['uncat_prob']} | Goals: {r['num_prob_pairs']} | -:- |   \t\t"

    if r['over_60_and_distance']:
        if r['over_60_and_distance'][0] == "U":
            msg += "Uncategorized"
        else:
            msg += (f"Target: ==> {r['over_60_and_distance'][0]} <== over 60% | "
                    f"distance: {int(r['over_60_and_distance'][2] * 100)}cm")

    print(msg)


def get_study_trajectories(test_id: str, is_assemble: bool, hand: str) -> str:
    if hand != 'left' and hand != 'right':
        raise ValueError("No valid hand checked to be tracked.")

    if is_assemble:
        return r'data/test_data_study/assemble_' + hand + '_hand/' + test_id + '_' + hand[0] + '.csv'
    else:
        return r'data/test_data_study/dismantle_' + hand + '_hand/' + test_id + '_' + hand[0] + '.csv'


def get_study_actions(test_id: str, is_assemble: bool) -> str:
    if is_assemble:
        return r'data/test_data_study/assemble_actions/' + test_id + '.csv'
    else:
        return r'data/test_data_study/dismantle_actions/' + test_id + '.csv'


def get_study_goals(test_id: str, is_assemble: bool) -> str:
    if is_assemble:
        return r'data/test_data_study/goals.csv'
    else:
        return r'data/test_data_study/dismantle_goals/' + test_id + '_g.csv'


if __name__ == "__main__":
    """
    General settings for STUDY DATA:
    use_study_data = True
    is_assemble     -> True if task is assembling structure, False if dismantling structure
    hand            -> "left" or "right" to choose which hand to track probability
    path_goals_other, path_trajectories_other   -> value does not matter
    
    General settings for OTHER DATA:
    use_study_data = False
    is_assemble, hand, test_id      -> Value does not matter
    path_trajectories       -> The path to csv with hand wrist positions over time with (time, x, y, z) as csv columns
    path_goals      -> The path to csv with goal positions -> (ID, x, y, z) as csv columns
    """

    # ALWAYS SET:
    use_study_data = False
    print_only_top3 = True  # True: print only top3 probabilities ||| False: print all goal probabilities

    # change only when using STUDY DATA:
    test_id_ = "41212_2_168"
    is_assemble_ = True
    hand_ = "right"

    # change only when using OTHER DATA:
    path_goals_other = r'data/test_data_recorded/recorded_goals/goal_config1.csv'
    path_trajectories_other = r'data/test_data_recorded/recorded_trajectories/configuration1/23_config1_all2.csv'

    if use_study_data:
        # Study data configuration
        path_trajectories_ = get_study_trajectories(test_id_, is_assemble_, hand_)
        path_actions_ = get_study_actions(test_id_, is_assemble_)  # -> (time,hand,action_id,possible_actions)
        path_goals_ = get_study_goals(test_id_, is_assemble_)
        use_database = True
    else:
        # Other data configurations
        path_goals_ = path_goals_other
        path_trajectories_ = path_trajectories_other
        path_actions_ = r'data/action_empty.csv'
        use_database = False

    main = Main(path_goals_, path_trajectories_, path_actions_, True, use_database, is_assemble_, hand_)
    main.run()
