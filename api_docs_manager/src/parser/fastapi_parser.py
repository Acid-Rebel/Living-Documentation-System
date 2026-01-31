import os
import ast
from typing import List
from .base import BaseParser, Endpoint

class FastAPIParser(BaseParser):
    def parse(self, project_root: str) -> List[Endpoint]:
        endpoints = []
        for root, _, files in os.walk(project_root):
             for file in files:
                if file.endswith(".py"):
                    endpoints.extend(self._scan_file(os.path.join(root, file)))
        return endpoints

    def _scan_file(self, file_path: str) -> List[Endpoint]:
        found = []
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
                visitor = FastAPIVisitor(file_path)
                visitor.visit(tree)
                found.extend(visitor.endpoints)
            except Exception:
                pass
        return found

class FastAPIVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.endpoints = []
        self.file_path = file_path

    def visit_FunctionDef(self, node):
        # Check decorators for @app.get, @router.post, etc.
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                method = None
                
                # Handle @app.get(...)
                if isinstance(func, ast.Attribute):
                    if func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                        method = func.attr.upper()
                
                if method:
                    # Extract path from arguments
                    path = "/"
                    if dec.args and isinstance(dec.args[0], ast.Constant):
                         path = dec.args[0].value
                    
                    desc = ast.get_docstring(node) or "No description"
                    
                    self.endpoints.append(Endpoint(
                        method=method,
                        path=path,
                        description=desc,
                        source_file=self.file_path,
                        line_number=node.lineno
                    ))
        self.generic_visit(node)
