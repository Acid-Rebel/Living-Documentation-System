import json
import os
from typing import Dict, Any, List

DEFAULT_CONFIG = {
    "projectName": "Architecture Docs",
    "sourceDir": "./src",
    "outputDir": "./docs/architecture",
    "layers": {
        "presentation": ["controllers", "routers", "views", "api", "routes"],
        "business_logic": ["services", "usecases", "domain", "logic", "models"],
        "data_access": ["repositories", "dao", "db", "database", "entities"],
        "infrastructure": ["infrastructure", "utils", "config", "shared"]
    },
    "patterns": ["layered", "mvc", "microservices"],
    "ignoredFolders": ["node_modules", "venv", ".git", "__pycache__", "dist", "build"]
}

class Config:
    def __init__(self, config_path: str = ".archdocsrc"):
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
