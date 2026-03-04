from dataclasses import dataclass, field
from typing import List

from api_endpoint_detector.models.api_endpoint import ApiEndpoint
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol


@dataclass
class AnalysisArtifacts:
    symbols: List[Symbol] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    api_endpoints: List[ApiEndpoint] = field(default_factory=list)
