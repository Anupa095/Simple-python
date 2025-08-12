import csv

# Write to CSV
with open('grades.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Grade'])
    writer.writerow(['Alice', '85'])
    writer.writerow(['Bob', '92'])
    writer.writerow(['Charlie', '60'])

# Read from CSV
with open('grades.csv', 'r') as file:
    reader = csv.reader(file)
    print('Grades:')
    for row in reader:
        print(row)
