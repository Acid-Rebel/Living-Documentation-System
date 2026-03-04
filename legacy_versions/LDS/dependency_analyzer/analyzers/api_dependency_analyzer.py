from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from analysis_store.models import AnalysisArtifacts
from dependency_analyzer.base_analyzer import BaseDependencyAnalyzer
from dependency_analyzer.models.dependency import Dependency
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol
from api_endpoint_detector.models.api_endpoint import ApiEndpoint


class ApiDependencyAnalyzer(BaseDependencyAnalyzer):
    _DEPENDENCY_TYPE = "API_DEPENDS_ON"

    def analyze(self, artifacts: AnalysisArtifacts) -> List[Dependency]:
        dependencies: List[Dependency] = []
        seen: Set[Tuple[str, str, str, str]] = set()

        call_relations = [rel for rel in artifacts.relations if rel.relation_type == "CALLS"]
        import_relations = [rel for rel in artifacts.relations if rel.relation_type == "IMPORTS"]

        symbols = artifacts.symbols

        for endpoint in artifacts.api_endpoints:
            api_identifier = self._api_identifier(endpoint)
            handler_name = endpoint.handler_name or "<anonymous>"

            metadata = {
                "file_path": endpoint.file_path,
                "http_method": endpoint.http_method,
                "framework": endpoint.framework,
            }
            if endpoint.class_name:
                metadata["class_name"] = endpoint.class_name
            if endpoint.metadata:
                metadata["endpoint_metadata"] = endpoint.metadata

            signature = (api_identifier, handler_name, endpoint.language, "handler")
            if signature not in seen:
                seen.add(signature)
                dependencies.append(
                    Dependency(
                        source=api_identifier,
                        target=handler_name,
                        dependency_type=self._DEPENDENCY_TYPE,
                        language=endpoint.language,
                        metadata=metadata,
                    )
                )

            handler_candidates = self._handler_candidates(endpoint, symbols)

            dependencies.extend(
                self._relation_dependencies(
                    api_identifier,
                    endpoint,
                    handler_candidates,
                    call_relations,
                    relation_type="CALLS",
                    seen=seen,
                )
            )

            dependencies.extend(
                self._relation_dependencies(
                    api_identifier,
                    endpoint,
                    handler_candidates,
                    import_relations,
                    relation_type="IMPORTS",
                    seen=seen,
                )
            )

        return dependencies

    def _api_identifier(self, endpoint: ApiEndpoint) -> str:
        return f"{endpoint.framework}:{endpoint.path}"

    def _handler_candidates(
        self,
        endpoint: ApiEndpoint,
        symbols: Iterable[Symbol],
    ) -> Set[str]:
        candidates: Set[str] = set()

        handler = endpoint.handler_name
        class_name = endpoint.class_name

        if handler:
            candidates.add(handler)
        if handler and class_name:
            candidates.add(f"{class_name}.{handler}")

        if handler:
            suffix = handler.split(".")[-1]
            for symbol in symbols:
                if symbol.name.endswith(suffix):
                    candidates.add(symbol.name)
        if class_name:
            for symbol in symbols:
                if symbol.name.endswith(class_name):
                    candidates.add(symbol.name)

        return candidates

    def _relation_dependencies(
        self,
        api_identifier: str,
        endpoint: ApiEndpoint,
        handler_candidates: Set[str],
        relations: Iterable[Relation],
        *,
        relation_type: str,
        seen: Set[Tuple[str, str, str, str]],
    ) -> List[Dependency]:
        dependencies: List[Dependency] = []

        for relation in relations:
            if relation.source not in handler_candidates:
                continue
            target = relation.target
            if not target:
                continue

            metadata: Dict[str, object] = {
                "via_handler": relation.source,
                "relation_type": relation.relation_type,
                "relation_file_path": relation.file_path,
            }

            signature = (api_identifier, target, endpoint.language, relation_type)
            if signature in seen:
                continue
            seen.add(signature)

            dependencies.append(
                Dependency(
                    source=api_identifier,
                    target=target,
                    dependency_type=self._DEPENDENCY_TYPE,
                    language=endpoint.language,
                    metadata=metadata,
                )
            )

        return dependencies
