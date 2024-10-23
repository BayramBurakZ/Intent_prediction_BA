This program processes target positions and wrist trajectories over time to predict which target the hand is most likely to move toward. Based on the positions of the hand and the goals, it calculates the probabilities of each goal being reached by the hand over time, helping to identify the most probable target.

Execution Instructions for Code (Python 3.12)

1. Using Study Data (in main.py):
- Set use_study_data to True.
- Choose the test ID you want to run (e.g., test_id_ = "41212_2_168", which corresponds to the CSV file names located in the action folder under /data/test_data_study).
- Set is_assemble:
  - True for assembling tasks.
  - False for dismantling tasks.
- Set hand_:
  - "right" to predict right-hand trajectories.
  - "left" for left-hand trajectories.

2. Using Other Data (in main.py):
- Set use_study_data to False.
- Specify the CSV file location for the goals using path_goals_other.
- Specify the CSV file location for the trajectory using path_trajectories_other.
- Recorded trajectories can be found in /data/test_data_recorded/recorded_trajectories with corresponding goal positions in /data/test_data_recorded/recorded_goals.

3. Using Generated Data (in /UTest/test_prediction_model_ip.py):
- Run test_prediction_model_ip.py.
- Results will be stored in /data/test_data_generated/result_g.
- To summarize the results, run /utilities/LogResultSummarizer.py. The summary will be saved in /data/test_data_generated/summary_results.log.

General Settings:
- Set print_only_top3 to True if you want only the top 3 highest probabilities for goals to be printed. Set it to False to print all goals with their probabilities.
- Parameters for generated trajectories are different from recorded trajectories and can be modified in main.py.

Data Format:
- Trajectory CSV columns: time, x, y, z
- Goal CSV columns: ID, x, y, z
