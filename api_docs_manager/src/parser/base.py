from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Endpoint:
    method: str
    path: str
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    responses: Dict[str, Any] = field(default_factory=dict)
    auth_required: bool = False
    source_file: str = ""
    line_number: int = 0

class BaseParser:
    def parse(self, project_root: str) -> List[Endpoint]:
        raise NotImplementedError
