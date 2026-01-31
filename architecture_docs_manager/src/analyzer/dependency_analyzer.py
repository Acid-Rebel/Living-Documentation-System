import os
import re
from typing import Dict, List, Set, Tuple

class DependencyAnalyzer:
    def __init__(self):
        pass

    def analyze(self, root_path: str) -> Dict[str, List[str]]:
        """
        Returns a simple adjacency list: { "file_path": ["imported_module", ...] }
        """
        graph = {}
        for root, dirs, files in os.walk(root_path):
             if "node_modules" in root or "__pycache__" in root: continue
             
             for file in files:
                 if file.endswith((".js", ".ts", ".py", ".java")):
                     full_path = os.path.join(root, file)
                     rel_path = os.path.relpath(full_path, root_path)
                     imports = self._extract_imports(full_path)
                     graph[rel_path] = imports
        return graph

    def _extract_imports(self, file_path: str) -> List[str]:
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if file_path.endswith(".py"):
                # import X, from X import Y
                matches = re.findall(r'^(?:from|import)\s+([\w\.]+)', content, re.MULTILINE)
                imports.extend(matches)
            elif file_path.endswith((".js", ".ts")):
                # import X from 'Y', require('Y')
                # Try to capture path
                matches_esm = re.findall(r'from\s+[\'"](.*?)[\'"]', content)
                matches_cjs = re.findall(r'require\s*\(\s*[\'"](.*?)[\'"]', content)
                imports.extend(matches_esm)
                imports.extend(matches_cjs)
                
        except Exception:
            pass
        return list(set(imports))
