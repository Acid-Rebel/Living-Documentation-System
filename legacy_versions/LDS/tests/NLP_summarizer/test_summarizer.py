
import pytest
from nlp_summarizer.summarizer import FileSummarizer

def test_summarize_file_simple(summarizer, simple_code):
    """Test summarization of simple code."""
    summary = summarizer.summarize_file(simple_code)
    assert "**File Overview**: This module provides utilities and classes." in summary
    assert "**Global Functions:**" in summary
    assert "- `hello`: Utility function." in summary

def test_summarize_file_complex(summarizer, complex_code):
    """Test summarization of complex code."""
    summary = summarizer.summarize_file(complex_code)
    assert "**File Overview**: This module provides utilities and classes." in summary
    assert "**Key Classes:**" in summary
    assert "- `class Processor`:" in summary
    assert "**Global Functions:**" in summary
    assert "- `helper_func`: A helper function." in summary

def test_summarize_file_syntax_error(summarizer, syntax_error_code):
    """Test summarization with syntax error."""
    summary = summarizer.summarize_file(syntax_error_code)
    assert "Could not parse file structure (Syntax Error)." in summary

def test_format_docstring(summarizer):
    """Test docstring formatting."""
    docstring = "First line.\nSecond line."
    formatted = summarizer._format_docstring(docstring)
    assert formatted == "First line."

    assert summarizer._format_docstring(None) == ""
    assert summarizer._format_docstring("") == ""
