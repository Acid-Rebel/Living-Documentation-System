from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, code: str):
        """Return raw AST from source code."""
        pass
    @abstractmethod
    def normalize(self, raw_ast):
        """convert raw AST to unified AST format."""
        pass