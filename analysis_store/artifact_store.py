from __future__ import annotations

from collections.abc import Iterable

from analysis_store.models import AnalysisArtifacts
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol
from api_endpoint_detector.models.api_endpoint import ApiEndpoint


class ArtifactStore:
    """In-memory container for analysis artifacts aggregated across stages."""

    def __init__(self) -> None:
        self._artifacts = AnalysisArtifacts()

    def add_symbols(self, symbols: Iterable[Symbol]) -> None:
        self._artifacts.symbols.extend(symbols)

    def add_relations(self, relations: Iterable[Relation]) -> None:
        self._artifacts.relations.extend(relations)

    def add_api_endpoints(self, endpoints: Iterable[ApiEndpoint]) -> None:
        self._artifacts.api_endpoints.extend(endpoints)

    def get_artifacts(self) -> AnalysisArtifacts:
        return AnalysisArtifacts(
            symbols=list(self._artifacts.symbols),
            relations=list(self._artifacts.relations),
            api_endpoints=list(self._artifacts.api_endpoints),
        )
