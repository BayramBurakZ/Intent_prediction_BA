import pandas as pd
import os

# Directories
input_directory = r'../data/test_data_study/test_action'
right_output_directory = "../data/test_data_study/test_right_hand"
left_output_directory = "../data/test_data_study/test_left_hand"

# Function to process files for a given participant_id, trial, and trajectory_id
def process_files(participant_id, trial, trajectory_id):

    prefix = f"{participant_id}_{trial}"
    all_files = os.listdir(input_directory) # Get all files in the directory

    # Filter files that start with the given prefix
    files = [f for f in all_files if f.startswith(prefix) and f.endswith('.csv')]

    # Extract time intervals from files
    intervals = {}
    for file in files:
        df = pd.read_csv(os.path.join(input_directory, file))
        start_time = df['time'].iloc[0]
        end_time = df['time'].iloc[-1]
        intervals[file] = (start_time, end_time)

    # Load the right and left hand wrist position data
    right_data_path = f'../data/study/right_hand/right_{trajectory_id}.csv'
    left_data_path = f'../data/study/left_hand/left_{trajectory_id}.csv'
    right_data = pd.read_csv(right_data_path)
    left_data = pd.read_csv(left_data_path)

    # Split the additional CSV based on intervals
    for file_name, (start_time, end_time) in intervals.items():
        # Extract the base name without the extension
        base_name = os.path.splitext(file_name)[0]

        # Filter data for the right and left hand data based on time intervals
        right_subset = right_data[(right_data['time'] >= start_time) & (right_data['time'] <= end_time)]
        left_subset = left_data[(left_data['time'] >= start_time) & (left_data['time'] <= end_time)]

        right_file_name = f"{base_name}_r.csv"
        left_file_name = f"{base_name}_l.csv"

        # Save the filtered data to the respective output directories
        right_subset.to_csv(os.path.join(right_output_directory, right_file_name), index=False)
        left_subset.to_csv(os.path.join(left_output_directory, left_file_name), index=False)

        print(right_file_name, left_file_name, "done!")

# List of participant_id, trial, and trajectory_id tuples
participants_trials_trajectories = [
    (31612, 0, 9),
    (31812, 1, 10),
    (33112, 1, 11),
    (41212, 2, 12),
    (50510, 0, 13),
    (51814, 1, 14),
    (52514, 0, 15),
    (53112, 2, 16)
]

# Process files for each participant_id, trial, and trajectory_id
for participant_id, trial, trajectory_id in participants_trials_trajectories:
    process_files(participant_id, trial, trajectory_id)
