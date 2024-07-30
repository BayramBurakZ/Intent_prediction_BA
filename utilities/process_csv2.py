import pandas as pd
import os

# Directory and prefix
input_directory = r'../data/test_data_study/test_action'
prefix = "53112_2"

# Output directories
right_output_directory = "../data/test_data_study/test_right_hand"
left_output_directory = "../data/test_data_study/test_left_hand"

# Get all files in the directory
all_files = os.listdir(input_directory)

# Filter files that start with the given prefix
files = [f for f in all_files if f.startswith(prefix) and f.endswith('.csv')]

# Extract time intervals from files
intervals = {}
for file in files:
    df = pd.read_csv(os.path.join(input_directory, file))
    start_time = df['time'].iloc[0]
    end_time = df['time'].iloc[-1]
    intervals[file] = (start_time, end_time)

# Load the right and left hand data
right_data = pd.read_csv(r'../data/study/right_hand/right_16.csv')
left_data = pd.read_csv(r'../data/study/left_hand/left_16.csv')

# Split the additional CSV based on intervals
for file_name, (start_time, end_time) in intervals.items():
    # Extract the base name without the extension
    base_name = os.path.splitext(file_name)[0]

    # Filter data for the right and left hand data based on time intervals
    right_subset = right_data[(right_data['time'] >= start_time) & (right_data['time'] <= end_time)]
    left_subset = left_data[(left_data['time'] >= start_time) & (left_data['time'] <= end_time)]

    # Create the new filenames
    right_file_name = f"{base_name}_r.csv"
    left_file_name = f"{base_name}_l.csv"

    # Save the filtered data to the respective output directories
    right_subset.to_csv(os.path.join(right_output_directory, right_file_name), index=False)
    left_subset.to_csv(os.path.join(left_output_directory, left_file_name), index=False)

    print(right_file_name, left_file_name, "done!")
