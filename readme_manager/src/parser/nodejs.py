from .base import BaseParser
from typing import Dict, Any
import json
import os

class NodeParser(BaseParser):
    def detect(self) -> bool:
        return os.path.exists(os.path.join(self.project_root, "package.json"))

    def parse(self) -> Dict[str, Any]:
        data = {
            "language": "JavaScript/TypeScript",
            "frameworks": [],
            "dependencies": [],
            "dev_dependencies": [],
            "scripts": {},
            "engines": {}
        }
        
        content = self.read_file("package.json")
        if not content:
            return data

        try:
            pkg = json.loads(content)
            data["name"] = pkg.get("name")
            data["version"] = pkg.get("version")
            data["description"] = pkg.get("description")
            data["scripts"] = pkg.get("scripts", {})
            data["engines"] = pkg.get("engines", {})
            
            deps = pkg.get("dependencies", {})
            dev_deps = pkg.get("devDependencies", {})
            
            data["dependencies"] = list(deps.keys())
            data["dev_dependencies"] = list(dev_deps.keys())
            
            # Simple framework detection
            all_deps = list(deps.keys()) + list(dev_deps.keys())
            if "react" in all_deps: data["frameworks"].append("React")
            if "vue" in all_deps: data["frameworks"].append("Vue")
            if "next" in all_deps: data["frameworks"].append("Next.js")
            if "express" in all_deps: data["frameworks"].append("Express")
            if "typescript" in all_deps: data["language"] = "TypeScript"

        except json.JSONDecodeError:
            pass
            
        return data
