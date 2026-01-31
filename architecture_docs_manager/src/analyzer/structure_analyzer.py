import os
from typing import Dict, List, Any
from ..config.config import Config

class StructureAnalyzer:
    def __init__(self, config: Config):
        self.config = config
        self.layers = config.get("layers")
        self.ignored = config.get("ignoredFolders")

    def analyze(self, root_path: str) -> Dict[str, Any]:
        structure = {
            "layers": {},
            "components": [],
            "unknown": []
        }
        
        # Initialize layers
        for layer in self.layers:
            structure["layers"][layer] = []

        abs_root = os.path.abspath(root_path)

        for root, dirs, files in os.walk(abs_root):
            # Prune ignored
            dirs[:] = [d for d in dirs if d not in self.ignored]
            
            # Determine current folder name relative to root
            rel_path = os.path.relpath(root, abs_root)
            if rel_path == ".": continue
            
            # Check if this folder belongs to a layer
            folder_name = os.path.basename(root)
            assigned_layer = None
            
            for layer_name, patterns in self.layers.items():
                if folder_name.lower() in patterns:
                    assigned_layer = layer_name
                    break
            
            if assigned_layer:
                # Treat subfolders as components of this layer
                structure["layers"][assigned_layer].append({
                    "path": rel_path,
                    "name": folder_name,
                    "type": "LayerComponent"
                })
            else:
                 # Check if parent was in a layer? for now simple matching
                 pass
        
        return structure
