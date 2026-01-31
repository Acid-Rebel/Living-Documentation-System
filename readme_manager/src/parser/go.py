from .base import BaseParser
from typing import Dict, Any
import os
import re

class GoParser(BaseParser):
    def detect(self) -> bool:
        return os.path.exists(os.path.join(self.project_root, "go.mod"))

    def parse(self) -> Dict[str, Any]:
        data = {
            "language": "Go",
            "frameworks": [],
            "dependencies": [],
            "scripts": {}
        }
        
        content = self.read_file("go.mod")
        if content:
            lines = content.splitlines()
            for line in lines:
                line = line.strip()
                if line.startswith("module"):
                    data["name"] = line.split(" ")[1]
                elif line.startswith("go"):
                    data["version"] = line.split(" ")[1]
        
        # Simplified dependency parsing
        # Real parsing would need to handle 'require' blocks
        
        if "gin" in content: data["frameworks"].append("Gin")
        if "echo" in content: data["frameworks"].append("Echo")
        if "fiber" in content: data["frameworks"].append("Fiber")
        if "cobra" in content: data["frameworks"].append("Cobra")

        return data
