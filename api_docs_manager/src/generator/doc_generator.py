from typing import List
from ..parser.base import Endpoint

class DocGenerator:
    def generate_markdown(self, endpoints: List[Endpoint]) -> str:
        lines = ["# API Documentation\n\n"]
        
        # Table of Contents
        lines.append("## Table of Contents")
        for ep in endpoints:
             anchor = f"{ep.method}-{ep.path}".lower().replace("/", "").replace(":", "")
             lines.append(f"- [{ep.method} {ep.path}](#{anchor})")
        lines.append("\n")

        # Details
        lines.append("## Endpoints\n")
        for ep in endpoints:
            lines.append(f"### {ep.method} {ep.path}")
            lines.append(f"{ep.description}\n")
            lines.append(f"**Source:** `{os.path.basename(ep.source_file)}:{ep.line_number}`\n")
            lines.append("---\n")
            
        return "\n".join(lines)

import os # Missing import added
