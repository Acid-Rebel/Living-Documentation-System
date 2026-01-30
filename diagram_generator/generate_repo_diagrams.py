import os
import shutil
import subprocess

from code_parser.language_detection import detect_language
from code_parser.parser_manager import get_parser

from diagram_generator.graph_model import DiagramGraph
from diagram_generator.repo_scanner import scan_repo

from semantic_extractor.analyzer_manager import AnalyzerManager
from diagram_generator.heuristics import enrich_with_heuristics
from diagram_generator.ast_relations import extract_ast_relations

from diagram_generator.renderers import (
    render_class_diagram_dot,
    render_dependency_diagram_dot,
    render_call_diagram_dot,
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

    analyzer = AnalyzerManager()
    graph = DiagramGraph()

    all_symbols = []
    all_relations = []

    # ---------- Scan repository ----------
    for file in scan_repo(TEMP_REPO_DIR):
        language = detect_language(file)
        if not language:
            continue

        with open(file, "r", errors="ignore") as f:
            code = f.read()

        parser = get_parser(language)
        ast = parser.normalize(parser.parse(code))

        module_name = (
            file.replace(TEMP_REPO_DIR, "")
            .replace("/", ".")
            .replace("\\", ".")
            .strip(".")
        )

        # ---------- Semantic analysis (FACTS) ----------
        result = analyzer.analyze(ast, module_name, language)
        all_symbols.extend(result["symbols"])
        all_relations.extend(result["relations"])

        # ---------- AST structural extraction (UNDERSTANDING) ----------
        ast_classes, ast_relations = extract_ast_relations(ast, module=module_name)
        graph.add_ast_relations(ast_classes, ast_relations)

    # ---------- Normalize semantic relation types ----------
    for r in all_relations:
        if r.relation_type == "IMPORTS":
            r.relation_type = "import"

    # ---------- Apply heuristics ----------
    all_relations = enrich_with_heuristics(all_symbols, all_relations)

    # ---------- Load semantic data into graph ----------
    graph.load_from_semantics(all_symbols, all_relations)

    # ---------- Output directory ----------
    out_dir = os.path.join(OUTPUT_BASE_DIR, repo, commit)
    os.makedirs(out_dir, exist_ok=True)

    # ---------- Global class diagram ----------
    global_png = os.path.join(out_dir, "class_diagram_global.png")
    dot = render_class_diagram_dot(graph)
    render_dot_to_png(dot, global_png)
    # ---------- File-level class diagrams ----------
    file_map = {}
    for cls, info in graph.classes.items():
        if info.module:
            file_map.setdefault(info.module, []).append(cls)
    
    for module, classes in file_map.items():
        safe = module.replace(".", "_")
        png_path = os.path.join(out_dir, f"class_{safe}.png")
    
        dot = render_class_diagram_dot(graph, focus_classes=classes)
        render_dot_to_png(dot, png_path)


    # ---------- Dependency diagram ----------
    dep_png = os.path.join(out_dir, "dependency_diagram.png")
    dep_dot = render_dependency_diagram_dot(graph)
    render_dot_to_png(dep_dot, dep_png)

    # ---------- Call diagrams (scoped, not global) ----------
    call_modules = group_calls_by_module(graph)
    for module, classes in call_modules.items():
        safe = module.replace(".", "_")
        png_path = os.path.join(out_dir, f"call_{safe}.png")

        dot = render_call_diagram_dot(graph, focus_classes=classes)
        render_dot_to_png(dot, png_path)

    shutil.rmtree(TEMP_REPO_DIR)

    print(f"✅ Diagrams generated at {out_dir}")
