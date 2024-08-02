import os

import pandas as pd
from sqlalchemy import create_engine

# Database path
path_db = r'../data/db_study/database.db'
engine = create_engine(f"sqlite:///{path_db}")
output_path = r'../data/test_data_study/test_action'

# Fetch data from the database
query = "SELECT * FROM possible_actions"
df = pd.read_sql(query, engine)


def filter_and_save(df, participant_id, trial, output_path):

    # Filter the dataframe based on participant_id and trial
    filtered_df = df[(df['participant_id'] == participant_id) & (df['trial'] == trial)]

    # Get unique run_ids from the filtered dataframe
    run_ids = filtered_df['run_id'].unique()

    # Loop through each run_id and save the corresponding rows to a CSV file
    for run_id in run_ids:
        run_df = filtered_df[filtered_df['run_id'] == run_id]
        file_name = f"{participant_id}_{trial}_{run_id}.csv"
        file_path = os.path.join(output_path, file_name)
        run_df.to_csv(file_path, index=False)
        print(f"Saved: {file_path}")


participants_trials = [
    (31612, 0),
    (31812, 1),
    (33112, 1),
    (41212, 2),
    (50510, 0),
    (51814, 1),
    (52514, 0),
    (53112, 2)
]

for participant_id, trial in participants_trials:
    filter_and_save(df, participant_id, trial, output_path)
