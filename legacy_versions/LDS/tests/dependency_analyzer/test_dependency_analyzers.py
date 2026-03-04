"""Tests for dependency analyzers."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_store.models import AnalysisArtifacts
from dependency_analyzer.analyzer_manager import DependencyAnalyzerManager
from dependency_analyzer.analyzers.api_dependency_analyzer import ApiDependencyAnalyzer
from dependency_analyzer.analyzers.function_dependency_analyzer import FunctionDependencyAnalyzer
from dependency_analyzer.analyzers.module_dependency_analyzer import ModuleDependencyAnalyzer
from dependency_analyzer.models.dependency import Dependency
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol
from api_endpoint_detector.models.api_endpoint import ApiEndpoint


def _build_dependencies(artifacts: AnalysisArtifacts) -> list[Dependency]:
    manager = DependencyAnalyzerManager(
        analyzers=[
            ModuleDependencyAnalyzer(),
            FunctionDependencyAnalyzer(),
            ApiDependencyAnalyzer(),
        ]
    )
    return manager.analyze(artifacts)


def test_module_dependency_analyzer_derives_imports() -> None:
    artifacts = AnalysisArtifacts(
        relations=[
            Relation(
                source="module.alpha",
                target="module.beta",
                relation_type="IMPORTS",
                language="python",
                file_path="alpha.py",
            )
        ]
    )

    dependencies = _build_dependencies(artifacts)

    assert dependencies == [
        Dependency(
            source="module.alpha",
            target="module.beta",
            dependency_type="MODULE_DEPENDS_ON",
            language="python",
            metadata={"file_path": "alpha.py"},
        )
    ]


def test_function_dependency_analyzer_uses_calls_relations() -> None:
    artifacts = AnalysisArtifacts(
        relations=[
            Relation(
                source="module.alpha.fn",
                target="module.beta.fn",
                relation_type="CALLS",
                language="python",
                file_path="alpha.py",
            )
        ]
    )

    dependencies = _build_dependencies(artifacts)

    assert Dependency(
        source="module.alpha.fn",
        target="module.beta.fn",
        dependency_type="FUNCTION_CALLS",
        language="python",
        metadata={"file_path": "alpha.py"},
    ) in dependencies


def test_api_dependency_analyzer_links_endpoints_to_relations() -> None:
    artifacts = AnalysisArtifacts(
        symbols=[
            Symbol(
                name="module.views.ItemDetailView",
                symbol_type="class",
                language="python",
                file_path="module/views.py",
            ),
            Symbol(
                name="module.views.status_view",
                symbol_type="function",
                language="python",
                file_path="module/views.py",
            ),
        ],
        relations=[
            Relation(
                source="module.views.status_view",
                target="module.services.fetch_status",
                relation_type="CALLS",
                language="python",
                file_path="module/views.py",
            ),
            Relation(
                source="module.views.ItemDetailView.as_view",
                target="module.repositories.ItemRepository",
                relation_type="IMPORTS",
                language="python",
                file_path="module/views.py",
            ),
        ],
        api_endpoints=[
            ApiEndpoint(
                path="/status",
                http_method="GET",
                handler_name="module.views.status_view",
                class_name=None,
                language="python",
                file_path="module/urls.py",
                framework="django",
                metadata={"route_name": "status"},
            ),
            ApiEndpoint(
                path="/items",
                http_method="GET",
                handler_name="module.views.ItemDetailView.as_view",
                class_name="module.views.ItemDetailView",
                language="python",
                file_path="module/urls.py",
                framework="django",
                metadata={"route_name": "item-detail"},
            ),
        ],
    )

    dependencies = _build_dependencies(artifacts)

    by_type = {
        (dep.source, dep.target, dep.dependency_type): dep for dep in dependencies
    }

    assert (
        "django:/status",
        "module.views.status_view",
        "API_DEPENDS_ON",
    ) in by_type
    assert (
        "django:/status",
        "module.services.fetch_status",
        "API_DEPENDS_ON",
    ) in by_type
    assert (
        "django:/items",
        "module.repositories.ItemRepository",
        "API_DEPENDS_ON",
    ) in by_type

    status_dependency = by_type[("django:/status", "module.views.status_view", "API_DEPENDS_ON")]
    assert status_dependency.metadata["framework"] == "django"
    assert status_dependency.metadata["http_method"] == "GET"

    item_dependency = by_type[("django:/items", "module.repositories.ItemRepository", "API_DEPENDS_ON")]
    assert item_dependency.metadata["via_handler"] == "module.views.ItemDetailView.as_view"
