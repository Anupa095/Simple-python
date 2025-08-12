# Write to the file
with open('example.txt', 'w') as file:
    file.write('Hello, world!\nThis is a file I/O example in Python.')

# Read from the file
with open('example.txt', 'r') as file:
    content = file.read()
    print('File contents:')
    print(content)