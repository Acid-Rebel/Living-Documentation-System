from typing import Dict, Any, List

class PatternDetector:
    def detect(self, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        patterns = []
        layers = structure.get("layers", {})
        
        # 1. Layered Architecture Detection
        # Heuristic: Presence of specific layers and flow
        present_layers = [L for L, comps in layers.items() if comps]
        
        is_layered = "presentation" in present_layers and "data_access" in present_layers
        if is_layered:
            confidence = "High" if "business_logic" in present_layers else "Medium"
            patterns.append({
                "name": "Layered Architecture",
                "confidence": confidence,
                "description": "Separation of concerns into Presentation, Business Logic, and Data Access layers."
            })
            
        # 2. MVC Detection
        # Heuristic: Controllers + Models + Views
        # In our layer config, Views are in Presentation, Models in Business/Data
        # We need to look at component names
        all_components = []
        for comps in layers.values():
            all_components.extend([c['name'].lower() for c in comps])
            
        has_controllers = any("controller" in c for c in all_components)
        has_models = any("model" in c for c in all_components)
        has_views = any("view" in c for c in all_components)
        
        if has_controllers and has_models:
            confidence = "High" if has_views else "Medium"
            patterns.append({
                "name": "MVC (Model-View-Controller)",
                "confidence": confidence,
                "description": "Application structure follows Model-View-Controller pattern."
            })

        return patterns
