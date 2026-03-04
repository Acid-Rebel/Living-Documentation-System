"""Unit tests for Python symbol analyzer."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from semantic_extractor.python.symbol_analyzer import PythonSymbolAnalyzer


FILE_PATH = "tests/fixtures/sample_python_simple.py"


def _node(node_type: str, name: str | None = None, children: list[ASTNode] | None = None) -> ASTNode:
    return ASTNode(
        node_type=node_type,
        name=name,
        language="python",
        children=children or [],
        metadata={},
    )


def test_symbol_analyzer_extracts_classes_methods_and_functions() -> None:
    ast_root = _node(
        "Module",
        children=[
            _node(
                "ClassDef",
                name="Greeter",
                children=[
                    _node("FunctionDef", name="__init__"),
                    _node("FunctionDef", name="greet"),
                ],
            ),
            _node("FunctionDef", name="helper"),
        ],
    )

    analyzer = PythonSymbolAnalyzer()
    symbols = analyzer.analyze(ast_root, FILE_PATH)

    by_name = {symbol.name: symbol for symbol in symbols}

    assert by_name["Greeter"].symbol_type == "class"
    assert by_name["Greeter"].parent is None

    assert by_name["Greeter.__init__"].symbol_type == "method"
    assert by_name["Greeter.__init__"].parent == "Greeter"

    assert by_name["Greeter.greet"].symbol_type == "method"
    assert by_name["Greeter.greet"].parent == "Greeter"

    assert by_name["helper"].symbol_type == "function"
    assert by_name["helper"].parent is None
