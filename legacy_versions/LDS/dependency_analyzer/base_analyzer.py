from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from analysis_store.models import AnalysisArtifacts
from dependency_analyzer.models.dependency import Dependency


class BaseDependencyAnalyzer(ABC):
    @abstractmethod
    def analyze(self, artifacts: AnalysisArtifacts) -> List[Dependency]:
        raise NotImplementedError
