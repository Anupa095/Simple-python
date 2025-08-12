from inputs import get_numbers
from calculator import add_numbers

while True:
    num1, num2 = get_numbers()
    add_numbers(num1, num2)

    again = input("Do you want to add more numbers? (yes/no): ").lower()
    if again != 'yes':
        print("Exiting program. Goodbye!")
        break
