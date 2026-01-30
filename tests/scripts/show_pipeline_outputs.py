import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis_store.artifact_store import ArtifactStore
from api_endpoint_detector.detector_manager import DetectorManager
from code_parser.parsers.python_parser import PythonParser
from dependency_analyzer.analyzer_manager import DependencyAnalyzerManager
from semantic_extractor.analyzer_manager import AnalyzerManager

PIPELINE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "pipeline"


def run_pipeline() -> None:
    parser = PythonParser()
    semantic_manager = AnalyzerManager()
    endpoint_manager = DetectorManager()
    store = ArtifactStore()

    print("=== Parser Outputs ===")
    for source_path in sorted(PIPELINE_ROOT.glob("**/*.py")):
        relative_path = source_path.relative_to(PROJECT_ROOT)
        source = source_path.read_text(encoding="utf-8")
        ast_root = parser.normalize(parser.parse(source))
        print(f"Parsed {relative_path} -> AST node_type={ast_root.node_type}")

        semantics = semantic_manager.analyze(ast_root, str(relative_path), "python")
        if semantics["symbols"]:
            print("  Symbols detected:")
            for symbol in semantics["symbols"]:
                print(f"    - {symbol.name} ({symbol.symbol_type})")
        if semantics["relations"]:
            print("  Relations detected:")
            for relation in semantics["relations"]:
                print(
                    f"    - {relation.relation_type}: {relation.source} -> {relation.target}"
                )
        store.add_symbols(semantics["symbols"])
        store.add_relations(semantics["relations"])

        endpoints = endpoint_manager.detect(ast_root, str(relative_path), "python")
        if endpoints:
            print("  API endpoints detected:")
            for endpoint in endpoints:
                print(
                    "    - "
                    f"{endpoint.http_method} {endpoint.path} handled by {endpoint.handler_name}"
                )
            store.add_api_endpoints(endpoints)

    artifacts = store.get_artifacts()

    print("\n=== Artifact Store Snapshot ===")
    print(f"Total symbols: {len(artifacts.symbols)}")
    print(f"Total relations: {len(artifacts.relations)}")
    print(f"Total API endpoints: {len(artifacts.api_endpoints)}")

    dependency_manager = DependencyAnalyzerManager()
    dependencies = dependency_manager.analyze(artifacts)

    print("\n=== Dependencies ===")
    for dependency in dependencies:
        line = (
            f"  - {dependency.dependency_type}: {dependency.source} -> {dependency.target}"
            f" [{dependency.language}]"
        )
        print(line)
        if dependency.metadata:
            print(f"      metadata: {dependency.metadata}")


if __name__ == "__main__":
    run_pipeline()
