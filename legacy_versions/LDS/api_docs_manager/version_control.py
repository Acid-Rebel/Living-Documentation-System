import json
import os
from typing import List, Dict, Any, Tuple

class APIVersionManager:
    """
    Manages API versions and detects changes between extractions.
    """
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def load_previous_version(self) -> List[Dict[str, Any]]:
        """Loads the last saved API definition."""
        if not os.path.exists(self.storage_path):
            return []
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_version(self, endpoints: List[Dict[str, Any]]):
        """Saves the current API definition."""
        with open(self.storage_path, 'w') as f:
            json.dump(endpoints, f, indent=2)

    def diff_versions(self, current_endpoints: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Compares current endpoints with the previous version.
        Returns a dictionary with keys: 'added', 'removed', 'unchanged', 'deprecated'.
        """
        previous_endpoints = self.load_previous_version()
        
        prev_map = {self._get_signature(ep): ep for ep in previous_endpoints}
        curr_map = {self._get_signature(ep): ep for ep in current_endpoints}
        
        added = []
        removed = []
        unchanged = []
        deprecated = []
        
        for sig, ep in curr_map.items():
            if sig not in prev_map:
                added.append(ep)
            else:
                unchanged.append(ep)
                if 'deprecated' in (ep.get('description', '') or '').lower():
                    deprecated.append(ep)
        
        for sig, ep in prev_map.items():
            if sig not in curr_map:
                removed.append(ep)
                
        return {
            'added': added,
            'removed': removed,
            'unchanged': unchanged,
            'deprecated': deprecated
        }

    def _get_signature(self, endpoint: Dict[str, Any]) -> str:
        """Generates a unique signature for an endpoint (method + path)."""
        methods = sorted(endpoint.get('method', ['GET']))
        path = endpoint.get('path', '/')
        return f"{','.join(methods)} {path}"
