from typing import List, Set, Tuple

from analysis_store.models import AnalysisArtifacts

from drift_detection.engine.base_rule import BaseDriftRule
from drift_detection.models import DriftFinding, DriftSeverity
from drift_detection.utils import (
    build_symbol_name_set,
    candidate_handler_names,
    endpoint_to_metadata,
    is_symbol_reference_relation,
    relation_to_metadata,
)

_SymbolIdentity = Tuple[str, str]


class ApiHandlerMissingRule(BaseDriftRule):
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        baseline_symbols = build_symbol_name_set(baseline.symbols)
        current_symbols = build_symbol_name_set(current.symbols)
        for endpoint in baseline.api_endpoints:
            lookup_keys = self._build_symbol_keys(endpoint)
            baseline_has_handler = any(key in baseline_symbols for key in lookup_keys)
            if not baseline_has_handler:
                continue
            if any(key in current_symbols for key in lookup_keys):
                continue
            findings.append(
                DriftFinding(
                    drift_type="API_HANDLER_MISSING",
                    description=(
                        f"Handler for endpoint {endpoint.http_method.upper()} {endpoint.path} "
                        "is missing from current symbols."
                    ),
                    severity=DriftSeverity.HIGH,
                    metadata={
                        "endpoint": {
                            "handler_candidates": sorted(name for _, name in lookup_keys),
                            "details": endpoint_to_metadata(endpoint),
                        }
                    },
                )
            )
        return findings

    def _build_symbol_keys(self, endpoint) -> Set[_SymbolIdentity]:
        language = endpoint.language or ""
        return {
            (language, candidate_name)
            for candidate_name in candidate_handler_names(endpoint)
        }


class SymbolReferenceMissingDefinitionRule(BaseDriftRule):
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        baseline_symbols = build_symbol_name_set(baseline.symbols)
        current_symbols = build_symbol_name_set(current.symbols)
        reported: Set[Tuple[str, str, str, str, str, str]] = set()
        for relation in current.relations:
            if not is_symbol_reference_relation(relation):
                continue
            language = relation.language or ""
            source_key = (language, relation.source)
            target_key = (language, relation.target)
            if source_key not in current_symbols and source_key in baseline_symbols:
                key = (
                    "source",
                    language,
                    relation.relation_type,
                    relation.source,
                    relation.target,
                    relation.source,
                )
                if key not in reported:
                    reported.add(key)
                    findings.append(
                        DriftFinding(
                            drift_type="SYMBOL_REFERENCE_MISSING",
                            description=(
                                f"Relation {relation.relation_type} references source symbol "
                                f"{relation.source} which is not defined in current symbols."
                            ),
                            severity=DriftSeverity.HIGH,
                            metadata={
                                "relation": relation_to_metadata(relation),
                                "missing_symbol": relation.source,
                                "role": "source",
                            },
                        )
                    )
            if target_key not in current_symbols and target_key in baseline_symbols:
                key = (
                    "target",
                    language,
                    relation.relation_type,
                    relation.source,
                    relation.target,
                    relation.target,
                )
                if key in reported:
                    continue
                reported.add(key)
                findings.append(
                    DriftFinding(
                        drift_type="SYMBOL_REFERENCE_MISSING",
                        description=(
                            f"Relation {relation.relation_type} references target symbol "
                            f"{relation.target} which is not defined in current symbols."
                        ),
                        severity=DriftSeverity.HIGH,
                        metadata={
                            "relation": relation_to_metadata(relation),
                            "missing_symbol": relation.target,
                            "role": "target",
                        },
                    )
                )
        return findings
