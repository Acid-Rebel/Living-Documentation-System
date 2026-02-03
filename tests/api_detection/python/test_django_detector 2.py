"""Tests for Django API endpoint detection."""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api_endpoint_detector.python.django_detector import DjangoApiDetector
from code_parser.normalizers.python_normalizer import normalize_python_ast


FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "api" / "sample_django_urls.py"


def _load_normalized_ast():
    source = FIXTURE_PATH.read_text(encoding="utf-8")
    raw_ast = ast.parse(source)
    return normalize_python_ast(raw_ast)


def test_django_detector_identifies_urlpatterns():
    ast_root = _load_normalized_ast()
    detector = DjangoApiDetector()

    endpoints = detector.detect(ast_root, str(FIXTURE_PATH))

    signature = {(endpoint.path, endpoint.handler_name) for endpoint in endpoints}
    assert signature == {
        ("/health/", "views.health_view"),
        ("/items/<int:item_id>/", "views.ItemDetailView.as_view"),
        ("^legacy/$", "views.legacy_view"),
        ("/status/", "views.status_view"),
    }

    cbv_endpoint = next(
        endpoint for endpoint in endpoints if endpoint.handler_name == "views.ItemDetailView.as_view"
    )
    assert cbv_endpoint.class_name == "views.ItemDetailView"
    assert cbv_endpoint.metadata["route_name"] == "item-detail"
    assert cbv_endpoint.http_method == "ANY"
    assert cbv_endpoint.framework == "django"

    regex_endpoint = next(
        endpoint for endpoint in endpoints if endpoint.path == "^legacy/$"
    )
    assert regex_endpoint.metadata["route_name"] == "legacy"
