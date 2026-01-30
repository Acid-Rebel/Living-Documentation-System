from collections import defaultdict
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from drift_detection.models import DriftFinding, DriftSeverity

_DEFAULT_SEVERITY_ORDER: Tuple[DriftSeverity, ...] = (
    DriftSeverity.HIGH,
    DriftSeverity.MEDIUM,
    DriftSeverity.LOW,
)


def summarize_findings(
    findings: Iterable[DriftFinding],
    severity_order: Sequence[DriftSeverity] | None = None,
) -> Dict[str, object]:
    order = tuple(severity_order) if severity_order else _DEFAULT_SEVERITY_ORDER
    order_values = {severity: index for index, severity in enumerate(order)}

    counts_by_severity: Dict[str, int] = {
        severity.value: 0 for severity in order
    }
    counts_by_type: Dict[str, int] = defaultdict(int)

    total = 0
    for finding in findings:
        total += 1
        severity_key = finding.severity.value
        if finding.severity in order_values:
            counts_by_severity[severity_key] += 1
        else:
            counts_by_severity.setdefault(severity_key, 0)
            counts_by_severity[severity_key] += 1
        counts_by_type[finding.drift_type] += 1

    ordered_counts_by_severity = {
        severity.value: counts_by_severity.get(severity.value, 0)
        for severity in order
    }
    # Include unknown severities at the end for completeness.
    for severity_key, count in counts_by_severity.items():
        if severity_key not in ordered_counts_by_severity:
            ordered_counts_by_severity[severity_key] = count

    ordered_counts_by_type = dict(sorted(counts_by_type.items()))

    return {
        "total_findings": total,
        "counts_by_severity": ordered_counts_by_severity,
        "counts_by_type": ordered_counts_by_type,
    }


def group_findings_by_severity(
    findings: Iterable[DriftFinding],
    severity_order: Sequence[DriftSeverity] | None = None,
) -> List[Tuple[DriftSeverity, List[DriftFinding]]]:
    order = tuple(severity_order) if severity_order else _DEFAULT_SEVERITY_ORDER
    grouping: Dict[DriftSeverity, List[DriftFinding]] = {
        severity: [] for severity in order
    }
    extra: Dict[DriftSeverity, List[DriftFinding]] = defaultdict(list)

    for finding in findings:
        if finding.severity in grouping:
            grouping[finding.severity].append(finding)
        else:
            extra[finding.severity].append(finding)

    ordered: List[Tuple[DriftSeverity, List[DriftFinding]]] = [
        (severity, grouping[severity]) for severity in order
    ]
    ordered.extend(sorted(extra.items(), key=lambda item: item[0].value))
    return ordered


def finding_to_dict(finding: DriftFinding) -> Dict[str, object]:
    return {
        "drift_type": finding.drift_type,
        "description": finding.description,
        "severity": finding.severity.value,
        "metadata": finding.metadata,
    }


def findings_to_list(findings: Iterable[DriftFinding]) -> List[Dict[str, object]]:
    return [finding_to_dict(finding) for finding in findings]
