from typing import List

from analysis_store.models import AnalysisArtifacts

from drift_detection.engine.base_rule import BaseDriftRule
from drift_detection.models import DriftFinding, DriftSeverity
from drift_detection.utils import (
    build_dependency_set,
    index_dependencies,
    relation_to_metadata,
)


class DependencyAddedRule(BaseDriftRule):
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        baseline_dependencies = build_dependency_set(baseline.relations)
        current_dependencies = build_dependency_set(current.relations)
        current_index = index_dependencies(current.relations)
        added_dependencies = current_dependencies - baseline_dependencies
        for dependency in sorted(added_dependencies):
            relation = current_index.get(dependency)
            if relation is None:
                continue
            findings.append(
                DriftFinding(
                    drift_type="DEPENDENCY_ADDED",
                    description=(
                        f"Dependency {dependency[1]} from {dependency[2]} to {dependency[3]} added."
                    ),
                    severity=DriftSeverity.LOW,
                    metadata={
                        "dependency": dependency,
                        "relation": relation_to_metadata(relation),
                    },
                )
            )
        return findings


class DependencyRemovedRule(BaseDriftRule):
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        baseline_dependencies = build_dependency_set(baseline.relations)
        current_dependencies = build_dependency_set(current.relations)
        baseline_index = index_dependencies(baseline.relations)
        removed_dependencies = baseline_dependencies - current_dependencies
        for dependency in sorted(removed_dependencies):
            relation = baseline_index.get(dependency)
            if relation is None:
                continue
            findings.append(
                DriftFinding(
                    drift_type="DEPENDENCY_REMOVED",
                    description=(
                        f"Dependency {dependency[1]} from {dependency[2]} to {dependency[3]} removed."
                    ),
                    severity=DriftSeverity.MEDIUM,
                    metadata={
                        "dependency": dependency,
                        "relation": relation_to_metadata(relation),
                    },
                )
            )
        return findings
