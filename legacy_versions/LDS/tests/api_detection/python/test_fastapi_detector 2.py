"""Tests for FastAPI endpoint detection."""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api_endpoint_detector.python.fastapi_detector import FastApiDetector
from code_parser.normalizers.python_normalizer import normalize_python_ast


FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "api" / "sample_fastapi_app.py"


def _load_normalized_ast():
    source = FIXTURE_PATH.read_text(encoding="utf-8")
    raw_ast = ast.parse(source)
    return normalize_python_ast(raw_ast)


def test_fastapi_detector_identifies_routes():
    ast_root = _load_normalized_ast()
    detector = FastApiDetector()

    endpoints = detector.detect(ast_root, str(FIXTURE_PATH))

    signature_set = {(endpoint.path, endpoint.http_method) for endpoint in endpoints}
    assert signature_set == {
        ("/health", "GET"),
        ("/items", "POST"),
        ("/users/{user_id}", "GET"),
        ("/users/{user_id}", "PATCH"),
    }

    health_endpoint = next(
        endpoint
        for endpoint in endpoints
        if endpoint.handler_name == "health_check"
    )
    assert health_endpoint.metadata["decorator"]["name"] == "app.get"
    assert health_endpoint.class_name is None

    router_endpoint = next(
        endpoint
        for endpoint in endpoints
        if endpoint.metadata["decorator"]["name"] == "router.patch"
    )
    assert router_endpoint.http_method == "PATCH"
