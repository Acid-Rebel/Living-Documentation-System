from __future__ import annotations

from typing import Iterable, List

from analysis_store.models import AnalysisArtifacts
from dependency_analyzer.base_analyzer import BaseDependencyAnalyzer
from dependency_analyzer.models.dependency import Dependency
from dependency_analyzer.analyzers.api_dependency_analyzer import ApiDependencyAnalyzer
from dependency_analyzer.analyzers.function_dependency_analyzer import FunctionDependencyAnalyzer
from dependency_analyzer.analyzers.module_dependency_analyzer import ModuleDependencyAnalyzer


class DependencyAnalyzerManager:
    def __init__(self, analyzers: Iterable[BaseDependencyAnalyzer] | None = None) -> None:
        self._analyzers: List[BaseDependencyAnalyzer] = (
            list(analyzers)
            if analyzers is not None
            else [
                ModuleDependencyAnalyzer(),
                FunctionDependencyAnalyzer(),
                ApiDependencyAnalyzer(),
            ]
        )

    def analyze(self, artifacts: AnalysisArtifacts) -> List[Dependency]:
        dependencies: List[Dependency] = []
        for analyzer in self._analyzers:
            dependencies.extend(analyzer.analyze(artifacts))
        return dependencies
