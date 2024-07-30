import os
import pandas as pd
from sqlalchemy import create_engine

# Database path
path_db = r'../data/db_study/database.db'
engine = create_engine(f"sqlite:///{path_db}")
output_path = r'../data/test_data_study/test_action'

# Fetch data from the database
query = "SELECT * FROM action_exec"
df = pd.read_sql(query, engine)

# Extract the first two numeric parts from `state_id`
df[['part1', 'part2']] = df['state_id'].str.extract(r'(\d+)_(\d+)')

# Combine the extracted parts with `run_id` to form `state_id_run_id`
df['state_id_run_id'] = df['part1'] + '_' + df['part2'] + '_' + df['run_id'].astype(str)

# Drop the temporary columns `part1` and `part2`
df.drop(columns=['part1', 'part2'], inplace=True)

# Define the aggregation function
def aggregate_other_actions(group):
    # Combine 'other_actions' into a single string, ignore NaN values, handle empty cases
    other_actions_combined = ','.join(group['other_actions'].dropna().astype(str))
    return pd.Series({
        'time': group['time'].iloc[0],
        'run_id': group['run_id'].iloc[0],
        'hand': group['hand'].iloc[0],
        'action_id': group['action_id'].iloc[0],
        'other_actions': other_actions_combined,
        'state_id_run_id': group['state_id_run_id'].iloc[0]
    })

# Group by `state_id_run_id`, `action_id`, and `time` and apply aggregation
grouped_df = df.groupby(['state_id_run_id', 'action_id', 'time'], group_keys=False).apply(aggregate_other_actions).reset_index(drop=True)

# Sort by `time`
grouped_df.sort_values(by='time', inplace=True)

# Save to CSV by `state_id_run_id`
for state_id_run_id, group in grouped_df.groupby('state_id_run_id'):
    output_filename = os.path.join(output_path, f'{state_id_run_id}.csv')
    group.to_csv(output_filename, index=False)
    print(f'Created CSV file: {output_filename}')  # Print message for each file created
