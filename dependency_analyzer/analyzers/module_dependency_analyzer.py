from __future__ import annotations

from typing import List, Tuple

from analysis_store.models import AnalysisArtifacts
from dependency_analyzer.base_analyzer import BaseDependencyAnalyzer
from dependency_analyzer.models.dependency import Dependency


class ModuleDependencyAnalyzer(BaseDependencyAnalyzer):
    _DEPENDENCY_TYPE = "MODULE_DEPENDS_ON"

    def analyze(self, artifacts: AnalysisArtifacts) -> List[Dependency]:
        dependencies: List[Dependency] = []
        seen: set[Tuple[str, str, str]] = set()

        for relation in artifacts.relations:
            if relation.relation_type != "IMPORTS":
                continue

            source = relation.source or relation.file_path
            target = relation.target
            if not source or not target:
                continue

            signature = (source, target, relation.language)
            if signature in seen:
                continue
            seen.add(signature)

            dependencies.append(
                Dependency(
                    source=source,
                    target=target,
                    dependency_type=self._DEPENDENCY_TYPE,
                    language=relation.language,
                    metadata={"file_path": relation.file_path},
                )
            )

        return dependencies
