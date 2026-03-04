from code_parser.language_detector import detect_language
from code_parser.parsers.python_parser import PythonParser
from code_parser.parsers.java_parser import JavaParser

PARSERS = {
    "python": PythonParser(),
    "java": JavaParser(),
}

def parse_source_file(file_path: str, source_code: str):
    language = detect_language(file_path)
    if not language:
        return None

    parser = PARSERS.get(language)
    if not parser:
        return None

    raw_ast = parser.parse(source_code)
    return parser.normalize(raw_ast)


def get_parser(language: str):
    """
    Returns the parser instance for the given language.
    """
    parser = PARSERS.get(language)
    if not parser:
        raise ValueError(f"No parser available for language: {language}")
    return parser