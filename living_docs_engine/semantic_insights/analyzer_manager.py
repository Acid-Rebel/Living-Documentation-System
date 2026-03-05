from typing import Dict, Iterable, List, TypeVar, Any

from code_parser.ast_schema import ASTNode

from semantic_insights.base_analyzer import BaseAnalyzer
from semantic_insights.java.call_analyzer import JavaCallAnalyzer
from semantic_insights.java.import_analyzer import JavaImportAnalyzer
from semantic_insights.java.symbol_analyzer import JavaSymbolAnalyzer
from semantic_insights.models.relation import Relation
from semantic_insights.models.symbol import Symbol
from semantic_insights.models.summary import Summary
from semantic_insights.python.call_analyzer import PythonCallAnalyzer
from semantic_insights.python.import_analyzer import PythonImportAnalyzer
from semantic_insights.python.symbol_analyzer import PythonSymbolAnalyzer
from semantic_insights.python.summarizer_analyzer import PythonSummarizerAnalyzer

T = TypeVar("T")


class AnalyzerManager:
    def __init__(self) -> None:
        self._symbol_analyzers: Dict[str, List[BaseAnalyzer]] = {
            "python": [PythonSymbolAnalyzer(), PythonSummarizerAnalyzer()],
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

        symbols: List[object] = []
        relations: List[Relation] = []

        for analyzer in self._symbol_analyzers[language_key]:
            artifacts = analyzer.analyze(ast_root, file_path)
            symbols.extend(self._filter_type(artifacts, (Symbol, Summary)))

        for analyzer in self._relation_analyzers[language_key]:
            artifacts = analyzer.analyze(ast_root, file_path)
            relations.extend(self._filter_type(artifacts, Relation))

        return {
            "symbols": symbols,
            "relations": relations,
        }

    def _filter_type(self, artifacts: Iterable[object], expected_type: Any) -> List[Any]:
        return [artifact for artifact in artifacts if isinstance(artifact, expected_type)]
