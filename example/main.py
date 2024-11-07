# main.py

from package import MyClass1, my_function

def main():
    # Create an instance of MyClass1 and use its method
    my_object = MyClass1("John")
    print(my_object.greet())  # Output: Hello, John!
    
    # Use the function from module2
    result = my_function(10, 5)
    print(f"Sum: {result}")  # Output: Sum: 15

if __name__ == "__main__":
    main()
