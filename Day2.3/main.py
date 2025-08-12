import csv

with open('School.csv', 'w+', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['School', 'Name'])
    writer.writerow(['Springfield High', 'Alice'])
    writer.writerow(['Greenwood College', 'Bob'])
    writer.writerow(['Riverdale Academy', 'Charlie'])

    # Move pointer to the start to read
    file.seek(0)

    reader = csv.reader(file)
    print('School and Name:')
    for row in reader:
        print(row)
