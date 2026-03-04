"""
arch_flow_diagram.py
~~~~~~~~~~~~~~~~~~~~
Generates Architecture Flow Diagrams showing high-level system layers and
the directional data/control flows between them.

Layer detection uses heuristic keyword matching on module/class names to
assign nodes to one of the predefined architectural layers:

    API / Controller  →  HTTP entry points (endpoints, controllers, routes)
    Service / Logic   →  Business logic (services, managers, use_cases, handlers)
    Repository / DAO  →  Data access (repos, daos, stores, gateways)
    Model / Entity    →  Data models (models, entities, schemas, domain)
    External          →  Third-party or infrastructure (client, adapter, integration)
    Utility           →  Cross-cutting helpers (utils, helpers, common, shared)

Public API
----------
  build_arch_graph(artifacts, graph) -> dict
  render_arch_flow_diagram_dot(arch_graph) -> str
  render_arch_flow_diagram(arch_graph) -> str   (Mermaid)
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Set, Tuple

from diagram_generator.renderers import wrap_mermaid


# ---------------------------------------------------------------------------
# Layer definitions  (ordered by typical dependency direction: top → bottom)
# ---------------------------------------------------------------------------

LAYERS: List[Tuple[str, List[str]]] = [
    ("API",        ["controller", "route", "endpoint", "view", "api", "resource", "handler"]),
    ("Service",    ["service", "manager", "usecase", "use_case", "logic", "processor", "workflow"]),
    ("Repository", ["repo", "repository", "dao", "store", "gateway", "query", "finder"]),
    ("Model",      ["model", "entity", "schema", "domain", "dto", "record"]),
    ("External",   ["client", "adapter", "integration", "connector", "provider", "proxy"]),
    ("Utility",    ["util", "helper", "common", "shared", "mixin", "base", "abstract"]),
]

# Colours for DOT subgraph clusters (one per layer)
LAYER_COLOURS: Dict[str, str] = {
    "API":        "#AED6F1",
    "Service":    "#A9DFBF",
    "Repository": "#FAD7A0",
    "Model":      "#D7BDE2",
    "External":   "#F5CBA7",
    "Utility":    "#CCD1D1",
    "Other":      "#EAECEE",
}


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_arch_graph(artifacts, graph) -> dict:
    """
    Build an architecture flow graph.

    Returns a dict::

        {
            "layers":  Dict[str, List[str]],    # layer → [module/class names]
            "nodes":   Set[str],                # all unique node names
            "flows":   List[(src_layer, dst_layer, count)],
            "api_entries": List[str],           # endpoint labels from api_endpoints
        }

    Algorithm
    ---------
    1. Classify every class/module from graph.classes into a layer using
       the LAYERS keyword table.
    2. Walk graph.dependencies: for each (src_module, dst_module) pair,
       look up the layers of src and dst and emit a layer→layer flow.
    3. Collect API endpoints as special "entry point" annotations.
    """
    # --- Step 1: Classify nodes ---
    class_to_layer: Dict[str, str] = {}
    layers: Dict[str, List[str]] = defaultdict(list)

    all_names = list(graph.classes.keys())

    # Also pull module-level names from dependencies
    for src, dst in graph.dependencies:
        if src not in all_names:
            all_names.append(src)
        if dst not in all_names:
            all_names.append(dst)

    for name in all_names:
        layer = _classify(name)
        class_to_layer[name] = layer
        layers[layer].append(name)

    # --- Step 2: Derive inter-layer flows ---
    flow_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    for src, dst in graph.dependencies:
        src_layer = class_to_layer.get(src, "Other")
        dst_layer = class_to_layer.get(dst, "Other")
        if src_layer != dst_layer:
            flow_counts[(src_layer, dst_layer)] += 1

    # Also consider call relations for flow
    for src, dst in graph.calls:
        src_layer = class_to_layer.get(src, "Other")
        dst_layer = class_to_layer.get(dst, "Other")
        if src_layer != dst_layer:
            flow_counts[(src_layer, dst_layer)] += 1

    flows = [
        (src, dst, count)
        for (src, dst), count in flow_counts.items()
    ]

    # --- Step 3: API entry points ---
    api_entries: List[str] = []
    for ep in getattr(artifacts, "api_endpoints", []):
        label = f"{ep.http_method} {ep.path}"
        if label not in api_entries:
            api_entries.append(label)

    return {
        "layers": dict(layers),
        "nodes": set(all_names),
        "flows": flows,
        "api_entries": api_entries,
        "class_to_layer": class_to_layer,
    }


# ---------------------------------------------------------------------------
# DOT renderer
# ---------------------------------------------------------------------------

def render_arch_flow_diagram_dot(arch_graph: dict) -> str:
    """
    Render the architecture flow graph as a Graphviz DOT digraph.

    Each architectural layer becomes a ``subgraph cluster``.
    Edges between clusters carry a label showing the flow count.
    """
    layers = arch_graph["layers"]
    flows = arch_graph["flows"]
    api_entries = arch_graph["api_entries"]

    lines = [
        "digraph ArchFlowDiagram {",
        "    rankdir=TB;",
        "    compound=true;",
        "    node [fontname=\"Helvetica\" fontsize=11];",
        "    edge [fontname=\"Helvetica\" fontsize=10];",
        "",
    ]

    # API entry points cluster
    if api_entries:
        lines.append("    subgraph cluster_entry {")
        lines.append("        label=\"API Entry Points\";")
        lines.append("        style=filled;")
        lines.append(f"        fillcolor=\"#D5E8D4\";")
        for ep in api_entries[:20]:  # cap to avoid huge diagrams
            safe = _safe(ep)
            lines.append(f'        "entry_{safe}" [label="{ep}" shape=parallelogram];')
        lines.append("    }")
        lines.append("")

    # One subgraph per layer
    layer_rep: Dict[str, str] = {}  # layer → a representative node ID for ltail/lhead
    for layer, members in layers.items():
        if not members:
            continue
        colour = LAYER_COLOURS.get(layer, LAYER_COLOURS["Other"])
        safe_layer = _safe(layer)
        lines.append(f"    subgraph cluster_{safe_layer} {{")
        lines.append(f"        label=\"{layer}\";")
        lines.append(f"        style=filled;")
        lines.append(f"        fillcolor=\"{colour}\";")

        for i, member in enumerate(members):
            safe_m = _safe(member)
            lines.append(f'        "{safe_layer}_{safe_m}" [label="{member}"];')
            if i == 0:
                layer_rep[layer] = f"{safe_layer}_{safe_m}"

        lines.append("    }")
        lines.append("")

    # Inter-layer flow edges (use ltail/lhead for cluster edges)
    for src_layer, dst_layer, count in flows:
        src_rep = layer_rep.get(src_layer)
        dst_rep = layer_rep.get(dst_layer)
        if not src_rep or not dst_rep:
            continue
        label = f"{count} flow{'s' if count != 1 else ''}"
        lines.append(
            f'    "{src_rep}" -> "{dst_rep}" '
            f'[ltail=cluster_{_safe(src_layer)} lhead=cluster_{_safe(dst_layer)} '
            f'label="{label}" penwidth={min(1 + count * 0.3, 4):.1f}];'
        )

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mermaid renderer
# ---------------------------------------------------------------------------

def render_arch_flow_diagram(arch_graph: dict) -> str:
    """
    Render the architecture flow graph as a Mermaid ``graph TD``.

    Each layer becomes a Mermaid ``subgraph`` block.
    """
    layers = arch_graph["layers"]
    flows = arch_graph["flows"]
    api_entries = arch_graph["api_entries"]

    lines = ["graph TD"]

    # API entry points subgraph
    if api_entries:
        lines.append("    subgraph ENTRY[\"API Entry Points\"]")
        for ep in api_entries[:15]:
            node_id = f"EP_{_mermaid_safe(ep)}"
            lines.append(f"        {node_id}[\"{ep}\"]")
        lines.append("    end")
        lines.append("")

    # Layer subgraphs
    layer_node_map: Dict[str, str] = {}  # layer → first node id
    for layer, members in layers.items():
        if not members:
            continue
        safe_layer = _mermaid_safe(layer)
        lines.append(f"    subgraph {safe_layer}[\"{layer} Layer\"]")
        for i, member in enumerate(members):
            node_id = f"{safe_layer}_{_mermaid_safe(member)}"
            lines.append(f"        {node_id}[\"{member}\"]")
            if i == 0:
                layer_node_map[layer] = node_id
        lines.append("    end")
        lines.append("")

    # Flow edges between layers
    seen_edges: Set[Tuple[str, str]] = set()
    for src_layer, dst_layer, count in flows:
        src_node = layer_node_map.get(src_layer)
        dst_node = layer_node_map.get(dst_layer)
        if not src_node or not dst_node:
            continue
        edge = (src_layer, dst_layer)
        if edge in seen_edges:
            continue
        seen_edges.add(edge)
        lines.append(f"    {src_node} -->|\"{count} flows\"| {dst_node}")

    return wrap_mermaid("\n".join(lines))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify(name: str) -> str:
    """
    Return the architectural layer for a class/module name using keyword matching.
    Checks the last segment of a dotted module path for the best signal.
    """
    # Use the last component of dotted paths for matching
    parts = name.replace("\\", ".").replace("/", ".").split(".")
    tail = parts[-1].lower()
    full_lower = name.lower()

    for layer, keywords in LAYERS:
        for kw in keywords:
            if kw in tail:
                return layer
        # Also try full path for patterns like "app.api.routes"
        for kw in keywords:
            if f".{kw}" in full_lower or full_lower.startswith(kw):
                return layer

    return "Other"


def _safe(name: str) -> str:
    return (
        name.replace(" ", "_")
            .replace(".", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace("-", "_")
            .replace(":", "_")
            .replace("(", "")
            .replace(")", "")
    )


def _mermaid_safe(name: str) -> str:
    return (
        name.replace(" ", "_")
            .replace(".", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace("-", "_")
            .replace(":", "_")
            .replace("(", "")
            .replace(")", "")
    )
