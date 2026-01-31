from typing import Dict, List, Any

class MermaidRenderer:
    def render_layer_diagram(self, structure: Dict[str, Any]) -> str:
        lines = ["graph TD"]
        layers = structure.get("layers", {})
        
        # Define subgraphs for layers
        for layer_name, components in layers.items():
            if not components: continue
            lines.append(f"    subgraph {layer_name.title()}")
            for comp in components:
                # Sanitize name
                node_id = comp['name'].replace(" ", "_").replace("-", "_")
                label = comp['name']
                lines.append(f"        {node_id}[{label}]")
            lines.append("    end")
            
        # Add edges based on typical layer flow (Presentation -> Business -> Data)
        # This is hardcoded for the diagram visual logic unless we have real dependency data mapped to layers
        lines.append("    Presentation --> Business_Logic")
        lines.append("    Business_Logic --> Data_Access")
        
        return "\n".join(lines)

    def render_dependency_graph(self, dependency_graph: Dict[str, List[str]]) -> str:
        lines = ["graph LR"]
        count = 0
        limit = 50 # Limit to prevent huge diagrams
        
        node_map = {}
        
        for file, imports in dependency_graph.items():
            fname = file.replace("\\", "/").split("/")[-1]
            src_id = f"N{hash(fname) % 10000}"
            node_map[fname] = src_id
            
            # Add node def if needed, but usually edges suffice
            
            for imp in imports:
                # Clean import
                imp_name = imp.split("/")[-1]
                dest_id = f"N{hash(imp_name) % 10000}"
                
                lines.append(f"    {src_id}[{fname}] --> {dest_id}[{imp_name}]")
                count += 1
                if count > limit: break
            if count > limit: break
            
        return "\n".join(lines)
import typing
# Fix for Any
Any = typing.Any
