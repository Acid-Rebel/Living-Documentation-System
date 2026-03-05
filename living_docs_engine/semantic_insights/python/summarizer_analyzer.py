from typing import List
import os

from code_parser.ast_schema import ASTNode
from semantic_insights.base_analyzer import BaseAnalyzer
from semantic_insights.models.summary import Summary
from nlp_summarizer.summarizer import FileSummarizer


class PythonSummarizerAnalyzer(BaseAnalyzer):
    """
    Analyzer that generates a natural language summary of a Python file.
    """

    def __init__(self):
        self.summarizer = FileSummarizer()

    def analyze(self, ast_root: ASTNode, file_path: str) -> List[Summary]:
        """
        Reads the file content and generates a summary artifact.
        """
        if not os.path.exists(file_path):
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception:
            return []

        summary_text = self.summarizer.summarize_file(code)
        
        return [
            Summary(
                content=summary_text,
                file_path=file_path,
                language="python"
            )
        ]
