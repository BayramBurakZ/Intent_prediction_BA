import logging
import os

from colorama import Fore, Style

from main import Main


class TestIntentionRecognition:
    """
    A class responsible for testing predefined goals and their corresponding trajectories. The results of these tests
    are stored in a specified log folder.
    """

    def __init__(self, goals_folder, trajectories_folder, logs_folder):
        """
        Parameters:
            goals_folder (str): Path to the folder containing the goal files to be tested.
            trajectories_folder (str): Path to the folder containing the trajectory files associated with the goals.
            logs_folder (str): Path to the folder where the test results will be stored as logs.
        """
        self.goals_folder = goals_folder
        self.trajectories_folder = trajectories_folder
        self.logs_folder = logs_folder
        self.logger = None

    def find_trajectories_for_goal(self, goal_prefix):
        """
        Finds and returns a list of file paths for trajectories associated with a specific goal.

        Parameters:
            goal_prefix (str): The prefix used to identify trajectories related to a specific goal.

        Returns:
            list: A list of file paths for the trajectories that match the given goal prefix.
         """
        trajectory_files = []
        for file_name in os.listdir(self.trajectories_folder):
            if file_name.startswith(goal_prefix):
                file_path = os.path.join(self.trajectories_folder, file_name)
                trajectory_files.append(file_path)

        return trajectory_files

    def run_test(self):
        """ Executes tests for each goal and its associated trajectories. """

        # Iterate through all goals in the goals folder
        for goal_file in os.listdir(self.goals_folder):
            goal_prefix = os.path.splitext(goal_file)[0]  # file name without extension
            goal_path = os.path.join(self.goals_folder, goal_file)
            trajectories = self.find_trajectories_for_goal(goal_prefix)  # all corresponding trajectories

            if trajectories:
                # Set up a log file for recording results for this goal
                log_file = os.path.join(self.logs_folder, f"{goal_prefix}_results.log")
                self.setup_logging(log_file)

                # Iterate through each trajectory and test it against the goal
                for trajectory_path in trajectories:
                    self.run_individual_test(goal_path, trajectory_path)
            else:
                print(f"No trajectories found for goal {goal_file}")

    def run_individual_test(self, goal_path, trajectory_path):
        """
        Executes a test for a given goal and trajectory.

        Parameters:
            goal_path (str): The file path to the goal to be tested.
            trajectory_path (str): The file path to the trajectory corresponding to the goal.
        """
        main_instance = Main(goal_path, trajectory_path)
        processed_data = main_instance.run()

        # Extract test ID from trajectory file name
        test_id = get_filename_without_extension(trajectory_path)

        # Extract target ID from test id
        target_index = int(test_id.split('_')[2]) - 1

        self.evaluate_results(processed_data, target_index, test_id)

    def evaluate_results(self, results, target_index, test_id):
        """
        Evaluates the results of a test based on a given goal and its corresponding trajectory.

        Parameters:
            results (list): A list containing the output data from the test. time, ids, probabilities, samples, distances, angles, uncategorized
                [0] Timestamp
                [1] ID's of goals
                [2] Probabilities of goals
                [3] Sample sizes of goals
                [4] Distance from each goal to observed hand wrist
                [5] Angle of each predicted goal trajectory
                [6] Probability of uncategorized goal
                [7] (not used) actions from observed hand and other possible actions as list of tuples (action, ID)
            target_index (int): The index indicating the specific target that is being reached.
            test_id (str): A unique identifier for the test, derived from the file name of the trajectory.
        """
        timestamps, probabilities_target, distances, uncategorized = [], [], [], []
        goal_ids, probabilities_other, sample_sizes = [], [], []

        for r in results:
            # NOTE this is after changing output into dict. Following Lists have been updated accordingly.
            goal_ids.append([])
            probabilities_other.append([])
            sample_sizes.append([])
            distances.append([])

            # Unpack the results
            timestamps.append(r["time"])
            uncategorized.append(r["uncat_prob"])

            for key, data in r["goals"].items():
                goal_ids[-1].append(key)

                if key != target_index + 1:
                    probabilities_other[-1].append(data["probability"])
                else:
                    probabilities_target.append(data["probability"])

                sample_sizes[-1].append(data["sample_quantity"])
                distances[-1].append(data["distance"])

        # setup passing criteria for test results
        highest_probability = max(probabilities_target, default=0.0)  # highest probability of target
        prob_60_reached = False  # target reached 60% probability
        distance_60 = sample_size_60 = time_60 = None  # distance, sample size and timestamp at 60% probability

        target_counter = other_counter = 0
        for i, prob in enumerate(probabilities_target):
            # check for each measurement if the target or another goal had the highest probability
            if (probabilities_other[i] and max(probabilities_other[i]) > prob) or uncategorized[i] > prob:
                other_counter += 1
            else:
                target_counter += 1

            # passing conditions. Save data at first time reaching 60% with sample size greater then 9
            if prob >= 60.0 and not prob_60_reached and sample_sizes[i][target_index] > 9:
                prob_60_reached = True
                distance_60 = distances[i][target_index]
                sample_size_60 = sample_sizes[i][target_index]
                time_60 = timestamps[i]

        # Determine status and color
        status, color = determine_status(prob_60_reached, distance_60, target_counter, other_counter)

        # Log the result
        self.log_result(test_id, highest_probability, time_60, sample_size_60, distance_60, status, color)

    def log_result(self, trajectory_file, highest_probability, time_60, sample_size_60, distance_60, status, color):
        """
        Logs and prints the results of a test, including relevant metrics and status.

        Parameters:
            trajectory_file (str): The name or path of the trajectory file being logged.
            highest_probability (float): The highest probability observed during the test.
            time_60 (float): The timestamp corresponding to the 60% threshold.
            sample_size_60 (int): The sample size at the 60% threshold.
            distance_60 (float): The distance measured at the 60% threshold.
            status (str): The status of the test ('Success','Pass1', 'Pass2, 'Failure').
            color (str): The color code used to print the message to the console.
        """
        log_message = (
            f"Result: {status} | Test_ID: {trajectory_file} | "
            f"Highest Probability: {highest_probability} | "
            f"[Timestamp/sample/distance] at 60% = [{time_60}/{sample_size_60}/{distance_60}]"
        )
        self.logger.info(log_message)
        print(color + log_message + Style.RESET_ALL)

    def setup_logging(self, log_file):
        """
        Configures logging for the test results, ensuring logs are recorded in a specified file.

        Parameters:
            log_file (str): The file path where the log entries will be recorded.
        """
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()  # prevent duplicate logging

        file_handler = logging.FileHandler(log_file, mode='w')  # overwrite existing logs
        formatter = logging.Formatter('%(message)s')  # only message display
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)


