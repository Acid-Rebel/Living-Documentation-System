from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Dependency:
    source: str
    target: str
    dependency_type: str
    language: str
    metadata: Dict = field(default_factory=dict)
