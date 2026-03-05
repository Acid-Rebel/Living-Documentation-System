import os
import pytest
from living_docs_engine.nlp_summarizer.summarizer import FileSummarizer
from living_docs_engine.semantic_insights.python.summarizer_analyzer import PythonSummarizerAnalyzer
from code_parser.ast_schema import ASTNode

@pytest.fixture
def summarizer():
    return FileSummarizer()

@pytest.fixture
def analyzer():
    return PythonSummarizerAnalyzer()

def test_file_summarizer_basic(summarizer):
    code = """
\"\"\"
Module docstring.
\"\"\"
class MyClass:
    \"\"\"Class docstring.\"\"\"
    def my_method(self):
        \"\"\"Method docstring.\"\"\"
        pass

def my_function():
    \"\"\"Function docstring.\"\"\"
    pass
"""
    summary = summarizer.summarize_file(code)
    assert "**File Overview**: Module docstring." in summary
    assert "`class MyClass`: Class docstring." in summary
    assert "`my_function`: Function docstring." in summary

def test_summarizer_analyzer(analyzer, tmp_path):
    code = "def test():\n    \"\"\"A simple test.\"\"\"\n    pass"
    file_path = tmp_path / "test_file.py"
    file_path.write_text(code)
    
    ast_root = ASTNode(node_type="Module", language="python") # Dummy AST
    
    results = analyzer.analyze(ast_root, str(file_path))
    
    assert len(results) == 1
    assert "test`: A simple test." in results[0].content
    assert results[0].language == "python"
    assert results[0].file_path == str(file_path)

def test_invalid_syntax(summarizer):
    code = "invalid syntax ["
    summary = summarizer.summarize_file(code)
    assert "Could not parse" in summary
