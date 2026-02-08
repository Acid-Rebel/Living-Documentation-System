
import pytest
import sys
import os

# Ensure the nlp_summarizer module is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp_summarizer.code_analyzer import CodeAnalyzer
from nlp_summarizer.summarizer import FileSummarizer
from tests.fixtures import sample_code

@pytest.fixture
def analyzer():
    """Returns a CodeAnalyzer instance."""
    return CodeAnalyzer()

@pytest.fixture
def summarizer():
    """Returns a FileSummarizer instance."""
    return FileSummarizer()

@pytest.fixture
def simple_code():
    return sample_code.SIMPLE_CODE

@pytest.fixture
def complex_code():
    return sample_code.COMPLEX_CODE

@pytest.fixture
def syntax_error_code():
    return sample_code.SYNTAX_ERROR_CODE

@pytest.fixture
def empty_code():
    return sample_code.EMPTY_CODE
