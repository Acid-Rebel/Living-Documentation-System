from language_detector import detect_language
from parsers.python_parser import PythonParser
from parsers.java_parser import JavaParser

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