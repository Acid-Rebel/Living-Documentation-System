from abc import ABC, abstractmethod
from typing import Dict, Any, List
import os

class BaseParser(ABC):
    def __init__(self, project_root: str):
        self.project_root = project_root

    @abstractmethod
    def detect(self) -> bool:
        """Returns True if this parser applies to the current project."""
        pass

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """Extracts metadata from project files."""
        pass

    def read_file(self, filename: str) -> str:
        path = os.path.join(self.project_root, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
