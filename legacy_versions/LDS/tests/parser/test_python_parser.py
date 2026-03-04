"""Unit tests for the Python parser and normalizer."""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from code_parser.parsers.python_parser import PythonParser

FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"


def _load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_parse_produces_ast_module() -> None:
    parser = PythonParser()
    source_code = _load_fixture("sample_python_simple.py")

    raw_ast = parser.parse(source_code)

    assert isinstance(raw_ast, ast.Module)
    names = {node.name for node in raw_ast.body if hasattr(node, "name")}
    assert "Greeter" in names
    assert "helper" in names


def test_normalize_produces_language_agnostic_ast() -> None:
    parser = PythonParser()
    source_code = _load_fixture("sample_python_simple.py")
    raw_ast = parser.parse(source_code)

    normalized = parser.normalize(raw_ast)

    assert isinstance(normalized, ASTNode)
    assert normalized.node_type == "Module"
    assert normalized.language == "python"

    class_nodes = [child for child in normalized.children if child.node_type == "ClassDef"]
    function_nodes = [child for child in normalized.children if child.node_type == "FunctionDef"]

    assert any(node.name == "Greeter" for node in class_nodes)
    assert any(node.name == "helper" for node in function_nodes)
    assert all(node.language == "python" for node in normalized.children)
