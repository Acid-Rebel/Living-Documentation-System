from collections import defaultdict
import subprocess
import os


def wrap_mermaid(content: str) -> str:
    return f"```mermaid\n{content}\n```"


def render_dot_to_png(dot_content: str, png_path: str):
    """
    Renders DOT content to PNG using Python graphviz library.
    This requires GraphViz executables to be installed on the system.
    """
    import graphviz
    import os
    
    # Ensure GraphViz is in PATH for Windows
    if os.name == 'nt':
        graphviz_path = r"C:\Program Files\Graphviz\bin"
        if os.path.exists(graphviz_path) and graphviz_path not in os.environ["PATH"]:
            os.environ["PATH"] += os.pathsep + graphviz_path

    # Get directory and filename without extension

    directory = os.path.dirname(png_path) or '.'
    filename = os.path.basename(png_path).replace('.png', '')
    
    # Create Source object and render
    source = graphviz.Source(dot_content)
    source.render(filename=filename, directory=directory, format='png', cleanup=True)



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

    # ---------- Composition (Owner <>- Part) ----------
    for owner, part in graph.composition:
        if owner in visible_classes and part in visible_classes:
            mult = graph.multiplicity.get((owner, part), "")
            label_attr = f'taillabel="{mult}"' if mult else ""
            # Diamond on Owner (Tail), Arrow points to Part
            lines.append(
                f'"{owner}" -> "{part}" [dir=back arrowtail=diamond {label_attr}];'
            )

    # ---------- Aggregation (Owner o- Part) ----------
    for owner, part in graph.aggregation:
        if owner in visible_classes and part in visible_classes:
            mult = graph.multiplicity.get((owner, part), "")
            label_attr = f'taillabel="{mult}"' if mult else ""
            lines.append(
                f'"{owner}" -> "{part}" [dir=back arrowtail=odiamond {label_attr}];'
            )

    # ---------- Usage ----------
    for src, dst in graph.usage:
        if src != dst and src in visible_classes and dst in visible_classes:
            lines.append(
                f'"{src}" -> "{dst}" [style=dashed];'
            )

    lines.append("}")
    return "\n".join(lines)



def render_api_diagram_dot(endpoints):
    lines = [
        "digraph G {",
        "rankdir=LR;",
        "node [shape=record];",
    ]

    # Group by class or file
    groups = defaultdict(list)
    for ep in endpoints:
        key = ep.class_name if ep.class_name else f"File: {os.path.basename(ep.file_path)}"
        groups[key].append(ep)

    for group, items in groups.items():
        # Create a record for the controller
        rows = [f"{{ {group} | | }}"]
        for item in items:
            rows.append(f"{{ {item.http_method} | {item.path} | {item.handler_name} }}")
        
        label = "|".join(rows)
        # Escape simplified
        label = label.replace("{", "\\{").replace("}", "\\}")
        # Graphviz record needs nested braces? 
        # Actually simplest is HTML labels or just record with fields
        # Let's try simple record: { Class | Method Path... | ... }
        # { Class | { GET /foo | handler } | { POST /bar | handler } }
        
        inner_rows = []
        for item in items:
             inner_rows.append(f"{{{item.http_method}|{item.path}|{item.handler_name}}}")
        
        inner_str = "|".join(inner_rows)
        label = f"{{{group}|{{{inner_str}}}}}"
        
        safe_id = group.replace(" ", "_").replace(".", "_").replace(":", "")
        lines.append(f'"{safe_id}" [label="{label}"];')

    lines.append("}")
    return "\n".join(lines)


def render_call_diagram_dot(graph, focus_classes=None):
    lines = ["digraph G {", "rankdir=LR;"]

    # FIX: Use AST calls ONLY
    calls = set(graph.calls)

    for src, dst in calls:
        if focus_classes and (src not in focus_classes or dst not in focus_classes):
            continue

        # AST calls are solid
        lines.append(f'"{src}" -> "{dst}" [style=solid];')

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


