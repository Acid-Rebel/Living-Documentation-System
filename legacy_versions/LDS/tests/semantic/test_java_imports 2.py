"""Unit tests for Java import analyzer."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from semantic_extractor.java.import_analyzer import JavaImportAnalyzer


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


def test_import_analyzer_emits_defines_and_import_relations() -> None:
    ast_root = _node(
        "CompilationUnit",
        children=[
            _node("PackageDeclaration", metadata={"name": "fixtures"}),
            _node("ImportDeclaration", metadata={"path": "java.util.List"}),
            _node(
                "ClassDeclaration",
                name="SampleJava",
            ),
        ],
    )

    analyzer = JavaImportAnalyzer()
    relations = analyzer.analyze(ast_root, FILE_PATH)

    relation_pairs = {(rel.relation_type, rel.source, rel.target) for rel in relations}

    assert ("DEFINES", FILE_PATH, "fixtures") in relation_pairs
    assert ("IMPORTS", FILE_PATH, "java.util.List") in relation_pairs
