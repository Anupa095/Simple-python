import pandas as pd
import matplotlib.pyplot as plt

# Create sample data (like grades.csv)
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Grade': [85, 92, 60, 75]
}
df = pd.DataFrame(data)

# Plot
plt.bar(df['Name'], df['Grade'], color='Gold')

# Add labels & title
plt.xlabel('Student Name')
plt.ylabel('Grade')
plt.title('Student Grades')
plt.ylim(0, 100)  # y-axis range
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show chart
plt.show()
