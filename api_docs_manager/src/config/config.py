import json
import os
from typing import Dict, Any

DEFAULT_CONFIG = {
    "projectName": "API Docs",
    "version": "1.0.0",
    "outputDir": "./docs",
    "parsers": {
        "express": True,
        "fastapi": True,
        "openapi": True
    },
    "generator": {
        "examples": ["curl", "javascript", "python", "go"]
    }
}

class Config:
    def __init__(self, config_path: str = ".apidocsrc"):
        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config = DEFAULT_CONFIG.copy()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except json.JSONDecodeError:
                pass
        return config

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
