"""Unit tests for Java call analyzer."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from semantic_extractor.java.call_analyzer import JavaCallAnalyzer


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


def test_call_analyzer_records_method_invocations() -> None:
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
                        children=[
                            _node(
                                "MethodInvocation",
                                metadata={"name": "helper", "qualifier": "utils"},
                            ),
                        ],
                    )
                ],
            ),
        ],
    )

    analyzer = JavaCallAnalyzer()
    relations = analyzer.analyze(ast_root, FILE_PATH)

    relation_pairs = {(rel.source, rel.target) for rel in relations}

    assert ("fixtures.SampleJava.sum", "utils.helper") in relation_pairs
