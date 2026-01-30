import ast

from code_parser.normalizers.python_normalizer import normalize_python_ast
from code_parser.parsers.base_parser import BaseParser

class PythonParser(BaseParser):
    def parse(self, source_code: str):
        return ast.parse(source_code)

    def normalize(self, raw_ast):
        return normalize_python_ast(raw_ast)
