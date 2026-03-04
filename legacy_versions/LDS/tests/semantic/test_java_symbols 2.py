"""Unit tests for Java symbol analyzer."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from semantic_extractor.java.symbol_analyzer import JavaSymbolAnalyzer


FILE_PATH = "tests/fixtures/SampleJava.java"


def _node(
    node_type: str,
    name: str | None = None,
    *,
    children: list[ASTNode] | None = None,
    metadata: dict | None = None,
) -> ASTNode:
    return ASTNode(
        node_type=node_type,
        name=name,
        language="java",
        children=children or [],
        metadata=metadata or {},
    )


def test_symbol_analyzer_produces_package_qualified_symbols() -> None:
    ast_root = _node(
        "CompilationUnit",
        children=[
            _node("PackageDeclaration", metadata={"name": "fixtures"}),
            _node(
                "ClassDeclaration",
                name="SampleJava",
                children=[
                    _node(
                        "MethodDeclaration",
                        name="sum",
                    )
                ],
            ),
        ],
    )

    analyzer = JavaSymbolAnalyzer()
    symbols = analyzer.analyze(ast_root, FILE_PATH)

    by_name = {symbol.name: symbol for symbol in symbols}

    assert by_name["fixtures.SampleJava"].symbol_type == "class"
    assert by_name["fixtures.SampleJava"].parent == "fixtures"

    assert by_name["fixtures.SampleJava.sum"].symbol_type == "method"
    assert by_name["fixtures.SampleJava.sum"].parent == "fixtures.SampleJava"
