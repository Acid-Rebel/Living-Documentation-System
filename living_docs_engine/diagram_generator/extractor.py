import os
from typing import List, Dict

class CodeExtractor:
    """Extracts code files for diagram generation."""
    
    def __init__(self, include_extensions: List[str] = None, exclude_dirs: List[str] = None):
        self.include_extensions = include_extensions or ['.py', '.js', '.ts', '.java', '.cpp', '.cs']
        self.exclude_dirs = exclude_dirs or [
            '.git', '__pycache__', 'node_modules', 'venv', 'env', 
            '.venv', 'dist', 'build', '.idea', '.vscode'
        ]

    def extract_codebase(self, directory_path: str) -> Dict[str, str]:
        """
        Walks through the directory and extracts the content of relevant code files.
        Returns a dictionary mapping relative file paths to file contents.
        """
        extracted_files = {}
        directory_path = os.path.abspath(directory_path)

        for root, dirs, files in os.walk(directory_path):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs and not d.startswith('.')]

            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in self.include_extensions:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Optional: We could truncate or filter very large files here
                            extracted_files[rel_path] = content
                    except Exception as e:
                        print(f"Failed to read {file_path}: {e}")
                        
        return extracted_files

    def format_for_llm(self, extracted_files: Dict[str, str]) -> str:
        """
        Formats the dictionary of extracted files into a string suitable for an LLM prompt.
        """
        formatted = ""
        for path, content in extracted_files.items():
            formatted += f"\n--- File: {path} ---\n"
            formatted += f"```{self._get_lang(path)}\n{content}\n```\n"
        return formatted

    def _get_lang(self, path: str) -> str:
        ext = os.path.splitext(path)[1]
        mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust'
        }
        return mapping.get(ext, '')
