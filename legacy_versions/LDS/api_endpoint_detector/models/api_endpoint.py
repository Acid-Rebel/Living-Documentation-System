from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ApiEndpoint:
    path: str
    http_method: str
    handler_name: str
    class_name: Optional[str]
    language: str
    file_path: str
    framework: str
    metadata: Dict = field(default_factory=dict)

