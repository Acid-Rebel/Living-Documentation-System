import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_store.artifact_store import ArtifactStore
from api_endpoint_detector.models.api_endpoint import ApiEndpoint
from semantic_extractor.models.symbol import Symbol
from semantic_extractor.models.relation import Relation
from dependency_analyzer.analyzer_manager import DependencyAnalyzerManager


def demo() -> None:
    store = ArtifactStore()

    store.add_symbols(
        [
            Symbol(
                name="module.views.status_view",
                symbol_type="function",
                language="python",
                file_path="module/views.py",
            ),
            Symbol(
                name="module.repositories.ItemRepository",
                symbol_type="class",
                language="python",
                file_path="module/repositories.py",
            ),
        ]
    )

    store.add_relations(
        [
            Relation(
                source="module.views.status_view",
                target="module.repositories.ItemRepository",
                relation_type="CALLS",
                language="python",
                file_path="module/views.py",
            ),
            Relation(
                source="module.views.status_view",
                target="module.utils.logging",
                relation_type="IMPORTS",
                language="python",
                file_path="module/views.py",
            ),
        ]
    )

    store.add_api_endpoints(
        [
            ApiEndpoint(
                path="/status",
                http_method="GET",
                handler_name="module.views.status_view",
                class_name=None,
                language="python",
                file_path="module/urls.py",
                framework="django",
                metadata={"route_name": "status"},
            )
        ]
    )

    artifacts = store.get_artifacts()

    print("Artifacts in store:")
    for symbol in artifacts.symbols:
        print(f"  Symbol: {symbol.name} ({symbol.symbol_type})")
    for relation in artifacts.relations:
        print(f"  Relation: {relation.relation_type} {relation.source} -> {relation.target}")
    for endpoint in artifacts.api_endpoints:
        print(
            f"  API: {endpoint.http_method} {endpoint.path} handled by {endpoint.handler_name}"
        )

    manager = DependencyAnalyzerManager()
    dependencies = manager.analyze(artifacts)

    print("\nDerived dependencies:")
    for dependency in dependencies:
        print(
            f"  {dependency.dependency_type}: {dependency.source} -> {dependency.target}"
        )
        if dependency.metadata:
            print(f"    metadata: {dependency.metadata}")


if __name__ == "__main__":
    demo()
