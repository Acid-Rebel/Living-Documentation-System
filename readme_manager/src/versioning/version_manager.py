import os
import re
from typing import Dict, Any

class VersionManager:
    def __init__(self, readme_path: str):
        self.readme_path = readme_path

    def get_current_metadata(self) -> Dict[str, Any]:
        """Extracts YAML frontmatter from existing README."""
        if not os.path.exists(self.readme_path):
            return {}
        
        with open(self.readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex for frontmatter
        match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            # Parse YAML manually to avoid PyYAML dep, or assume simple key-value
            yaml_content = match.group(1)
            data = {}
            for line in yaml_content.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip()
            return data
        return {}

    def has_changes(self, new_metadata: Dict[str, Any]) -> bool:
        current = self.get_current_metadata()
        # Simple version check
        return current.get("version") != new_metadata.get("version")
