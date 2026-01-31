from typing import Dict, Any, List
from ..visualizer.mermaid_renderer import MermaidRenderer

class DocGenerator:
    def __init__(self):
        self.visualizer = MermaidRenderer()

    def generate(self, structure: Dict[str, Any], dependency_graph: Dict[str, Any], patterns: List[Dict[str, Any]] = None) -> str:
        lines = ["# Architecture Documentation\n\n"]
        
        if patterns:
            lines.append("## Detected Architectural Patterns\n")
            for p in patterns:
                lines.append(f"### {p['name']} (Confidence: {p['confidence']})")
                lines.append(f"{p['description']}\n")
        
        # 1. Layer Analysis
        lines.append("## System Layers\n")
        layers = structure.get("layers", {})
        has_layers = False
        
        for layer, components in layers.items():
            if components:
                has_layers = True
                lines.append(f"### {layer.title()} Layer")
                lines.append("**Components detected:**")
                for comp in components:
                    lines.append(f"- `{comp['name']}` ({comp['path']})")
                lines.append("")
        
        if not has_layers:
            lines.append("_No standard architectural layers detected._\n")

        # 2. Diagrams
        lines.append("## Architectural Diagrams\n")
        
        if has_layers:
            lines.append("### High-Level Layer View")
            lines.append("```mermaid")
            lines.append(self.visualizer.render_layer_diagram(structure))
            lines.append("```\n")

        lines.append("### Component Dependency Graph")
        lines.append("_Partial view of file dependencies_")
        lines.append("```mermaid")
        lines.append(self.visualizer.render_dependency_graph(dependency_graph))
        lines.append("```\n")

        return "\n".join(lines)
