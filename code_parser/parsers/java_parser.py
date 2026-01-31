try:
    import javalang
    from ..normalizers.java_normalizer import normalize_java_ast
except ImportError:
    javalang = None
    normalize_java_ast = None

from .base_parser import BaseParser

class JavaParser(BaseParser):

    def parse(self, source_code: str):
        if not javalang:
            return None
        return javalang.parse.parse(source_code)

    def normalize(self, raw_ast):
        if not normalize_java_ast:
            return None
        return normalize_java_ast(raw_ast)