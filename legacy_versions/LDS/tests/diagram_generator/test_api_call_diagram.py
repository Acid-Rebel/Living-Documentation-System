"""
test_api_call_diagram.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for diagram_generator.api_call_diagram:
  - build_api_call_graph
  - render_api_call_diagram_dot
  - render_api_call_diagram (Mermaid)
"""

import pytest
from unittest.mock import MagicMock

from diagram_generator.graph_model import DiagramGraph, ClassInfo
from diagram_generator.api_call_diagram import (
    build_api_call_graph,
    render_api_call_diagram_dot,
    render_api_call_diagram,
    _safe,
)


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def _make_endpoint(path="/api/users", method="GET", handler="get_users",
                   class_name=None, framework="flask", file_path="app/routes.py",
                   language="python"):
    ep = MagicMock()
    ep.path = path
    ep.http_method = method
    ep.handler_name = handler
    ep.class_name = class_name
    ep.framework = framework
    ep.file_path = file_path
    ep.language = language
    return ep


def _make_relation(source, target, relation_type, language="python", file_path="app.py"):
    rel = MagicMock()
    rel.source = source
    rel.target = target
    rel.relation_type = relation_type
    rel.language = language
    rel.file_path = file_path
    return rel


def _make_artifacts(endpoints=None, relations=None):
    artifacts = MagicMock()
    artifacts.api_endpoints = endpoints or []
    artifacts.relations = relations or []
    return artifacts


def _make_graph(calls=None):
    graph = DiagramGraph()
    if calls:
        graph.calls.update(calls)
    return graph


# ---------------------------------------------------------------------------
# build_api_call_graph
# ---------------------------------------------------------------------------

class TestBuildApiCallGraph:

    def test_empty_artifacts_returns_empty_list(self):
        artifacts = _make_artifacts()
        graph = _make_graph()
        result = build_api_call_graph(artifacts, graph)
        assert result == []

    def test_single_endpoint_no_calls(self):
        ep = _make_endpoint()
        artifacts = _make_artifacts(endpoints=[ep])
        graph = _make_graph()
        result = build_api_call_graph(artifacts, graph)

        assert len(result) == 1
        node = result[0]
        assert node["endpoint"] == "GET /api/users"
        assert node["http_method"] == "GET"
        assert node["path"] == "/api/users"
        assert node["handler"] == "get_users"
        assert node["callers"] == []

    def test_semantic_calls_attached_to_handler(self):
        ep = _make_endpoint(handler="create_order")
        rel = _make_relation("create_order", "OrderService.save", "CALLS")
        artifacts = _make_artifacts(endpoints=[ep], relations=[rel])
        graph = _make_graph()

        result = build_api_call_graph(artifacts, graph)
        assert len(result) == 1
        assert "OrderService.save" in result[0]["callers"]

    def test_ast_calls_used_as_fallback(self):
        ep = _make_endpoint(handler="list_items")
        artifacts = _make_artifacts(endpoints=[ep])
        graph = _make_graph(calls={("list_items", "ItemRepo.find_all")})

        result = build_api_call_graph(artifacts, graph)
        assert "ItemRepo.find_all" in result[0]["callers"]

    def test_qualified_class_handler_name_matched(self):
        """Handler candidates include class_name.handler combos."""
        ep = _make_endpoint(handler="update", class_name="UserController")
        rel = _make_relation("UserController.update", "UserService.update", "CALLS")
        artifacts = _make_artifacts(endpoints=[ep], relations=[rel])
        graph = _make_graph()

        result = build_api_call_graph(artifacts, graph)
        assert "UserService.update" in result[0]["callers"]

    def test_multiple_endpoints(self):
        ep1 = _make_endpoint(path="/users", method="GET", handler="list_users")
        ep2 = _make_endpoint(path="/orders", method="POST", handler="create_order")
        artifacts = _make_artifacts(endpoints=[ep1, ep2])
        graph = _make_graph()

        result = build_api_call_graph(artifacts, graph)
        assert len(result) == 2
        endpoints_labels = {r["endpoint"] for r in result}
        assert "GET /users" in endpoints_labels
        assert "POST /orders" in endpoints_labels

    def test_duplicate_callers_deduplicated(self):
        ep = _make_endpoint(handler="save")
        rel1 = _make_relation("save", "DB.insert", "CALLS")
        rel2 = _make_relation("save", "DB.insert", "CALLS")  # duplicate
        artifacts = _make_artifacts(endpoints=[ep], relations=[rel1, rel2])
        graph = _make_graph()

        result = build_api_call_graph(artifacts, graph)
        callers = result[0]["callers"]
        assert callers.count("DB.insert") == 1

    def test_imports_chased_one_level(self):
        ep = _make_endpoint(handler="handle")
        rel_import = _make_relation("handle", "service_module", "IMPORTS")
        rel_call = _make_relation("service_module", "process", "CALLS")
        artifacts = _make_artifacts(endpoints=[ep], relations=[rel_import, rel_call])
        graph = _make_graph()

        result = build_api_call_graph(artifacts, graph)
        assert "process" in result[0]["callers"]


