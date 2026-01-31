from .base import BaseParser
from typing import Dict, Any
import os

class GenericParser(BaseParser):
    def detect(self) -> bool:
        return True  # Always fallback

    def parse(self) -> Dict[str, Any]:
        return {
            "name": os.path.basename(os.path.abspath(self.project_root)),
            "language": "unknown",
            "dependencies": [],
            "scripts": {}
        }
