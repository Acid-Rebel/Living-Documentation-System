from code_parser.parsers.python_parser import PythonParser
from code_parser.parsers.java_parser import JavaParser


def get_parser(language: str):
    if language == "python":
        return PythonParser()
    elif language == "java":
        return JavaParser()
    else:
        raise ValueError(f"No parser available for language: {language}")
