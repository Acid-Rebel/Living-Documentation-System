import os
import re
from typing import List

class FeatureExtractor:
    def __init__(self, project_root: str):
        self.project_root = project_root

    def extract_features(self) -> List[str]:
        features = []
        # Walk through files
        for root, dirs, files in os.walk(self.project_root):
            if "node_modules" in dirs: 
                dirs.remove("node_modules")
            if "venv" in dirs: 
                dirs.remove("venv")
            if ".git" in dirs: 
                dirs.remove(".git")
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.go', '.java')):
                    path = os.path.join(root, file)
                    features.extend(self._scan_file(path))
        
        return list(set(features))

    def _scan_file(self, file_path: str) -> List[str]:
        found = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for @feature tag matching // @feature or # @feature
                matches = re.findall(r'[@]feature\s+(.*)', content)
                found.extend([m.strip() for m in matches])
                
                # Heuristics for "Services" or "Controllers"
                if "class " in content:
                     class_matches = re.findall(r'class\s+([A-Z]\w+Service)', content)
                     for c in class_matches:
                         # Simple space insertion
                         name = re.sub(r'([a-z])([A-Z])', r'\1 \2', c)
                         found.append(f"{name} logic")

        except Exception:
            pass
        return found
