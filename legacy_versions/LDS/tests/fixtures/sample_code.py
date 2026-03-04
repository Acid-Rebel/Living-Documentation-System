
# Sample code strings for testing

SIMPLE_CODE = """
import os

def hello():
    print("Hello, world!")
"""

COMPLEX_CODE = """
import ast
from typing import List

class Processor:
    \"\"\"
    A class that processes things.
    \"\"\"
    def __init__(self, data: List[int]):
        self.data = data

    def process(self):
        \"\"\"
        Process the data.
        \"\"\"
        return [x * 2 for x in self.data]

def helper_func():
    \"\"\"
    A helper function.
    \"\"\"
    pass
"""

SYNTAX_ERROR_CODE = """
def broken_function(
    print("This is a syntax error")
"""

EMPTY_CODE = ""
