from typing import Dict, Any, List

class Classifier:
    def classify(self, metadata: Dict[str, Any]) -> str:
        """
        Determines the project type based on extracted metadata.
        Returns: web-app, library, cli, or generic.
        """
        deps = [d.lower() for d in metadata.get("dependencies", [])]
        dev_deps = [d.lower() for d in metadata.get("dev_dependencies", [])]
        frameworks = [f.lower() for f in metadata.get("frameworks", [])]
        scripts = metadata.get("scripts", {})
        
        # Merge all keywords for checking
        all_keywords = set(deps + dev_deps + frameworks)
        
        # Check for CLI
        if "commander" in all_keywords or "yargs" in all_keywords or "cobra" in all_keywords or "click" in all_keywords or "argparse" in all_keywords:
            if "bin" in metadata or any("bin" in s for s in scripts.keys()): 
                 return "cli"

        # Check for Web App
        web_indicators = {"react", "vue", "next", "express", "django", "flask", "fastapi", "gin", "echo"}
        if any(w in all_keywords for w in web_indicators):
            return "web-app"

        # Check for Library (heuristic: main entry point, no start script)
        if "start" not in scripts and "dev" not in scripts:
            # Weak signal, but if it has a name and version but no app-like scripts
            return "library"
            
        return "generic"
