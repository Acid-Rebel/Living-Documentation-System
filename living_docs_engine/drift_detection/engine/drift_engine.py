from typing import Iterable, List, Optional, Tuple

from analysis_store.models import AnalysisArtifacts

from drift_detection.engine.base_rule import BaseDriftRule
from drift_detection.engine.rules.api_drift_rules import (
    EndpointMethodChangedRule,
    EndpointPathChangedRule,
    EndpointRemovedRule,
)
from drift_detection.engine.rules.dependency_drift_rules import (
    DependencyAddedRule,
    DependencyRemovedRule,
)
from drift_detection.engine.rules.structural_drift_rules import (
    ApiHandlerMissingRule,
    SymbolReferenceMissingDefinitionRule,
)
from drift_detection.models import DriftFinding


class DriftEngine:
    def __init__(self, rules: Optional[Iterable[BaseDriftRule]] = None) -> None:
        self._rules: List[BaseDriftRule] = list(rules) if rules else self._load_default_rules()

    def _load_default_rules(self) -> List[BaseDriftRule]:
        return [
            EndpointRemovedRule(),
            EndpointPathChangedRule(),
            EndpointMethodChangedRule(),
            DependencyAddedRule(),
            DependencyRemovedRule(),
            ApiHandlerMissingRule(),
            SymbolReferenceMissingDefinitionRule(),
        ]

    @property
    def rules(self) -> Tuple[BaseDriftRule, ...]:
        return tuple(self._rules)

    def add_rule(self, rule: BaseDriftRule) -> None:
        self._rules.append(rule)

    def extend_rules(self, rules: Iterable[BaseDriftRule]) -> None:
        self._rules.extend(rules)

    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        for rule in self._rules:
            findings.extend(rule.evaluate(baseline, current))
        return findings
