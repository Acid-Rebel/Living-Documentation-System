from typing import List, Dict, Any

class APIDocGenerator:
    """
    Generates documentation from extracted endpoints.
    """
    
    def generate_markdown(self, endpoints: List[Dict[str, Any]], diff: Dict[str, List[Dict[str, Any]]] = None) -> str:
        """
        Generates a Markdown string from the endpoints.
        """
        md = ["# API Documentation\n"]
        
        if diff:
            md.append("## Recent Changes\n")
            if diff['added']:
                md.append("### 🆕 Added Endpoints")
                for ep in diff['added']:
                    md.append(f"- `{ep['path']}` ({', '.join(ep['method'])})")
                md.append("")
            
            if diff['removed']:
                md.append("### ❌ Removed Endpoints")
                for ep in diff['removed']:
                    md.append(f"- `{ep['path']}` ({', '.join(ep['method'])})")
                md.append("")
                
            if diff['deprecated']:
                md.append("### ⚠️ Deprecated Endpoints")
                for ep in diff['deprecated']:
                    md.append(f"- `{ep['path']}` ({', '.join(ep['method'])})")
                md.append("")

        md.append("## Endpoints\n")
        
        # Group by path to handle multiple methods per path if needed? 
        # For now, just list them.
        
        for ep in endpoints:
            methods = ", ".join(ep.get('method', ['GET']))
            path = ep.get('path', '/')
            name = ep.get('name', 'Unknown')
            desc = ep.get('description', 'No description provided.')
            
            status_icon = ""
            if diff:
                # Check status
                # (This is O(N^2) effectively if lists are large, but fine for now)
                # Ideally we'd have a map, but sticking to simple logic.
                if any(e['path'] == path and e['method'] == ep['method'] for e in diff.get('added', [])):
                     status_icon = "🆕 "
                elif any(e['path'] == path and e['method'] == ep['method'] for e in diff.get('deprecated', [])):
                     status_icon = "⚠️ "
            
            md.append(f"### {status_icon}{methods} {path}")
            md.append(f"**Name:** `{name}`\n")
            md.append(f"{desc}\n")
            md.append("---\n")
            
        return "\n".join(md)
