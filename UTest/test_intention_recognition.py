import os
import logging
from main import Main
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)  # Initialize colorama for colored output


class TestIntentionRecognition:
    def __init__(self, goals_folder, trajectories_folder, logs_folder):
        self.goals_folder = goals_folder
        self.trajectories_folder = trajectories_folder
        self.logs_folder = logs_folder
        self.logger = None

    def find_trajectories_for_goal(self, goal_prefix):
        trajectories = []
        for file_name in os.listdir(self.trajectories_folder):
            if file_name.startswith(goal_prefix):
                trajectories.append(os.path.join(self.trajectories_folder, file_name))
        return trajectories

    def run_test(self):
        for goal_file in os.listdir(self.goals_folder):
            goal_prefix = os.path.splitext(goal_file)[0]  # Get the goal prefix
            goal_path = os.path.join(self.goals_folder, goal_file).replace("\\", "/")
            trajectories = self.find_trajectories_for_goal(goal_prefix)

            if trajectories:
                log_file = os.path.join(self.logs_folder, f"{goal_prefix}_results.log")
                self.setup_logging(log_file)
                for trajectory_path in trajectories:
                    self.run_individual_test(goal_path, trajectory_path.replace("\\", "/"))
            else:
                print(f"No trajectories found for goal {goal_file}")

    def run_individual_test(self, goal_path, trajectory_path):
        main_instance = Main(goal_path, trajectory_path)
        processed_data = main_instance.run()
        test_id = get_filename_without_extension(trajectory_path)
        target_index = int(test_id.split('_')[2]) - 1
        self.evaluate_results(processed_data, target_index, test_id)

    def evaluate_results(self, results, target, trajectory_file):
        timestamps, probabilities_target, distances, uncategorized = [], [], [], []
        goal_ids, probabilities_other, sample_sizes = [], [], []

        for result in results:
            timestamps.append(result[0])
            goal_ids.append(result[1])
            probabilities_target.append(result[2].pop(target))
            probabilities_other.append(result[2])
            sample_sizes.append(result[3])
            distances.append(result[4])
            uncategorized.append(result[6])

        highest_probability, prob_60_reached = 0.0, False
        distance_60, sample_size_60, time_60 = None, None, None
        target_counter, other_counter = 0, 0

        for i, prob in enumerate(probabilities_target):
            if (probabilities_other[i] and max(probabilities_other[i]) > prob) or uncategorized[i] > prob:
                other_counter += 1
            else:
                target_counter += 1

            if prob >= 60.0 and not prob_60_reached and sample_sizes[i][target] >= 3:
                prob_60_reached = True
                distance_60 = distances[i][target]
                sample_size_60 = sample_sizes[i][target]
                time_60 = timestamps[i]

            if prob > highest_probability:
                highest_probability = prob

        distance_limit = 0.2

        if prob_60_reached and distance_60 >= distance_limit:
            status, color = ("Success", Fore.GREEN) if target_counter >= other_counter else ("Pass", Fore.YELLOW)
        else:
            status, color = "Failed", Fore.RED

        self.log_result(trajectory_file, highest_probability, time_60, sample_size_60, distance_60, status, color)

    def log_result(self, trajectory_file, highest_probability, time_60, sample_size_60, distance_60, status, color):
        log_message = (
            f"Result: {status} | Test_ID: {trajectory_file} | "
            f"Highest Probability: {highest_probability} | "
            f"[Timestamp/sample/distance] at 60% = [{time_60}/{sample_size_60}/{distance_60}]"
        )
        self.logger.info(log_message)
        print(color + log_message + Style.RESET_ALL)

    def setup_logging(self, log_file):
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(logging.INFO)

        # Clear previous handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        file_handler = logging.FileHandler(log_file, mode='w')
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)


def get_filename_without_extension(path):
    return os.path.splitext(os.path.basename(path))[0]


if __name__ == "__main__":
    # Specify the directories for goals, trajectories, and test_logs
    goals_folder = r'../data/test_data/test_goal'
    trajectories_folder = r'../data/test_data/test_trajectory'
    logs_folder = r'../data/test_data/test_logs'

    test = TestIntentionRecognition(goals_folder, trajectories_folder, logs_folder)
    test.run_test()
