"""
test_arch_flow_diagram.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for diagram_generator.arch_flow_diagram:
  - build_arch_graph  (layer classification + flow extraction)
  - render_arch_flow_diagram_dot
  - render_arch_flow_diagram (Mermaid)
  - _classify helper
"""

import pytest
try:
    from diagram_generator import *
except ImportError:
    pytest.skip('Legacy dependencies missing', allow_module_level=True)
from unittest.mock import MagicMock

from diagram_generator.graph_model import DiagramGraph, ClassInfo
from diagram_generator.arch_flow_diagram import (
    build_arch_graph,
    render_arch_flow_diagram_dot,
    render_arch_flow_diagram,
    _classify,
    LAYERS,
)


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def _make_graph(class_names=None, dependencies=None, calls=None):
    graph = DiagramGraph()
    for cls_name in (class_names or []):
        graph.classes[cls_name] = ClassInfo(module=f"app.{cls_name.lower()}")
    if dependencies:
        graph.dependencies.update(dependencies)
    if calls:
        graph.calls.update(calls)
    return graph


def _make_endpoint(path="/api/test", method="GET"):
    ep = MagicMock()
    ep.path = path
    ep.http_method = method
    return ep


def _make_artifacts(endpoints=None):
    artifacts = MagicMock()
    artifacts.api_endpoints = endpoints or []
    return artifacts


# ---------------------------------------------------------------------------
# _classify
# ---------------------------------------------------------------------------

class TestClassify:

    def test_controller_mapped_to_api(self):
        assert _classify("UserController") == "API"

    def test_route_mapped_to_api(self):
        assert _classify("user_route") == "API"

    def test_service_mapped_to_service(self):
        assert _classify("OrderService") == "Service"

    def test_manager_mapped_to_service(self):
        assert _classify("SessionManager") == "Service"

    def test_repo_mapped_to_repository(self):
        assert _classify("UserRepo") == "Repository"

    def test_repository_mapped_to_repository(self):
        assert _classify("ProductRepository") == "Repository"

    def test_model_mapped_to_model(self):
        assert _classify("UserModel") == "Model"

    def test_entity_mapped_to_model(self):
        assert _classify("OrderEntity") == "Model"

    def test_client_mapped_to_external(self):
        assert _classify("PaymentClient") == "External"

    def test_adapter_mapped_to_external(self):
        assert _classify("EmailAdapter") == "External"

    def test_util_mapped_to_utility(self):
        assert _classify("StringUtil") == "Utility"

    def test_helper_mapped_to_utility(self):
        assert _classify("DateHelper") == "Utility"

    def test_unknown_name_mapped_to_other(self):
        assert _classify("XyZComponent") == "Other"

    def test_dotted_path_tail_used_for_classification(self):
        # Last segment "controller" should classify to API
        assert _classify("app.web.UserController") == "API"

    def test_case_insensitive_matching(self):
        assert _classify("USERSERVICE") == "Service"


# ---------------------------------------------------------------------------
# build_arch_graph
# ---------------------------------------------------------------------------

class TestBuildArchGraph:

    def test_empty_graph_returns_empty_nodes(self):
        artifacts = _make_artifacts()
        graph = _make_graph()
        result = build_arch_graph(artifacts, graph)
        assert result["nodes"] == set()
        assert result["flows"] == []

    def test_classes_classified_into_layers(self):
        artifacts = _make_artifacts()
        graph = _make_graph(class_names=["UserController", "UserService", "UserRepo"])
        result = build_arch_graph(artifacts, graph)

        assert "UserController" in result["layers"].get("API", [])
        assert "UserService" in result["layers"].get("Service", [])
        assert "UserRepo" in result["layers"].get("Repository", [])

    def test_dependency_creates_inter_layer_flow(self):
        artifacts = _make_artifacts()
        graph = _make_graph(
            class_names=["UserController", "UserService"],
            dependencies={("UserController", "UserService")},
        )
        result = build_arch_graph(artifacts, graph)
        flows = [(s, d) for s, d, _ in result["flows"]]
        assert ("API", "Service") in flows

    def test_call_relation_creates_flow(self):
        artifacts = _make_artifacts()
        graph = _make_graph(
            class_names=["OrderService", "OrderRepo"],
            calls={("OrderService", "OrderRepo")},
        )
        result = build_arch_graph(artifacts, graph)
        flows = [(s, d) for s, d, _ in result["flows"]]
        assert ("Service", "Repository") in flows

    def test_same_layer_flows_excluded(self):
        """Two classes in the same layer should NOT create a flow edge."""
        artifacts = _make_artifacts()
        graph = _make_graph(
            class_names=["UserService", "OrderService"],
            dependencies={("UserService", "OrderService")},
        )
        result = build_arch_graph(artifacts, graph)
        # Both are in "Service" layer → same layer flow should be absent
        flows = [(s, d) for s, d, _ in result["flows"]]
        assert ("Service", "Service") not in flows

    def test_api_endpoints_captured(self):
        ep1 = _make_endpoint("/api/users", "GET")
        ep2 = _make_endpoint("/api/orders", "POST")
        artifacts = _make_artifacts(endpoints=[ep1, ep2])
        graph = _make_graph()
        result = build_arch_graph(artifacts, graph)
        assert "GET /api/users" in result["api_entries"]
        assert "POST /api/orders" in result["api_entries"]

    def test_flow_count_accumulated(self):
        artifacts = _make_artifacts()
        graph = _make_graph(
            class_names=["ControllerA", "ControllerB", "ServiceX"],
            dependencies={
                ("ControllerA", "ServiceX"),
                ("ControllerB", "ServiceX"),
            },
        )
        result = build_arch_graph(artifacts, graph)
        api_to_svc = [(s, d, c) for s, d, c in result["flows"]
                      if s == "API" and d == "Service"]
        assert len(api_to_svc) == 1
        assert api_to_svc[0][2] == 2  # two edges collapsed into one flow


