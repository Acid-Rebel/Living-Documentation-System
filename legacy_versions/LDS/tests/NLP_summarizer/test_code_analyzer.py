
import pytest
from nlp_summarizer.code_analyzer import CodeAnalyzer

def test_get_file_structure_simple(analyzer, simple_code):
    """Test analysis of simple code."""
    structure = analyzer.get_file_structure(simple_code)
    assert structure is not None
    assert structure['classes'] == []
    assert len(structure['functions']) == 1
    assert structure['functions'][0]['name'] == 'hello'
    assert structure['docstring'] is None
    assert "import os" in structure['imports']

def test_get_file_structure_complex(analyzer, complex_code):
    """Test analysis of complex code with classes and docstrings."""
    structure = analyzer.get_file_structure(complex_code)
    assert structure is not None
    
    # Check classes
    assert len(structure['classes']) == 1
    cls = structure['classes'][0]
    assert cls['name'] == 'Processor'
    assert cls['docstring'] is not None
    assert len(cls['methods']) == 2 # init and process
    
    # Check functions
    assert len(structure['functions']) == 1
    assert structure['functions'][0]['name'] == 'helper_func'
    
    # Check imports
    assert "import ast" in structure['imports']
    assert "from typing import List" in structure['imports']

def test_get_file_structure_syntax_error(analyzer, syntax_error_code):
    """Test that syntax errors are handled gracefully."""
    structure = analyzer.get_file_structure(syntax_error_code)
    assert structure is None

def test_get_file_structure_empty(analyzer, empty_code):
    """Test analysis of empty code."""
    structure = analyzer.get_file_structure(empty_code)
    assert structure is not None
    assert structure['classes'] == []
    assert structure['functions'] == []
    assert structure['imports'] == []
    assert structure['docstring'] is None
