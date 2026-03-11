"""
test_er_diagram.py
~~~~~~~~~~~~~~~~~~
Unit tests for diagram_generator.er_diagram:
  - build_er_graph
  - render_er_diagram_dot
  - render_er_diagram (Mermaid)
  - helper functions: _detect_pk, _infer_attr_type
"""

import pytest
try:
    from diagram_generator import *
except ImportError:
    pytest.skip('Legacy dependencies missing', allow_module_level=True)

from diagram_generator.graph_model import DiagramGraph, ClassInfo
from diagram_generator.er_diagram import (
    build_er_graph,
    render_er_diagram_dot,
    render_er_diagram,
    _detect_pk,
    _infer_attr_type,
)


# ---------------------------------------------------------------------------
# Fixtures / Helpers
# ---------------------------------------------------------------------------

def _make_graph_with_classes(class_defs, composition=None, aggregation=None,
                              inheritance=None):
    """
    Build a DiagramGraph with the given class definitions.

    class_defs: dict { class_name: {"attributes": [...], "methods": [...]} }
    """
    graph = DiagramGraph()
    for cls_name, data in class_defs.items():
        info = ClassInfo(module=f"module.{cls_name.lower()}")
        info.attributes = set(data.get("attributes", []))
        info.methods = set(data.get("methods", []))
        graph.classes[cls_name] = info

    if composition:
        graph.composition.update(composition)
    if aggregation:
        graph.aggregation.update(aggregation)
    if inheritance:
        graph.inheritance.update(inheritance)

    return graph


# ---------------------------------------------------------------------------
# build_er_graph
# ---------------------------------------------------------------------------

class TestBuildErGraph:

    def test_empty_graph_returns_empty_entities(self):
        graph = DiagramGraph()
        er = build_er_graph(graph)
        assert er["entities"] == {}
        assert er["relations"] == []

    def test_class_without_attrs_excluded(self):
        graph = _make_graph_with_classes({
            "EmptyClass": {"attributes": [], "methods": ["do_something"]}
        })
        er = build_er_graph(graph)
        assert "EmptyClass" not in er["entities"]

    def test_class_with_attrs_becomes_entity(self):
        graph = _make_graph_with_classes({
            "User": {"attributes": ["id", "name", "email"]}
        })
        er = build_er_graph(graph)
        assert "User" in er["entities"]
        attrs = er["entities"]["User"]["attributes"]
        assert "id" in attrs
        assert "name" in attrs
        assert "email" in attrs

    def test_pk_detected_for_id_attr(self):
        graph = _make_graph_with_classes({
            "Product": {"attributes": ["id", "price", "name"]}
        })
        er = build_er_graph(graph)
        assert er["entities"]["Product"]["pk"] == "id"

    def test_pk_detected_class_specific_id(self):
        graph = _make_graph_with_classes({
            "Order": {"attributes": ["order_id", "total"]}
        })
        er = build_er_graph(graph)
        assert er["entities"]["Order"]["pk"] == "order_id"

    def test_composition_becomes_relation(self):
        graph = _make_graph_with_classes({
            "Order": {"attributes": ["order_id", "status"]},
            "LineItem": {"attributes": ["item_id", "quantity"]},
        }, composition={("Order", "LineItem")})
        er = build_er_graph(graph)
        assert len(er["relations"]) == 1
        src, dst, *_ = er["relations"][0]
        assert src == "Order"
        assert dst == "LineItem"

    def test_aggregation_becomes_relation(self):
        graph = _make_graph_with_classes({
            "Department": {"attributes": ["dept_id", "name"]},
            "Employee": {"attributes": ["emp_id", "salary"]},
        }, aggregation={("Department", "Employee")})
        er = build_er_graph(graph)
        assert len(er["relations"]) == 1

    def test_inheritance_becomes_isa_relation(self):
        graph = _make_graph_with_classes({
            "Animal": {"attributes": ["id", "name"]},
            "Dog": {"attributes": ["id", "breed"]},
        }, inheritance={("Dog", "Animal")})
        er = build_er_graph(graph)
        isa = [r for r in er["relations"] if r[4] == "is a"]
        assert len(isa) == 1

    def test_composition_excluded_if_entity_not_in_graph(self):
        """If one side of a relation is a class without attrs, skip the relation."""
        graph = _make_graph_with_classes({
            "Order": {"attributes": ["order_id"]},
        }, composition={("Order", "Ghost")})
        er = build_er_graph(graph)
        # Ghost has no attributes → not an entity → relation excluded
        assert er["relations"] == []

    def test_multiple_entities_and_relations(self):
        graph = _make_graph_with_classes(
            {
                "A": {"attributes": ["id", "val"]},
                "B": {"attributes": ["id", "ref"]},
                "C": {"attributes": ["id", "data"]},
            },
            composition={("A", "B")},
            aggregation={("B", "C")},
        )
        er = build_er_graph(graph)
        assert len(er["entities"]) == 3
        assert len(er["relations"]) == 2


