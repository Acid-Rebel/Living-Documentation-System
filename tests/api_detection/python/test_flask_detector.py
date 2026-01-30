"""Tests for Flask API endpoint detection."""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from api_endpoint_detector.python.flask_detector import FlaskApiDetector
from code_parser.normalizers.python_normalizer import normalize_python_ast


FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "api" / "sample_flask_app.py"


def _load_normalized_ast():
	source = FIXTURE_PATH.read_text(encoding="utf-8")
	raw_ast = ast.parse(source)
	return normalize_python_ast(raw_ast)


def test_flask_detector_identifies_routes():
	ast_root = _load_normalized_ast()
	detector = FlaskApiDetector()

	endpoints = detector.detect(ast_root, str(FIXTURE_PATH))

	signature_set = {(endpoint.path, endpoint.http_method) for endpoint in endpoints}
	assert signature_set == {
		("/hello", "GET"),
		("/hello", "POST"),
		("/ping", "GET"),
		("/items", "PUT"),
	}

	hello_endpoint = next(
		endpoint
		for endpoint in endpoints
		if endpoint.handler_name == "hello_route" and endpoint.http_method == "GET"
	)
	assert hello_endpoint.class_name is None
	assert hello_endpoint.metadata["decorator"]["name"] == "app.route"

	blueprint_endpoint = next(
		endpoint for endpoint in endpoints if endpoint.handler_name == "blueprint_route"
	)
	assert blueprint_endpoint.http_method == "PUT"
	assert blueprint_endpoint.metadata["decorator"]["name"] == "blueprint.route"