def get_filename_without_extension(path):
    return os.path.splitext(os.path.basename(path))[0]


def determine_status(prob_60_reached, distance_60, target_counter, other_counter, distance_limit=0.0):
    """
    Determine the status and color based on the following criteria:
        - "Success" (Green): 60% threshold reached, above distance limit, and overall preferred target.
        - "Pass1" (Yellow): 60% threshold reached, above distance limit, but not overall preferred target.
        - "Pass2" (Blue): 60% threshold not reached or under distance limit, but overall preferred target.
        - "Failure" (Red): 60% threshold not reached or under distance limit, and not overall preferred target.
        NOTE: At least 3 consecutive samples must meet these criteria

    Parameters:
        prob_60_reached (bool): Indicates whether the 60% probability threshold was reached.
        distance_60 (float): The distance when the 60% probability was reached.
        target_counter (int): The amount of times the target was preferred.
        other_counter (int): The amount of times another option was preferred.
        distance_limit (float): The minimum distance limit.

    Returns:
        tuple: A tuple containing the determined status (str) and corresponding color (str).
    """

    if prob_60_reached and distance_60 >= distance_limit:
        if target_counter >= other_counter:
            return "Success", Fore.GREEN
        else:
            return "Pass1", Fore.YELLOW
    else:
        if target_counter >= other_counter:
            return "Pass2", Fore.BLUE
        else:
            return "Failure", Fore.RED


if __name__ == "__main__":
    goals_folder = r'../data/test_data_generated/test_goal'
    trajectories_folder = r'../data/test_data_generated/test_trajectory'
    logs_folder = r'../data/test_data_generated/result_g'

    test = TestIntentionRecognition(goals_folder, trajectories_folder, logs_folder)
    test.run_test()
