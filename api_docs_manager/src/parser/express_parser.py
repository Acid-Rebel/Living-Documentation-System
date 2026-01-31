import os
import re
from typing import List
from .base import BaseParser, Endpoint

class ExpressParser(BaseParser):
    def parse(self, project_root: str) -> List[Endpoint]:
        endpoints = []
        for root, _, files in os.walk(project_root):
             if "node_modules" in root: continue
             for file in files:
                if file.endswith(".js") or file.endswith(".ts"):
                    endpoints.extend(self._scan_file(os.path.join(root, file)))
        return endpoints

    def _scan_file(self, file_path: str) -> List[Endpoint]:
        found = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Regex for router.get('/path', ...) or app.post('/path', ...)
            # Matches: method, path
            pattern = r'(router|app)\.(get|post|put|delete|patch)\s*\(\s*[\'"`](.*?)[\'"`]'
            matches = re.finditer(pattern, content)
            
            for m in matches:
                method = m.group(2).upper()
                path = m.group(3)
                
                # Check for preceding JSDoc
                # This is a simplification; robust mapping requires AST or line tracking
                desc = "No description"
                
                found.append(Endpoint(
                    method=method,
                    path=path,
                    description=desc,
                    source_file=file_path
                ))
        return found
