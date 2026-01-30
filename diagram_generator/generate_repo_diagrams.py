import os
import shutil
import subprocess

from code_parser.language_detection import detect_language
from code_parser.parser_manager import get_parser

from diagram_generator.graph_model import DiagramGraph
from diagram_generator.repo_scanner import scan_repo

from analysis_store.artifact_store import ArtifactStore
from semantic_extractor.analyzer_manager import AnalyzerManager
from dependency_analyzer.analyzer_manager import DependencyAnalyzerManager
from api_endpoint_detector.detector_manager import DetectorManager

from diagram_generator.heuristics import enrich_with_heuristics
from diagram_generator.ast_relations import extract_ast_relations

from diagram_generator.renderers import (
    render_class_diagram_dot,
    render_dependency_diagram_dot,
    render_call_diagram_dot,
    render_api_diagram_dot,
    render_dot_to_png,
    group_calls_by_module,
)

TEMP_REPO_DIR = "_temp_repo"
OUTPUT_BASE_DIR = "output"


def repo_name_from_url(url):
    return url.rstrip("/").split("/")[-1].replace(".git", "")


def latest_commit(url):
    out = subprocess.check_output(["git", "ls-remote", url, "HEAD"], text=True)
    return out.split()[0][:7]


def clone_repo(url):
    if os.path.exists(TEMP_REPO_DIR):
        shutil.rmtree(TEMP_REPO_DIR)

    subprocess.run(
        ["git", "clone", "--depth", "1", url, TEMP_REPO_DIR],
        check=True,
    )


def generate_repo_diagrams(repo_url):
    repo = repo_name_from_url(repo_url)
    commit = latest_commit(repo_url)

    print(f"[INFO] Repo: {repo}")
    print(f"[INFO] Commit: {commit}")

    clone_repo(repo_url)

    # ---------- Setup components ----------
    artifact_store = ArtifactStore()
    analyzer = AnalyzerManager()
    dep_analyzer = DependencyAnalyzerManager()
    api_detector = DetectorManager()
    graph = DiagramGraph()

    # ---------- Scan repository ----------
    for file in scan_repo(TEMP_REPO_DIR):
        language = detect_language(file)
        if not language:
            continue

        with open(file, "r", errors="ignore") as f:
            code = f.read()

        # 1. PARSE
        parser = get_parser(language)
        ast = parser.normalize(parser.parse(code))

        module_name = (
            file.replace(TEMP_REPO_DIR, "")
            .replace("/", ".")
            .replace("\\", ".")
            .strip(".")
        )

        # 2. SEMANTIC ANALYSIS -> STORE
        result = analyzer.analyze(ast, module_name, language)
        artifact_store.add_symbols(result["symbols"])
        artifact_store.add_relations(result["relations"])

        # 3. API DETECTION -> STORE
        endpoints = api_detector.detect(ast, file, language)
        artifact_store.add_api_endpoints(endpoints)

        # 4. AST RELATIONS -> GRAPH (Directly, as it's behavior)
        # We also need these for the graph, and they are not strictly "semantic artifacts" in the same way
        ast_classes, ast_relations = extract_ast_relations(ast, module=module_name)
        graph.add_ast_relations(ast_classes, ast_relations)

    # ---------- Post-Scan Processing ----------
    
    # Get all artifacts
    artifacts = artifact_store.get_artifacts()

    # 5. DEPENDENCY ANALYSIS
    dependencies = dep_analyzer.analyze(artifacts)
    # Load dependencies into graph
    for dep in dependencies:
        graph.dependencies.add((dep.source, dep.target))

    # 6. ENRICH & LOAD TO GRAPH
    # Normalize semantic relation types
    for r in artifacts.relations:
        if r.relation_type == "IMPORTS":
            r.relation_type = "import"
        if r.relation_type == "CALLS":
            r.relation_type = "call"

    # Load semantic data into graph (Structure)
    graph.load_from_semantics(artifacts.symbols, artifacts.relations)

    # ---------- Output generation ----------
    out_dir = os.path.join(OUTPUT_BASE_DIR, repo, commit)
    os.makedirs(out_dir, exist_ok=True)

    # Global class diagram
    global_png = os.path.join(out_dir, "class_diagram_global.png")
    dot = render_class_diagram_dot(graph)
    render_dot_to_png(dot, global_png)

    # File-level class diagrams
    file_map = {}
    for cls, info in graph.classes.items():
        if info.module:
            file_map.setdefault(info.module, []).append(cls)
    
    for module, classes in file_map.items():
        safe = module.replace(".", "_")
        png_path = os.path.join(out_dir, f"class_{safe}.png")
        dot = render_class_diagram_dot(graph, focus_classes=classes)
        render_dot_to_png(dot, png_path)

    # Dependency diagram
    dep_png = os.path.join(out_dir, "dependency_diagram.png")
    dep_dot = render_dependency_diagram_dot(graph)
    render_dot_to_png(dep_dot, dep_png)

    # Call diagrams (AST only)
    call_modules = group_calls_by_module(graph)
    for module, classes in call_modules.items():
        safe = module.replace(".", "_")
        png_path = os.path.join(out_dir, f"call_{safe}.png")
        dot = render_call_diagram_dot(graph, focus_classes=classes)
        render_dot_to_png(dot, png_path)

    # API Diagram
    if artifacts.api_endpoints:
        api_png = os.path.join(out_dir, "api_diagram.png")
        api_dot = render_api_diagram_dot(artifacts.api_endpoints)
        render_dot_to_png(api_dot, api_png)

    shutil.rmtree(TEMP_REPO_DIR)
    print(f"✅ Diagrams generated at {out_dir}")
