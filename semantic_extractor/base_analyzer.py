from abc import ABC, abstractmethod
from typing import Iterable

from code_parser.ast_schema import ASTNode


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, ast_root: ASTNode, file_path: str) -> Iterable[object]:
        """Return semantic artifacts (symbols or relations)."""
        raise NotImplementedError