# ---------------------------------------------------------------------------
# render_api_call_diagram_dot
# ---------------------------------------------------------------------------

class TestRenderApiCallDiagramDot:

    def _simple_graph(self):
        return [
            {
                "endpoint": "GET /items",
                "http_method": "GET",
                "path": "/items",
                "handler": "list_items",
                "framework": "flask",
                "file_path": "app/views.py",
                "class_name": None,
                "callers": ["ItemService.all"],
            }
        ]

    def test_returns_string(self):
        dot = render_api_call_diagram_dot(self._simple_graph())
        assert isinstance(dot, str)

    def test_contains_digraph(self):
        dot = render_api_call_diagram_dot(self._simple_graph())
        assert "digraph" in dot

    def test_endpoint_node_present(self):
        dot = render_api_call_diagram_dot(self._simple_graph())
        assert "GET" in dot
        assert "/items" in dot

    def test_handler_node_present(self):
        dot = render_api_call_diagram_dot(self._simple_graph())
        assert "list_items" in dot

    def test_callee_node_present(self):
        dot = render_api_call_diagram_dot(self._simple_graph())
        assert "ItemService.all" in dot

    def test_empty_graph_still_valid_dot(self):
        dot = render_api_call_diagram_dot([])
        assert "digraph" in dot
        assert dot.endswith("}")

    def test_class_name_shown_in_handler_label(self):
        graph = [
            {
                "endpoint": "POST /order",
                "http_method": "POST",
                "path": "/order",
                "handler": "create",
                "framework": "django",
                "file_path": "views.py",
                "class_name": "OrderView",
                "callers": [],
            }
        ]
        dot = render_api_call_diagram_dot(graph)
        assert "OrderView" in dot
        assert "create" in dot


# ---------------------------------------------------------------------------
# render_api_call_diagram (Mermaid)
# ---------------------------------------------------------------------------

class TestRenderApiCallDiagram:

    def _simple_graph(self):
        return [
            {
                "endpoint": "DELETE /user",
                "http_method": "DELETE",
                "path": "/user",
                "handler": "delete_user",
                "framework": "flask",
                "file_path": "app/routes.py",
                "class_name": None,
                "callers": ["UserRepo.delete"],
            }
        ]

    def test_returns_mermaid_fenced_block(self):
        md = render_api_call_diagram(self._simple_graph())
        assert md.startswith("```mermaid")
        assert md.endswith("```")

    def test_contains_graph_lr(self):
        md = render_api_call_diagram(self._simple_graph())
        assert "graph LR" in md

    def test_handler_and_callee_in_output(self):
        md = render_api_call_diagram(self._simple_graph())
        assert "delete_user" in md
        assert "UserRepo" in md

    def test_empty_graph_valid_mermaid(self):
        md = render_api_call_diagram([])
        assert "graph LR" in md


# ---------------------------------------------------------------------------
# Helper: _safe
# ---------------------------------------------------------------------------

class TestSafeHelper:
    def test_spaces_replaced(self):
        assert " " not in _safe("GET /api")

    def test_slashes_replaced(self):
        assert "/" not in _safe("GET /users")

    def test_dots_replaced(self):
        assert "." not in _safe("some.module")
