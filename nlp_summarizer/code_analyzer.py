import ast

class CodeAnalyzer:
    """
    Analyzes a single Python file to extract its structure and context.
    """

    def __init__(self):
        pass

    def get_file_structure(self, code):
        """
        Parses code into a high-level structure dictionary:
        {
            'docstring': 'Module docstring',
            'classes': [
                {
                    'name': 'ClassName',
                    'docstring': '...',
                    'methods': [{'name': 'm', 'docstring': '...'}],
                    'bases': ['Base']
                }
            ],
            'functions': [
                {'name': 'func', 'docstring': '...'}
            ],
            'imports': ['import os', ...]
        }
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None

        structure = {
            'docstring': ast.get_docstring(tree),
            'classes': [],
            'functions': [],
            'imports': []
        }

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = []
                for n in node.body:
                    if isinstance(n, ast.FunctionDef):
                        methods.append({
                            'name': n.name,
                            'docstring': ast.get_docstring(n)
                        })
                
                bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
                structure['classes'].append({
                    'name': node.name,
                    'methods': methods,
                    'bases': bases,
                    'docstring': ast.get_docstring(node)
                })

            elif isinstance(node, ast.FunctionDef):
                structure['functions'].append({
                    'name': node.name,
                    'docstring': ast.get_docstring(node)
                })

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    structure['imports'].append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    structure['imports'].append(f"from {module} import {alias.name}")
        
        return structure
