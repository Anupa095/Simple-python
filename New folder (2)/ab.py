def get_numbers():
    try:
        num1 = int(input("Enter the first number: "))
        num2 = int(input("Enter the second number: "))
        return num1, num2
    except ValueError:
        print("Invalid input! Please enter integers only.")
        return get_numbers()  # Try again
