import pandas as pd

# Create a small CSV
with open('grades.csv', 'w') as f:
    f.write("Name,Grade\nAlice,85\nBob,92\nCharlie,60\n")

# Now read it
df = pd.read_csv('grades.csv')

print(df.head())
print(df.describe())
