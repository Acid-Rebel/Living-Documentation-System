"""Unit tests for Python call analyzer."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from code_parser.ast_schema import ASTNode
from semantic_extractor.python.call_analyzer import PythonCallAnalyzer


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


def test_call_analyzer_records_function_and_method_calls() -> None:
    ast_root = _node(
        "Module",
        children=[
            _node(
                "FunctionDef",
                name="compute",
                children=[
                    _node("Call", metadata={"qualified_name": "helper"}),
                ],
            ),
            _node(
                "ClassDef",
                name="Greeter",
                children=[
                    _node(
                        "FunctionDef",
                        name="greet",
                        children=[
                            _node("Call", metadata={"qualified_name": "self.helper"}),
                        ],
                    )
                ],
            ),
        ],
    )

    analyzer = PythonCallAnalyzer()
    relations = analyzer.analyze(ast_root, FILE_PATH)

    summaries = {(rel.source, rel.target) for rel in relations}

    assert ("compute", "helper") in summaries
    assert ("Greeter.greet", "self.helper") in summaries
