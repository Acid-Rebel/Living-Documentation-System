"""
api_call_diagram.py
~~~~~~~~~~~~~~~~~~~
Generates API Call Diagrams showing the relationship between HTTP endpoints,
their handler functions, and the downstream functions/services they invoke.

Uses:
  - api_endpoint_detector.models.ApiEndpoint  (endpoint metadata)
  - semantic_extractor.models.Relation        (CALLS / IMPORTS relations)
  - diagram_generator.graph_model.DiagramGraph (class/call graph)

Public API
----------
  build_api_call_graph(artifacts, graph) -> List[dict]
  render_api_call_diagram_dot(api_call_graph) -> str
  render_api_call_diagram(api_call_graph) -> str   (Mermaid)
"""

from __future__ import annotations

from collections import defaultdict
from typing import List, Dict, Set

from diagram_generator.renderers import wrap_mermaid


# ---------------------------------------------------------------------------
# Data building
# ---------------------------------------------------------------------------

def build_api_call_graph(artifacts, graph) -> List[dict]:
    """
    Build a list of API call nodes from the analysis artifacts and diagram graph.

    Each node is a dict::

        {
            "endpoint":    str,   # e.g. "GET /api/users"
            "http_method": str,
            "path":        str,
            "handler":     str,   # function/method name
            "framework":   str,
            "file_path":   str,
            "class_name":  str | None,
            "callers":     List[str],   # functions called by the handler
        }

    Strategy
    --------
    1. Enumerate every detected API endpoint.
    2. Find all CALLS relations whose *source* matches the handler name.
    3. Also chase one level of indirection through IMPORTS so that service
       helpers imported into the handler file show up.
    4. Optionally fall back to graph.calls (AST-based call edges) when
       semantic relations are sparse.
    """
    # Pre-index semantic relations by source
    calls_by_source: Dict[str, List[str]] = defaultdict(list)
    imports_by_source: Dict[str, List[str]] = defaultdict(list)

    for rel in getattr(artifacts, "relations", []):
        if rel.relation_type in ("CALLS", "call"):
            calls_by_source[rel.source].append(rel.target)
        elif rel.relation_type in ("IMPORTS", "import"):
            imports_by_source[rel.source].append(rel.target)

    # AST-based calls fallback index
    ast_calls_by_source: Dict[str, List[str]] = defaultdict(list)
    for src, dst in graph.calls:
        ast_calls_by_source[src].append(dst)

    api_call_graph: List[dict] = []

    for ep in getattr(artifacts, "api_endpoints", []):
        handler = ep.handler_name or "<anonymous>"
        callers: List[str] = []

        # Candidates: bare name and qualified name
        candidates: Set[str] = {handler}
        if ep.class_name:
            candidates.add(f"{ep.class_name}.{handler}")

        seen_callers: Set[str] = set()
        for candidate in candidates:
            for callee in calls_by_source.get(candidate, []):
                if callee not in seen_callers:
                    seen_callers.add(callee)
                    callers.append(callee)

            # One level via imports
            for imported_mod in imports_by_source.get(candidate, []):
                for callee in calls_by_source.get(imported_mod, []):
                    if callee not in seen_callers:
                        seen_callers.add(callee)
                        callers.append(callee)

            # AST fallback
            for callee in ast_calls_by_source.get(candidate, []):
                if callee not in seen_callers:
                    seen_callers.add(callee)
                    callers.append(callee)

        api_call_graph.append(
            {
                "endpoint": f"{ep.http_method} {ep.path}",
                "http_method": ep.http_method,
                "path": ep.path,
                "handler": handler,
                "framework": ep.framework,
                "file_path": ep.file_path,
                "class_name": ep.class_name,
                "callers": callers,
            }
        )

    return api_call_graph


# ---------------------------------------------------------------------------
# DOT renderer
# ---------------------------------------------------------------------------

