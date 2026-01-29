import os
from code_parser.language_detection import detect_language
from code_parser.parser_manager import get_parser  # we will add this
from diagram_generator.graph_model import DiagramGraph
from diagram_generator.ast_traverser import traverse
from diagram_generator.renderers import (
    render_class_diagram,
    render_dependency_diagram,
    render_call_diagram
)


OUTPUT_DIR = "diagram_generator/output"

def generate_diagrams(file_path: str):
    language = detect_language(file_path)
    parser = get_parser(language)

    with open(file_path, "r") as f:
        source_code = f.read()

    raw_ast = parser.parse(source_code)
    unified_ast = parser.normalize(raw_ast)

    graph = DiagramGraph()
    traverse(unified_ast, graph)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(f"{OUTPUT_DIR}/class_diagram.md", "w") as f:
        f.write(render_class_diagram(graph))

    with open(f"{OUTPUT_DIR}/dependency_diagram.md", "w") as f:
        f.write(render_dependency_diagram(graph))

    with open(f"{OUTPUT_DIR}/call_diagram.md", "w") as f:
        f.write(render_call_diagram(graph))

    print("✅ Diagrams generated successfully.")