# ---------------------------------------------------------------------------
# render_arch_flow_diagram_dot
# ---------------------------------------------------------------------------

class TestRenderArchFlowDiagramDot:

    def _sample_arch(self):
        artifacts = _make_artifacts(endpoints=[_make_endpoint()])
        graph = _make_graph(
            class_names=["ProductController", "ProductService", "ProductRepo"],
            dependencies={
                ("ProductController", "ProductService"),
                ("ProductService", "ProductRepo"),
            },
        )
        return build_arch_graph(artifacts, graph)

    def test_returns_string(self):
        dot = render_arch_flow_diagram_dot(self._sample_arch())
        assert isinstance(dot, str)

    def test_contains_digraph(self):
        dot = render_arch_flow_diagram_dot(self._sample_arch())
        assert "digraph" in dot

    def test_layer_subgraphs_present(self):
        dot = render_arch_flow_diagram_dot(self._sample_arch())
        assert "subgraph" in dot
        assert "cluster_" in dot

    def test_api_entry_points_section_present(self):
        dot = render_arch_flow_diagram_dot(self._sample_arch())
        assert "Entry" in dot

    def test_class_names_in_output(self):
        dot = render_arch_flow_diagram_dot(self._sample_arch())
        assert "ProductController" in dot
        assert "ProductService" in dot
        assert "ProductRepo" in dot

    def test_empty_arch_valid_dot(self):
        dot = render_arch_flow_diagram_dot(
            {"layers": {}, "nodes": set(), "flows": [], "api_entries": [],
             "class_to_layer": {}}
        )
        assert "digraph" in dot
        assert dot.endswith("}")


# ---------------------------------------------------------------------------
# render_arch_flow_diagram (Mermaid)
# ---------------------------------------------------------------------------

class TestRenderArchFlowDiagram:

    def _sample_arch(self):
        artifacts = _make_artifacts(endpoints=[_make_endpoint("/api/items", "GET")])
        graph = _make_graph(
            class_names=["ItemController", "ItemService"],
            dependencies={("ItemController", "ItemService")},
        )
        return build_arch_graph(artifacts, graph)

    def test_returns_mermaid_fenced_block(self):
        md = render_arch_flow_diagram(self._sample_arch())
        assert md.startswith("```mermaid")
        assert md.endswith("```")

    def test_contains_graph_td(self):
        md = render_arch_flow_diagram(self._sample_arch())
        assert "graph TD" in md

    def test_subgraphs_present(self):
        md = render_arch_flow_diagram(self._sample_arch())
        assert "subgraph" in md

    def test_api_entry_subgraph_present(self):
        md = render_arch_flow_diagram(self._sample_arch())
        assert "ENTRY" in md or "Entry" in md

    def test_class_names_in_mermaid(self):
        md = render_arch_flow_diagram(self._sample_arch())
        assert "ItemController" in md
        assert "ItemService" in md

    def test_empty_arch_valid_mermaid(self):
        md = render_arch_flow_diagram(
            {"layers": {}, "nodes": set(), "flows": [], "api_entries": [],
             "class_to_layer": {}}
        )
        assert "graph TD" in md

    def test_flow_edges_rendered(self):
        md = render_arch_flow_diagram(self._sample_arch())
        # At least one flow edge (-->) should appear
        assert "-->" in md