# ---------------------------------------------------------------------------
# render_er_diagram_dot
# ---------------------------------------------------------------------------

class TestRenderErDiagramDot:

    def _simple_er(self):
        graph = _make_graph_with_classes({
            "Customer": {"attributes": ["id", "name", "email"]},
            "Order": {"attributes": ["order_id", "date", "total"]},
        }, composition={("Customer", "Order")})
        return build_er_graph(graph)

    def test_returns_string(self):
        dot = render_er_diagram_dot(self._simple_er())
        assert isinstance(dot, str)

    def test_contains_digraph(self):
        dot = render_er_diagram_dot(self._simple_er())
        assert "digraph" in dot

    def test_entity_nodes_present(self):
        dot = render_er_diagram_dot(self._simple_er())
        assert "Customer" in dot
        assert "Order" in dot

    def test_attributes_listed(self):
        dot = render_er_diagram_dot(self._simple_er())
        assert "name" in dot
        assert "email" in dot

    def test_relation_edge_present(self):
        dot = render_er_diagram_dot(self._simple_er())
        assert "->" in dot

    def test_empty_er_still_valid(self):
        dot = render_er_diagram_dot({"entities": {}, "relations": []})
        assert "digraph" in dot
        assert dot.endswith("}")

    def test_aggregation_relation_in_output(self):
        graph = _make_graph_with_classes({
            "Team": {"attributes": ["id", "name"]},
            "Member": {"attributes": ["id", "role"]},
        }, aggregation={("Team", "Member")})
        er = build_er_graph(graph)
        dot = render_er_diagram_dot(er)
        assert "Team" in dot
        assert "Member" in dot


# ---------------------------------------------------------------------------
# render_er_diagram (Mermaid)
# ---------------------------------------------------------------------------

class TestRenderErDiagram:

    def _simple_er(self):
        graph = _make_graph_with_classes({
            "User": {"attributes": ["user_id", "username", "is_active"]},
            "Post": {"attributes": ["post_id", "title", "created_at"]},
        }, aggregation={("User", "Post")})
        return build_er_graph(graph)

    def test_returns_mermaid_fenced_block(self):
        md = render_er_diagram(self._simple_er())
        assert md.startswith("```mermaid")
        assert md.endswith("```")

    def test_contains_er_diagram_keyword(self):
        md = render_er_diagram(self._simple_er())
        assert "erDiagram" in md

    def test_entities_present(self):
        md = render_er_diagram(self._simple_er())
        assert "User" in md
        assert "Post" in md

    def test_attributes_listed_with_types(self):
        md = render_er_diagram(self._simple_er())
        assert "username" in md
        assert "title" in md

    def test_pk_marked(self):
        md = render_er_diagram(self._simple_er())
        assert "PK" in md

    def test_boolean_attr_typed_correctly(self):
        md = render_er_diagram(self._simple_er())
        assert "boolean" in md   # is_active → boolean

    def test_datetime_attr_typed_correctly(self):
        md = render_er_diagram(self._simple_er())
        assert "datetime" in md  # created_at → datetime

    def test_empty_er_valid_mermaid(self):
        md = render_er_diagram({"entities": {}, "relations": []})
        assert "erDiagram" in md


# ---------------------------------------------------------------------------
# _detect_pk
# ---------------------------------------------------------------------------

class TestDetectPk:

    def test_detects_id(self):
        assert _detect_pk("User", {"id", "name"}) == "id"

    def test_detects_class_id(self):
        assert _detect_pk("Product", {"product_id", "price"}) == "product_id"

    def test_returns_none_when_no_pk(self):
        assert _detect_pk("Config", {"key", "value"}) is None


# ---------------------------------------------------------------------------
# _infer_attr_type
# ---------------------------------------------------------------------------

class TestInferAttrType:

    def test_id_field_is_int(self):
        assert _infer_attr_type("user_id") == "int"

    def test_date_field_is_datetime(self):
        assert _infer_attr_type("created_at") == "datetime"

    def test_bool_field(self):
        assert _infer_attr_type("is_active") == "boolean"

    def test_numeric_field(self):
        assert _infer_attr_type("total_amount") == "float"

    def test_default_is_string(self):
        assert _infer_attr_type("username") == "string"
