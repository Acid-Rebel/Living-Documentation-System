from collections import defaultdict
import subprocess
import os


def wrap_mermaid(content: str) -> str:
    return f"```mermaid\n{content}\n```"


def render_dot_to_png(dot_content: str, png_path: str):
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
        f.write(dot_content)
        dot_path = f.name

    subprocess.run(
        ["dot", "-Tpng", dot_path, "-o", png_path],
        check=True
    )


def render_dependency_diagram_dot(graph):
    lines = ["digraph G {", "rankdir=LR;"]

    if not graph.dependencies:
        lines.append('"No Dependencies Found";')

    for src, dst in graph.dependencies:
        lines.append(f'"{src}" -> "{dst}";')

    return "\n".join(lines) + "\n}"




def render_class_diagram_dot(graph, focus_classes=None):
    lines = [
        "digraph G {",
        "rankdir=TB;",
        "node [shape=record];",
    ]

    visible_classes = set(graph.classes.keys())
    if focus_classes:
        visible_classes &= set(focus_classes)

    # ---------- Class nodes ----------
    for cls in visible_classes:
        info = graph.classes[cls]

        attrs = "\\l".join(sorted(info.attributes)) + "\\l" if info.attributes else ""
        methods = "\\l".join(sorted(info.methods)) + "\\l" if info.methods else ""

        label = f"{{{cls}|{attrs}|{methods}}}"
        lines.append(f'"{cls}" [label="{label}"];')

    # ---------- Inheritance (Child -> Parent) ----------
    for child, parent in graph.inheritance:
        if child in visible_classes and parent in visible_classes:
            lines.append(
                f'"{child}" -> "{parent}" [arrowhead=empty];'
            )

    # ---------- Composition ----------
    for owner, part in graph.composition:
        if owner in visible_classes and part in visible_classes:
            lines.append(
                f'"{owner}" -> "{part}" [arrowhead=diamond];'
            )

    # ---------- Usage ----------
    for src, dst in graph.usage:
        if src != dst and src in visible_classes and dst in visible_classes:
            lines.append(
                f'"{src}" -> "{dst}" [style=dashed];'
            )

    lines.append("}")
    return "\n".join(lines)



def render_call_diagram_dot(graph, focus_classes=None):
    lines = ["digraph G {", "rankdir=LR;"]

    calls = set(graph.calls) | set(graph.calls_heuristic)

    for src, dst in calls:
        if focus_classes and (src not in focus_classes or dst not in focus_classes):
            continue

        style = "solid" if (src, dst) in graph.calls else "dashed"
        lines.append(f'"{src}" -> "{dst}" [style={style}];')

    return "\n".join(lines) + "\n}"





def render_mermaid_to_png(md_path):
    png_path = md_path.replace(".md", ".png")

    subprocess.run(
        ["mmdc", "-i", md_path, "-o", png_path],
        check=True,
    )

    return png_path



def is_internal_module(module, all_modules):
    return module in all_modules

def group_calls_by_module(graph):
    """
    Groups classes by module for call diagrams.
    Includes modules even if calls are self-loops.
    """
    module_map = {}

    # Build class → module map
    class_to_module = {
        cls: info.module
        for cls, info in graph.classes.items()
        if info.module
    }

    # Collect modules with any call activity
    for src, dst in graph.calls:
        module = class_to_module.get(src)
        if not module:
            continue

        module_map.setdefault(module, set()).add(src)
        module_map[module].add(dst)

    return module_map



def group_classes_by_module(graph):
    modules = defaultdict(list)
    for cls, info in graph.classes.items():
        modules[info.module].append(cls)
    return modules


def render_class_diagram(graph, focus_classes=None):
    lines = ["classDiagram"]

    # ---------- Classes ----------
    for cls, info in graph.classes.items():
        if focus_classes and cls not in focus_classes:
            continue

        # Abstract marker
        if info.is_abstract:
            lines.append(f"class {cls} {{")
            lines.append("  <<abstract>>")
        else:
            lines.append(f"class {cls} {{")

        # Attributes
        for attr in sorted(info.attributes):
            visibility = "+"
            if attr.startswith("__"):
                visibility = "-"
            elif attr.startswith("_"):
                visibility = "#"

            lines.append(f"  {visibility}{attr}")

        # Methods
        for method in sorted(info.methods):
            visibility = "+"
            if method.startswith("__"):
                visibility = "-"
            elif method.startswith("_"):
                visibility = "#"

            lines.append(f"  {visibility}{method}()")

        lines.append("}")

    # ---------- Generalization / Specialization ----------
    for parent, child in graph.inheritance:
        if focus_classes and (parent not in focus_classes or child not in focus_classes):
            continue
        lines.append(f"{parent} <|-- {child}")

    # ---------- Composition ----------
    for owner, part in graph.composition:
        if focus_classes and (owner not in focus_classes or part not in focus_classes):
            continue
        lines.append(f"{owner} *-- {part} : composition")

    # ---------- Dependency (Usage) ----------
    for src, dst in graph.usage:
        if focus_classes and (src not in focus_classes or dst not in focus_classes):
            continue
        lines.append(f"{src} ..> {dst} : uses")

    return wrap_mermaid("\n".join(lines))





def render_dependency_diagram(graph):
    lines = ["graph TD"]

    internal_modules = {
        cls_info.module.split(".")[0]
        for cls_info in graph.classes.values()
        if cls_info.module
    }

    for src, dst in graph.dependencies:
        if src in internal_modules and dst in internal_modules:
            lines.append(f"{src} --> {dst}")

    return wrap_mermaid("\n".join(lines))




def render_call_diagram(graph, focus_classes=None):
    lines = ["graph LR"]

    for src, dst in graph.usage:
        if focus_classes:
            if src not in focus_classes and dst not in focus_classes:
                continue
        lines.append(f"{src} --> {dst}")

    return wrap_mermaid("\n".join(lines))


