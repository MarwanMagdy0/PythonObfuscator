# package/module1.py

class MyClass1:
    name : str
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"
