import pandas as pd

# Dataframe for goals
path = r'../data/goals\goals.csv'
df = pd.read_csv(path)

df['active'] = [True] * 32
df['sample'] = [0] * 32
df['probability'] = [0] * 32

print(df)

