import pytest
from semantic_insights.analyzer_manager import AnalyzerManager
from semantic_insights.models.symbol import Symbol
from semantic_insights.models.summary import Summary
from code_parser.ast_schema import ASTNode

@pytest.fixture
def manager():
    return AnalyzerManager()

def test_analyzer_manager_initialization(manager):
    assert "python" in manager._symbol_analyzers
    assert "java" in manager._symbol_analyzers
    assert "python" in manager._relation_analyzers

def test_analyze_python_simple(manager, tmp_path):
    # Mock some data
    code = "def hello():\n    \"\"\"Doc.\"\"\"\n    pass"
    file_path = tmp_path / "hello.py"
    file_path.write_text(code)
    
    ast_root = ASTNode(
        node_type="Module",
        language="python",
        name="hello",
        children=[
            ASTNode(node_type="FunctionDef", name="hello", language="python")
        ]
    )
    
    results = manager.analyze(ast_root, str(file_path), "python")
    
    assert "symbols" in results
    assert "relations" in results
    
    # Check symbols
    symbols = results["symbols"]
    assert any(s.name == "hello" and s.symbol_type == "function" for s in symbols if isinstance(s, Symbol))
    
    # Check summary (since we integrated it earlier)
    summaries = [s for s in symbols if isinstance(s, Summary)]
    assert len(summaries) == 1
    assert "hello`: Doc." in summaries[0].content

def test_unsupported_language(manager):
    with pytest.raises(ValueError, match="Unsupported language"):
        manager.analyze(ASTNode(node_type="Module"), "test.js", "javascript")

def test_filter_type(manager):
    class A: pass
    class B: pass
    items = [A(), B(), A()]
    filtered = manager._filter_type(items, A)
    assert len(filtered) == 2
    assert all(isinstance(x, A) for x in filtered)
