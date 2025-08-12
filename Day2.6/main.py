import csv

import matplotlib.pyplot as plt



# Step 1: Create CSV file

with open('fruits.csv', mode='w', newline='') as file:

    writer = csv.writer(file)

    writer.writerow(['Fruit', 'Number of People'])

    writer.writerow(['Apple', 30])

    writer.writerow(['Banana', 15])

    writer.writerow(['Cherry', 25])

    writer.writerow(['Date', 10])

    writer.writerow(['Grape', 20])



# Step 2: Read CSV file

fruits = []

numbers = []

with open('fruits.csv', mode='r') as file:

    reader = csv.reader(file)

    next(reader)  # Skip header

    for row in reader:

        fruits.append(row[0])

        numbers.append(int(row[1]))



# Step 3: Create Pie Chart

explode = [0.1 if fruit == "Apple" else 0 for fruit in fruits]  # Highlight Apple slice

plt.pie(numbers, labels=fruits, autopct='%1.1f%%', startangle=140, explode=explode)

plt.title("Favorite Fruits Distribution")

plt.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.



# Step 4: Show chart

plt.show()