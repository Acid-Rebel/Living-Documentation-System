import json
import os
from typing import Dict, Any, List
from pathlib import Path

DEFAULT_CONFIG = {
    "projectType": "auto",
    "template": "auto",
    "sections": {
        "overview": True,
        "setup": True,
        "features": True,
        "usage": True,
        "structure": True,
        "contributing": True,
        "license": True
    },
    "versionTracking": True,
    "autoUpdate": True,
    "outputPath": "./README.md",
    "excludeSections": [],
    "metadata": {
        "author": "",
        "license": "MIT"
    }
}

class Config:
    def __init__(self, config_path: str = ".readmerc"):
        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config = DEFAULT_CONFIG.copy()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    self._deep_update(config, user_config)
            except json.JSONDecodeError:
                print(f"Warning: Malformed {self.config_path}. Using defaults.")
        return config

    def _deep_update(self, base: Dict[str, Any], update: Dict[str, Any]):
        for key, value in update.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __getitem__(self, item):
        return self.data[item]

    @property
    def sections(self) -> Dict[str, bool]:
        return self.data.get("sections", {})

    @property
    def project_type(self) -> str:
        return self.data.get("projectType", "auto")

    @property
    def template(self) -> str:
        return self.data.get("template", "auto")
