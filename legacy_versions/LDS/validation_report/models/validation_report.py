from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from drift_detection.models import DriftFinding


@dataclass
class ValidationReport:
    summary: Dict[str, Any]
    findings: List[DriftFinding]
    generated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
