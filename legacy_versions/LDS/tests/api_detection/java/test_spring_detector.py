"""Tests for Spring API endpoint detection."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api_endpoint_detector.java.spring_detector import SpringApiDetector
from code_parser.parsers.java_parser import JavaParser


FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "api" / "SampleSpringController.java"


def _load_normalized_ast():
    source = FIXTURE_PATH.read_text(encoding="utf-8")
    parser = JavaParser()
    raw_ast = parser.parse(source)
    return parser.normalize(raw_ast)


def test_spring_detector_identifies_mappings():
    ast_root = _load_normalized_ast()
    detector = SpringApiDetector()

    endpoints = detector.detect(ast_root, str(FIXTURE_PATH))

    signature_set = {(endpoint.path, endpoint.http_method) for endpoint in endpoints}
    assert signature_set == {
        ("/api/status", "GET"),
        ("/api/items", "POST"),
        ("/api/fallback", "PUT"),
        ("/api/legacy", "PUT"),
        ("/api/items/{id}", "PATCH"),
    }

    status_endpoint = next(
        endpoint
        for endpoint in endpoints
        if endpoint.handler_name == "status"
    )
    assert status_endpoint.class_name == "SampleSpringController"
    assert status_endpoint.metadata["annotation"]["name"].endswith("GetMapping")

    fallback_endpoint = next(
        endpoint
        for endpoint in endpoints
        if endpoint.path == "/api/fallback"
    )
    assert fallback_endpoint.http_method == "PUT"
    assert fallback_endpoint.metadata["annotation"]["keywords"]["method"] == "PUT"
