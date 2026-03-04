"""Unit tests for Python import analyzer."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from semantic_extractor.python.import_analyzer import PythonImportAnalyzer


FILE_PATH = "tests/fixtures/sample_python_simple.py"


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
        language="python",
        children=children or [],
        metadata=metadata or {},
    )


def test_import_analyzer_captures_module_and_scoped_imports() -> None:
    ast_root = _node(
        "Module",
        children=[
            _node("Import", metadata={"modules": ["math"]}),
            _node(
                "FunctionDef",
                name="compute",
                children=[
                    _node("Import", metadata={"modules": ["collections"]}),
                ],
            ),
            _node(
                "ImportFrom",
                metadata={"module": "pathlib"},
                children=[_node("alias", name="Path")],
            ),
        ],
    )

    analyzer = PythonImportAnalyzer()
    relations = analyzer.analyze(ast_root, FILE_PATH)

    summaries = {(rel.source, rel.target) for rel in relations}

    assert (FILE_PATH, "math") in summaries
    assert ("compute", "collections") in summaries
    assert (FILE_PATH, "pathlib.Path") in summaries
