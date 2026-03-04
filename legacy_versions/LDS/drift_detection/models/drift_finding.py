from dataclasses import dataclass, field
from typing import Any, Dict

from .drift_severity import DriftSeverity


@dataclass
class DriftFinding:
    drift_type: str
    description: str
    severity: DriftSeverity
    metadata: Dict[str, Any] = field(default_factory=dict)