def render_api_call_diagram_dot(api_call_graph: List[dict]) -> str:
    """
    Render the API call graph as a Graphviz DOT digraph.

    Layout
    ------
    - API endpoint nodes: oval, filled blue-ish, labelled "METHOD /path"
    - Handler nodes:      rectangle, filled light-gray
    - Callee nodes:       rectangle, white
    - Edges: endpoint → handler (bold), handler → callee (dashed)
    """
    lines = [
        "digraph ApiCallDiagram {",
        "    rankdir=LR;",
        "    node [fontname=\"Helvetica\" fontsize=11];",
        "    edge [fontsize=10];",
        "",
        "    // --- Endpoint nodes ---",
    ]

    added_endpoints: Set[str] = set()
    added_handlers: Set[str] = set()
    added_callees: Set[str] = set()

    def ep_id(node: dict) -> str:
        return f"ep_{_safe(node['endpoint'])}"

    def handler_id(h: str) -> str:
        return f"handler_{_safe(h)}"

    def callee_id(c: str) -> str:
        return f"callee_{_safe(c)}"

    for node in api_call_graph:
        eid = ep_id(node)
        if eid not in added_endpoints:
            added_endpoints.add(eid)
            label = f"{node['http_method']}\\n{node['path']}"
            lines.append(
                f'    "{eid}" [label="{label}" shape=ellipse '
                f'style=filled fillcolor="#4A90D9" fontcolor=white];'
            )

        hid = handler_id(node["handler"])
        if hid not in added_handlers:
            added_handlers.add(hid)
            label = node["handler"]
            if node.get("class_name"):
                label = f"{node['class_name']}::{node['handler']}"
            lines.append(
                f'    "{hid}" [label="{label}" shape=box '
                f'style=filled fillcolor="#D3D3D3"];'
            )

        # endpoint → handler edge
        lines.append(
            f'    "{eid}" -> "{hid}" [penwidth=2 label="handles"];'
        )

        for callee in node["callers"]:
            cid = callee_id(callee)
            if cid not in added_callees:
                added_callees.add(cid)
                lines.append(
                    f'    "{cid}" [label="{callee}" shape=box style=rounded];'
                )
            lines.append(
                f'    "{hid}" -> "{cid}" [style=dashed label="calls"];'
            )

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mermaid renderer
# ---------------------------------------------------------------------------

def render_api_call_diagram(api_call_graph: List[dict]) -> str:
    """
    Render the API call graph as a Mermaid ``graph LR`` diagram.
    """
    lines = ["graph LR"]

    seen_edges: Set[tuple] = set()

    for node in api_call_graph:
        ep_label = f"{node['http_method']} {node['path']}"
        handler = node["handler"]
        if node.get("class_name"):
            handler_label = f"{node['class_name']}::{node['handler']}"
        else:
            handler_label = handler

        ep_node = f'EP_{_safe(node["endpoint"])}'
        handler_node = f'H_{_safe(handler)}'

        ep_def = f'{ep_node}["{ep_label}"]'
        handler_def = f'{handler_node}["{handler_label}"]'

        edge = (ep_node, handler_node)
        if edge not in seen_edges:
            seen_edges.add(edge)
            lines.append(f"    {ep_def} -->|handles| {handler_def}")

        for callee in node["callers"]:
            callee_node = f'C_{_safe(callee)}'
            callee_def = f'{callee_node}("{callee}")'
            edge2 = (handler_node, callee_node)
            if edge2 not in seen_edges:
                seen_edges.add(edge2)
                lines.append(f"    {handler_def} -.->|calls| {callee_def}")

    return wrap_mermaid("\n".join(lines))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe(name: str) -> str:
    """Convert a string to a safe identifier (no spaces, slashes, colons, etc.)."""
    return (
        name.replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(".", "_")
            .replace(":", "_")
            .replace("-", "_")
            .replace("(", "")
            .replace(")", "")
    )
