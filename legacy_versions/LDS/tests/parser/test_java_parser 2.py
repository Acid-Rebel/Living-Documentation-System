"""Unit tests for the Java parser and normalizer."""

import sys
from pathlib import Path

import javalang

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from code_parser.parsers.java_parser import JavaParser

FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"


def _load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_parse_produces_compilation_unit() -> None:
    parser = JavaParser()
    source_code = _load_fixture("SampleJava.java")

    raw_ast = parser.parse(source_code)

    assert isinstance(raw_ast, javalang.tree.CompilationUnit)
    type_names = [type_decl.name for type_decl in raw_ast.types if hasattr(type_decl, "name")]
    assert "SampleJava" in type_names


def test_normalize_produces_language_agnostic_ast() -> None:
    parser = JavaParser()
    source_code = _load_fixture("SampleJava.java")
    raw_ast = parser.parse(source_code)

    normalized = parser.normalize(raw_ast)

    assert isinstance(normalized, ASTNode)
    assert normalized.node_type == "CompilationUnit"
    assert normalized.language == "java"

    class_nodes = [child for child in normalized.children if child.node_type == "ClassDeclaration"]
    assert any(node.name == "SampleJava" for node in class_nodes)
    assert all(node.language == "java" for node in normalized.children if node.language is not None)
