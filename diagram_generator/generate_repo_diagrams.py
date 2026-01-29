import os
import shutil
import subprocess

from code_parser.language_detection import detect_language
from code_parser.parser_manager import get_parser

from diagram_generator.graph_model import DiagramGraph
from diagram_generator.ast_traverser import traverse
from diagram_generator.repo_scanner import scan_repo
from diagram_generator.renderers import (
    render_class_diagram_dot,
    render_dependency_diagram_dot,
    render_call_diagram_dot,
    render_dot_to_png,
    group_classes_by_module,
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

    graph = DiagramGraph()

    # ---------- Parse repository ----------
    for file in scan_repo(TEMP_REPO_DIR):
        language = detect_language(file)
        if not language:
            continue

        parser = get_parser(language)

        with open(file, "r", errors="ignore") as f:
            code = f.read()

        ast = parser.normalize(parser.parse(code))

        module_name = (
            file.replace(TEMP_REPO_DIR, "")
            .replace("/", ".")
            .replace("\\", ".")
            .strip(".")
        )

        traverse(ast, graph, module=module_name)

    out_dir = os.path.join(OUTPUT_BASE_DIR, repo, commit)
    os.makedirs(out_dir, exist_ok=True)

   # ---------- Global class diagram (pyreverse-style) ----------
    global_png = os.path.join(out_dir, "class_diagram_global.png")
    dot = render_class_diagram_dot(graph)
    render_dot_to_png(dot, global_png)
    
    
    # ---------- File-by-file class diagrams ----------
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

    # ---------- Call diagrams ----------
    call_modules = group_calls_by_module(graph)
    for module, classes in call_modules.items():
        safe = module.replace(".", "_")
        png_path = os.path.join(out_dir, f"call_{safe}.png")

        dot = render_call_diagram_dot(graph, focus_classes=classes)
        render_dot_to_png(dot, png_path)

    shutil.rmtree(TEMP_REPO_DIR)

    print(f"✅ Diagrams generated at {out_dir}")
