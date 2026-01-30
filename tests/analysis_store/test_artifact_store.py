"""Tests for the analysis artifact store."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_store.artifact_store import ArtifactStore
from api_endpoint_detector.models.api_endpoint import ApiEndpoint
from semantic_extractor.models.relation import Relation
from semantic_extractor.models.symbol import Symbol


def test_artifact_store_accumulates_artifacts() -> None:
    store = ArtifactStore()

    store.add_symbols(
        [
            Symbol(
                name="module.A",
                symbol_type="module",
                language="python",
                file_path="module.py",
            )
        ]
    )

    store.add_relations(
        [
            Relation(
                source="module.A",
                target="module.B",
                relation_type="IMPORTS",
                language="python",
                file_path="module.py",
            )
        ]
    )

    store.add_api_endpoints(
        [
            ApiEndpoint(
                path="/health",
                http_method="GET",
                handler_name="module.health",
                class_name=None,
                language="python",
                file_path="module.py",
                framework="django",
                metadata={},
            )
        ]
    )

    artifacts = store.get_artifacts()

    assert len(artifacts.symbols) == 1
    assert len(artifacts.relations) == 1
    assert len(artifacts.api_endpoints) == 1

    copied = store.get_artifacts()
    copied.symbols.append(
        Symbol(
            name="module.C",
            symbol_type="module",
            language="python",
            file_path="module.py",
        )
    )

    # ensure store maintains its own state
    assert len(store.get_artifacts().symbols) == 1
