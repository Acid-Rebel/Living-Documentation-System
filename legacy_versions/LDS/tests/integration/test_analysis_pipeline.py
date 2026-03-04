"""Integration test for parser → semantic → API → artifact store → dependency pipeline."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_store.artifact_store import ArtifactStore
from dependency_analyzer.analyzer_manager import DependencyAnalyzerManager
from semantic_extractor.analyzer_manager import AnalyzerManager
from api_endpoint_detector.detector_manager import DetectorManager
from code_parser.parsers.python_parser import PythonParser


def test_full_pipeline_populates_artifacts_and_dependencies() -> None:
    views_source = """
from module.utils import fetch_status

def status_view():
    return fetch_status()

def item_detail_view(item_id):
    return fetch_status()
"""

    urls_source = """
from django.urls import path
from . import views

urlpatterns = [
    path("status/", views.status_view, name="status"),
    path("items/<int:item_id>/", views.item_detail_view, name="item-detail"),
]
"""

    parser = PythonParser()
    semantic_manager = AnalyzerManager()
    endpoint_manager = DetectorManager()
    store = ArtifactStore()

    for file_path, source in (
        ("module/views.py", views_source),
        ("module/urls.py", urls_source),
    ):
        ast_root = parser.normalize(parser.parse(source))
        semantic_artifacts = semantic_manager.analyze(ast_root, file_path, "python")
        store.add_symbols(semantic_artifacts["symbols"])
        store.add_relations(semantic_artifacts["relations"])
        endpoints = endpoint_manager.detect(ast_root, file_path, "python")
        if endpoints:
            store.add_api_endpoints(endpoints)

    artifacts = store.get_artifacts()

    assert any(symbol.name == "status_view" for symbol in artifacts.symbols)
    assert any(symbol.name == "item_detail_view" for symbol in artifacts.symbols)

    import_relations = [rel for rel in artifacts.relations if rel.relation_type == "IMPORTS"]
    call_relations = [rel for rel in artifacts.relations if rel.relation_type == "CALLS"]
    assert import_relations, "Expected import relations from semantic analysis"
    assert any(rel.source == "status_view" and rel.target for rel in call_relations)

    assert len(artifacts.api_endpoints) == 2
    assert {endpoint.path for endpoint in artifacts.api_endpoints} == {
        "/status/",
        "/items/<int:item_id>/",
    }

    dependency_manager = DependencyAnalyzerManager()
    dependencies = dependency_manager.analyze(artifacts)

    snapshot = store.get_artifacts()
    assert snapshot.symbols == artifacts.symbols
    assert snapshot.relations == artifacts.relations
    assert snapshot.api_endpoints == artifacts.api_endpoints

    assert any(
        dep.dependency_type == "FUNCTION_CALLS"
        and dep.source == "status_view"
        and dep.target
        for dep in dependencies
    )

    assert any(
        dep.dependency_type == "API_DEPENDS_ON"
        and dep.source == "django:/status/"
        and dep.target.endswith("status_view")
        for dep in dependencies
    )

    assert any(dep.dependency_type == "MODULE_DEPENDS_ON" for dep in dependencies)
