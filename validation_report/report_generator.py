from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional, Sequence

from drift_detection.models import DriftFinding, DriftSeverity

from validation_report.models import ValidationReport
from validation_report.utils import (
    findings_to_list,
    group_findings_by_severity,
    summarize_findings,
)


class ValidationReportGenerator:
    def __init__(
        self,
        severity_order: Optional[Sequence[DriftSeverity]] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._severity_order = tuple(severity_order) if severity_order else None
        self._clock = clock or datetime.utcnow

    def generate(
        self,
        findings: Iterable[DriftFinding],
        metadata: Optional[Dict[str, object]] = None,
    ) -> ValidationReport:
        findings_list = list(findings)
        summary = summarize_findings(findings_list, self._severity_order)
        report_metadata = dict(metadata) if metadata else {}
        generated_at = self._clock()
        return ValidationReport(
            summary=summary,
            findings=findings_list,
            generated_at=generated_at,
            metadata=report_metadata,
        )

    def to_dict(self, report: ValidationReport) -> Dict[str, object]:
        return {
            "summary": report.summary,
            "findings": findings_to_list(report.findings),
            "generated_at": report.generated_at.isoformat(),
            "metadata": report.metadata,
        }

    def to_markdown(self, report: ValidationReport) -> str:
        lines: List[str] = []
        lines.append("# Validation Report")
        lines.append("")
        lines.append(f"Generated: {report.generated_at.isoformat()}")
        lines.append("")
        lines.append("## Summary")
        total = report.summary.get("total_findings", len(report.findings))
        lines.append(f"- Total Findings: {total}")

        severity_counts = report.summary.get("counts_by_severity", {})
        if severity_counts:
            lines.append("- Severity Counts:")
            for severity, count in severity_counts.items():
                lines.append(f"  - {severity}: {count}")

        type_counts = report.summary.get("counts_by_type", {})
        if type_counts:
            lines.append("- Drift Types:")
            for drift_type, count in type_counts.items():
                lines.append(f"  - {drift_type}: {count}")
        lines.append("")

        grouped = group_findings_by_severity(report.findings, self._severity_order)
        for severity, severity_findings in grouped:
            if not severity_findings:
                continue
            lines.append(f"## {severity.value} ({len(severity_findings)})")
            for finding in severity_findings:
                lines.append(
                    f"- **{finding.drift_type}**: {finding.description}"
                )
            lines.append("")

        if lines and lines[-1] == "":
            lines.pop()
        return "\n".join(lines)
