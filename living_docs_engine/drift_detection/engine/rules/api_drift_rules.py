from typing import Dict, List, Tuple

from analysis_store.models import AnalysisArtifacts

from drift_detection.engine.base_rule import BaseDriftRule
from drift_detection.models import DriftFinding, DriftSeverity
from drift_detection.utils import build_handler_map, endpoint_to_metadata

_HandlerIdentity = Tuple[str, str, str, str]


class EndpointRemovedRule(BaseDriftRule):
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        baseline_map = build_handler_map(baseline.api_endpoints)
        current_map = build_handler_map(current.api_endpoints)
        for handler_id, endpoint in baseline_map.items():
            if handler_id in current_map:
                continue
            findings.append(
                DriftFinding(
                    drift_type="API_REMOVED",
                    description=(
                        f"Endpoint {endpoint.http_method.upper()} {endpoint.path} "
                        "is not present in the current artifacts."
                    ),
                    severity=DriftSeverity.HIGH,
                    metadata={
                        "baseline_endpoint": endpoint_to_metadata(endpoint),
                        "handler_identity": handler_id,
                    },
                )
            )
        return findings


class EndpointPathChangedRule(BaseDriftRule):
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        baseline_map: Dict[_HandlerIdentity, _EndpointWrapper] = {
            handler_id: _EndpointWrapper.from_endpoint(endpoint)
            for handler_id, endpoint in build_handler_map(baseline.api_endpoints).items()
        }
        current_map = {
            handler_id: _EndpointWrapper.from_endpoint(endpoint)
            for handler_id, endpoint in build_handler_map(current.api_endpoints).items()
        }
        common_handlers = baseline_map.keys() & current_map.keys()
        for handler_id in common_handlers:
            baseline_endpoint = baseline_map[handler_id]
            current_endpoint = current_map[handler_id]
            if baseline_endpoint.path == current_endpoint.path:
                continue
            findings.append(
                DriftFinding(
                    drift_type="API_PATH_CHANGED",
                    description=(
                        "Endpoint path changed from "
                        f"{baseline_endpoint.http_method} {baseline_endpoint.path} to "
                        f"{current_endpoint.http_method} {current_endpoint.path}."
                    ),
                    severity=DriftSeverity.MEDIUM,
                    metadata={
                        "baseline_endpoint": baseline_endpoint.metadata,
                        "current_endpoint": current_endpoint.metadata,
                        "handler_identity": handler_id,
                    },
                )
            )
        return findings


class EndpointMethodChangedRule(BaseDriftRule):
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        findings: List[DriftFinding] = []
        baseline_map: Dict[_HandlerIdentity, _EndpointWrapper] = {
            handler_id: _EndpointWrapper.from_endpoint(endpoint)
            for handler_id, endpoint in build_handler_map(baseline.api_endpoints).items()
        }
        current_map = {
            handler_id: _EndpointWrapper.from_endpoint(endpoint)
            for handler_id, endpoint in build_handler_map(current.api_endpoints).items()
        }
        common_handlers = baseline_map.keys() & current_map.keys()
        for handler_id in common_handlers:
            baseline_endpoint = baseline_map[handler_id]
            current_endpoint = current_map[handler_id]
            if baseline_endpoint.http_method == current_endpoint.http_method:
                continue
            findings.append(
                DriftFinding(
                    drift_type="API_METHOD_CHANGED",
                    description=(
                        f"Endpoint {baseline_endpoint.path} changed method from "
                        f"{baseline_endpoint.http_method} to {current_endpoint.http_method}."
                    ),
                    severity=DriftSeverity.MEDIUM,
                    metadata={
                        "baseline_endpoint": baseline_endpoint.metadata,
                        "current_endpoint": current_endpoint.metadata,
                        "handler_identity": handler_id,
                    },
                )
            )
        return findings


class _EndpointWrapper:
    def __init__(self, path: str, http_method: str, metadata: Dict):
        self.path = path
        self.http_method = http_method
        self.metadata = metadata

    @classmethod
    def from_endpoint(cls, endpoint):
        return cls(
            endpoint.path,
            endpoint.http_method.upper(),
            endpoint_to_metadata(endpoint),
        )
