"""
er_diagram.py
~~~~~~~~~~~~~
Generates Entity-Relationship (ER) Diagrams from the diagram graph.

Entities are derived from classes that have at least one attribute.
Relationships are inferred from:
  - graph.composition   → strong (filled diamond) ER relationship
  - graph.aggregation   → weak (open diamond) ER relationship
  - graph.inheritance   → IS-A relationship (shown as a special ER edge)

Public API
----------
  build_er_graph(graph) -> dict
  render_er_diagram_dot(er_graph) -> str
  render_er_diagram(er_graph) -> str   (Mermaid erDiagram)
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from diagram_generator.renderers import wrap_mermaid


# ---------------------------------------------------------------------------
# ER graph data structure
# ---------------------------------------------------------------------------
# er_graph = {
#   "entities": {
#       entity_name: {
#           "attributes": List[str],
#           "pk": str | None          # heuristically detected primary key
#       }
#   },
#   "relations": [
#       (source, target, cardinality_src, cardinality_dst, label, rel_type)
#   ]
# }


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_er_graph(graph) -> dict:
    """
    Derive an ER graph from a ``DiagramGraph``.

    Only classes with at least one attribute are promoted to entities.
    Relationships are pulled from composition, aggregation, and inheritance.
    """
    entities: Dict[str, dict] = {}
    relations: List[Tuple] = []

    # ---- Entities from classes that have attributes ----
    entity_names: Set[str] = set()
    for cls_name, cls_info in graph.classes.items():
        if cls_info.attributes:
            pk = _detect_pk(cls_name, cls_info.attributes)
            attributes = sorted(cls_info.attributes)
            entities[cls_name] = {"attributes": attributes, "pk": pk}
            entity_names.add(cls_name)

    # ---- Relations from composition ----
    for owner, part in graph.composition:
        if owner in entity_names and part in entity_names:
            # Owner contains exactly one Part (1 to 1 strong)
            relations.append((owner, part, "||", "||", "contains", "composition"))

    # ---- Relations from aggregation ----
    for owner, part in graph.aggregation:
        if owner in entity_names and part in entity_names:
            # Owner has zero or many Part (1 to many weak)
            relations.append((owner, part, "|o", "o{", "has", "aggregation"))

    # ---- Relations from inheritance (IS-A) ----
    for child, parent in graph.inheritance:
        if child in entity_names and parent in entity_names:
            relations.append((child, parent, "|o", "|{", "is a", "inheritance"))

    return {"entities": entities, "relations": relations}


# ---------------------------------------------------------------------------
# DOT renderer
# ---------------------------------------------------------------------------

def render_er_diagram_dot(er_graph: dict) -> str:
    """
    Render the ER graph as a Graphviz DOT digraph using record-shaped nodes
    to show entity attributes.
    """
    entities = er_graph["entities"]
    relations = er_graph["relations"]

    lines = [
        "digraph ERDiagram {",
        "    rankdir=LR;",
        "    node [shape=record fontname=\"Helvetica\" fontsize=11];",
        "    edge [fontsize=10];",
        "",
    ]

    for entity_name, info in entities.items():
        attrs = info["attributes"]
        pk = info.get("pk")

        # Build record label: { EntityName | pk_attr | other_attrs }
        attr_lines = []
        for attr in attrs:
            if attr == pk:
                attr_lines.append(f"\\underline{{{attr}}} PK")
            else:
                attr_lines.append(attr)

        pk_row = ""
        other_rows = "\\l".join(attr_lines) + "\\l" if attr_lines else ""
        label = f"{{{entity_name}|{other_rows}}}"
        safe_id = _safe(entity_name)
        lines.append(f'    "{safe_id}" [label="{label}"];')

    lines.append("")

    _rel_styles = {
        "composition": "[arrowhead=diamond arrowtail=none dir=both]",
        "aggregation": "[arrowhead=odiamond arrowtail=none dir=both]",
        "inheritance": "[arrowhead=empty arrowtail=none style=dashed]",
    }

    for src, dst, card_src, card_dst, label, rel_type in relations:
        style = _rel_styles.get(rel_type, "[]")
        lines.append(
            f'    "{_safe(src)}" -> "{_safe(dst)}" '
            f'[label="{label}" {style}];'
        )

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mermaid renderer
# ---------------------------------------------------------------------------

def render_er_diagram(er_graph: dict) -> str:
    """
    Render the ER graph as a Mermaid ``erDiagram``.

    Mermaid ER relationship syntax::

        ENTITY_A ||--o{ ENTITY_B : "label"
    """
    entities = er_graph["entities"]
    relations = er_graph["relations"]

    lines = ["erDiagram"]

    # Entity definitions with attributes
    for entity_name, info in entities.items():
        attrs = info["attributes"]
        pk = info.get("pk")

        lines.append(f"    {_mermaid_safe(entity_name)} {{")
        for attr in attrs:
            # Mermaid attribute format: type name [PK]
            attr_type = _infer_attr_type(attr)
            pk_marker = " PK" if attr == pk else ""
            lines.append(f"        {attr_type} {_mermaid_safe(attr)}{pk_marker}")
        lines.append("    }")

    # Relationships
    for src, dst, card_src, card_dst, label, rel_type in relations:
        lines.append(
            f"    {_mermaid_safe(src)} {card_src}--{card_dst} "
            f'{_mermaid_safe(dst)} : "{label}"'
        )

    return wrap_mermaid("\n".join(lines))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_pk(class_name: str, attributes: Set[str]) -> str | None:
    """
    Heuristically detect the primary-key attribute.
    Prefers attributes named 'id', '<class>_id', or '<class>Id'.
    """
    lower = class_name.lower()
    candidates = ["id", f"{lower}_id", f"{lower}id"]
    for attr in attributes:
        if attr.lower() in candidates:
            return attr
    return None


def _infer_attr_type(attr: str) -> str:
    """
    Infer a simple SQL-like type for a Mermaid attribute from its name.
    """
    lower = attr.lower()
    if any(k in lower for k in ("id", "key", "fk")):
        return "int"
    if any(k in lower for k in ("date", "time", "at", "on")):
        return "datetime"
    if any(k in lower for k in ("is_", "has_", "flag", "enabled", "active")):
        return "boolean"
    if any(k in lower for k in ("count", "num", "total", "amount", "price", "qty")):
        return "float"
    return "string"


def _safe(name: str) -> str:
    return (
        name.replace(" ", "_")
            .replace(".", "_")
            .replace("-", "_")
            .replace(":", "_")
    )


def _mermaid_safe(name: str) -> str:
    """Remove characters that break Mermaid identifiers."""
    return (
        name.replace(" ", "_")
            .replace(".", "_")
            .replace("-", "_")
            .replace(":", "_")
            .replace("/", "_")
            .replace("\\", "_")
    )
