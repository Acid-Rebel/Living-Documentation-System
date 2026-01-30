from typing import Dict, Iterable, List, Type, TypeVar

from code_parser.ast_schema import ASTNode

from semantic_extractor.base_analyzer import BaseAnalyzer
from semantic_extractor.java.call_analyzer import JavaCallAnalyzer
from semantic_extractor.java.import_analyzer import JavaImportAnalyzer
from semantic_extractor.java.symbol_analyzer import JavaSymbolAnalyzer
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol

T = TypeVar("T")
from semantic_extractor.python.call_analyzer import PythonCallAnalyzer
from semantic_extractor.python.import_analyzer import PythonImportAnalyzer
from semantic_extractor.python.symbol_analyzer import PythonSymbolAnalyzer


class AnalyzerManager:
    def __init__(self) -> None:
        self._symbol_analyzers: Dict[str, List[BaseAnalyzer]] = {
            "python": [PythonSymbolAnalyzer()],
            "java": [JavaSymbolAnalyzer()],
        }
        self._relation_analyzers: Dict[str, List[BaseAnalyzer]] = {
            "python": [PythonImportAnalyzer(), PythonCallAnalyzer()],
            "java": [JavaImportAnalyzer(), JavaCallAnalyzer()],
        }

    def analyze(self, ast_root: ASTNode, file_path: str, language: str) -> Dict[str, List[object]]:
        language_key = language.lower()
        if language_key not in self._symbol_analyzers or language_key not in self._relation_analyzers:
            raise ValueError(f"Unsupported language for semantic analysis: {language}")

        symbols: List[Symbol] = []
        relations: List[Relation] = []

        for analyzer in self._symbol_analyzers[language_key]:
            artifacts = analyzer.analyze(ast_root, file_path)
            symbols.extend(self._filter_type(artifacts, Symbol))

        for analyzer in self._relation_analyzers[language_key]:
            artifacts = analyzer.analyze(ast_root, file_path)
            relations.extend(self._filter_type(artifacts, Relation))

        return {
            "symbols": symbols,
            "relations": relations,
        }

    def _filter_type(self, artifacts: Iterable[object], expected_type: Type[T]) -> List[T]:
        return [artifact for artifact in artifacts if isinstance(artifact, expected_type)]
