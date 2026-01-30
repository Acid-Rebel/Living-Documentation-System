import javalang
from code_parser.parsers.base_parser import BaseParser
from code_parser.normalizers.java_normalizer import normalize_java_ast

class JavaParser(BaseParser):

    def parse(self, source_code: str):
        return javalang.parse.parse(source_code)

    def normalize(self, raw_ast):
        return normalize_java_ast(raw_ast)