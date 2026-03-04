from abc import ABC, abstractmethod
from typing import List

from analysis_store.models import AnalysisArtifacts
from ..models import DriftFinding


class BaseDriftRule(ABC):
    @abstractmethod
    def evaluate(
        self,
        baseline: AnalysisArtifacts,
        current: AnalysisArtifacts,
    ) -> List[DriftFinding]:
        raise NotImplementedError
