import os
import re
import sys
from typing import List

# Import existing tool modules
# Assuming they are in the path or relative
try:
    from code_parser.parser_manager import parse_source_file
    from semantic_extractor.analyzer_manager import AnalyzerManager
    SEMANTIC_ANALYSIS_AVAILABLE = True

except ImportError:
    SEMANTIC_ANALYSIS_AVAILABLE = False

class FeatureExtractor:
    def __init__(self, project_root: str):
        self.project_root = project_root
        if SEMANTIC_ANALYSIS_AVAILABLE:
            self.analyzer = AnalyzerManager()

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
        
        return sorted(list(set(features)))

    def _scan_file(self, file_path: str) -> List[str]:
        found = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 1. Regex - Always run for comments
            matches = re.findall(r'[@]feature\s+(.*)', content)
            found.extend([m.strip() for m in matches])
            
            # 2. Semantic Analysis
            if SEMANTIC_ANALYSIS_AVAILABLE and file_path.endswith(".py"):
                # Use powerful semantic extraction for Python (since parser supports it)
                ast_node = parse_source_file(file_path, content)
                if ast_node:
                    analysis = self.analyzer.analyze(ast_node, file_path, "python")
                    symbols = analysis.get("symbols", [])
                    for sym in symbols:
                        # Extract High-Level classes as features
                        if sym.symbol_type == "class":
                            name = sym.name
                            if "Service" in name or "Controller" in name or "Manager" in name:
                                readable = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
                                found.append(f"{readable} logic")
            
            # Fallback for other languages or if semantic failed
            elif "class " in content:
                 class_matches = re.findall(r'class\s+([A-Z]\w+Service)', content)
                 for c in class_matches:
                     name = re.sub(r'([a-z])([A-Z])', r'\1 \2', c)
                     found.append(f"{name} logic")

        except Exception as e:
            # print(f"Error scanning {file_path}: {e}")
            pass
        return found
