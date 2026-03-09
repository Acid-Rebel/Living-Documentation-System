from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import logging
import os
import sys
import time
import hashlib
import hmac
import base64
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import aiohttp

# Ensure living_docs_engine is in the path
engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'living_docs_engine'))
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lds", tags=["Living Docs Engine"])

# ── Helpers ──────────────────────────────────────────────────────────────────

# Simple in-memory cache for repo tree to avoid repeated GitHub API calls
_repo_tree_cache: Dict[str, Tuple[float, List[str]]] = {}
_CACHE_TTL = 120  # seconds


async def _fetch_repo_tree(owner: str, repo: str, repo_type: str) -> List[str]:
    """Fetch repository file paths from the hosting API (with short-lived cache)."""
    cache_key = f"{repo_type}:{owner}/{repo}"
    cached = _repo_tree_cache.get(cache_key)
    if cached and (time.time() - cached[0]) < _CACHE_TTL:
        return cached[1]

    headers: Dict[str, str] = {"Accept": "application/json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    result: List[str] = []
    if repo_type == "github":
        async with aiohttp.ClientSession() as session:
            for branch in ("main", "master"):
                api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = [item["path"] for item in data.get("tree", []) if item.get("type") == "blob"]
                        break

    _repo_tree_cache[cache_key] = (time.time(), result)
    return result


def _classify_file(path: str) -> Optional[str]:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".rb", ".cs", ".cpp", ".c", ".h", ".swift", ".kt"}:
        return "code"
    if ext in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"}:
        return "config"
    if ext in {".md", ".rst", ".txt", ".adoc"}:
        return "docs"
    if ext in {".html", ".css", ".scss", ".less"}:
        return "frontend"
    return None


def _infer_language(files: List[str]) -> str:
    counts: Dict[str, int] = {}
    ext_map = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
        ".java": "Java", ".go": "Go", ".rs": "Rust", ".rb": "Ruby",
        ".cs": "C#", ".cpp": "C++", ".swift": "Swift", ".kt": "Kotlin",
    }
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        lang = ext_map.get(ext)
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
    return max(counts, key=lambda k: counts[k]) if counts else "Unknown"


def _extract_modules(files: List[str]) -> List[Dict[str, Any]]:
    top_dirs: Dict[str, set] = {}
    skip = {"node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".git"}
    for f in files:
        parts = f.split("/")
        if len(parts) < 2:
            continue
        if _classify_file(f) is None:
            continue
        top = parts[0]
        if top.startswith(".") or top in skip:
            continue
        if top not in top_dirs:
            top_dirs[top] = set()
        if len(parts) >= 3:
            top_dirs[top].add(parts[1])
    dir_names = list(top_dirs.keys())
    modules = []
    for d in dir_names:
        deps = [o for o in dir_names if o != d and o in top_dirs[d]]
        modules.append({"name": d, "dependencies": deps})
    return modules


def _detect_external_packages(files: List[str]) -> List[str]:
    pkgs: set = set()
    for f in files:
        base = os.path.basename(f)
        if base == "package.json":
            pkgs.add("npm packages (see package.json)")
        elif base in ("requirements.txt", "pyproject.toml"):
            pkgs.add(f"pip packages (see {base})")
        elif base == "go.mod":
            pkgs.add("Go modules (see go.mod)")
        elif base == "Cargo.toml":
            pkgs.add("Rust crates (see Cargo.toml)")
        elif base in ("build.gradle", "pom.xml"):
            pkgs.add(f"JVM dependencies (see {base})")
    return sorted(pkgs) if pkgs else ["No manifest files detected"]


# ── Drift Report ─────────────────────────────────────────────────────────────

def _generate_drift_findings(files: List[str]) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    fid = 0

    code_files = [f for f in files if _classify_file(f) == "code"]
    doc_files = [f for f in files if _classify_file(f) == "docs"]
    config_files = [f for f in files if _classify_file(f) == "config"]

    documented_dirs = {os.path.dirname(d) for d in doc_files if "/" in d}
    code_dirs = {os.path.dirname(c) for c in code_files if "/" in c}
    # collapse to top-level dirs
    top_code_dirs = {d.split("/")[0] for d in code_dirs if d}
    top_doc_dirs = {d.split("/")[0] for d in documented_dirs if d}

    undocumented = top_code_dirs - top_doc_dirs
    for d in sorted(undocumented)[:6]:
        fid += 1
        findings.append({
            "id": f"drift-{fid}",
            "type": "MissingDocumentation",
            "severity": "medium",
            "description": f"Module '{d}/' contains source code but has no documentation files.",
            "file": d + "/"
        })

    has_root_readme = any(f.lower() in ("readme.md", "readme.rst", "readme.txt") for f in files)
    if not has_root_readme:
        fid += 1
        findings.append({
            "id": f"drift-{fid}",
            "type": "MissingDocumentation",
            "severity": "high",
            "description": "Repository has no root-level README file.",
            "file": "/"
        })

    if config_files and not any("doc" in os.path.dirname(f).lower() for f in doc_files):
        fid += 1
        findings.append({
            "id": f"drift-{fid}",
            "type": "ConfigUndocumented",
            "severity": "low",
            "description": f"Found {len(config_files)} config file(s) but no dedicated docs/ directory.",
            "file": config_files[0] if config_files else ""
        })

    high = sum(1 for f in findings if f["severity"] == "high")
    med = sum(1 for f in findings if f["severity"] == "medium")
    low = sum(1 for f in findings if f["severity"] == "low")

    return {
        "summary": {
            "total_findings": len(findings),
            "high_severity": high,
            "medium_severity": med,
            "low_severity": low,
            "files_analyzed": len(files),
            "code_files": len(code_files),
            "doc_files": len(doc_files),
        },
        "findings": findings,
    }


# ── Semantic Insights ────────────────────────────────────────────────────────

def _generate_semantic_insights(files: List[str]) -> Dict[str, Any]:
    symbols: List[Dict[str, Any]] = []
    relations: List[Dict[str, Any]] = []

    code_files = [f for f in files if _classify_file(f) == "code"]
    primary_lang = _infer_language(files)

    dir_files: Dict[str, List[str]] = {}
    skip = {"node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".git"}
    for f in code_files:
        parts = f.split("/")
        if len(parts) >= 2 and not parts[0].startswith(".") and parts[0] not in skip:
            top = parts[0]
            dir_files.setdefault(top, []).append(f)

    for mod_name, mod_files in sorted(dir_files.items(), key=lambda x: -len(x[1])):
        complexity = "high" if len(mod_files) > 15 else ("medium" if len(mod_files) > 5 else "low")
        symbols.append({
            "name": mod_name,
            "type": "module",
            "complexity": complexity,
            "file_count": len(mod_files),
            "language": primary_lang,
        })

    mod_names = list(dir_files.keys())
    for i, mod_a in enumerate(mod_names):
        for mod_b in mod_names[i + 1:]:
            a_refs_b = any(mod_b.lower() in f.lower() for f in dir_files.get(mod_a, []))
            b_refs_a = any(mod_a.lower() in f.lower() for f in dir_files.get(mod_b, []))
            if a_refs_b:
                relations.append({"source": mod_a, "target": mod_b, "type": "imports"})
            if b_refs_a:
                relations.append({"source": mod_b, "target": mod_a, "type": "imports"})

    if not relations and len(mod_names) >= 2:
        for mn in mod_names[1:]:
            relations.append({"source": mod_names[0], "target": mn, "type": "contains"})

    return {
        "symbols": symbols[:20],
        "relations": relations[:30],
        "primary_language": primary_lang,
        "total_code_files": len(code_files),
    }


# ── Endpoints ────────────────────────────────────────────────────────────────

# --- API Docs Download Endpoint ---
@router.get("/api-docs-download")
async def download_api_docs(owner: str, repo: str, repo_type: str = "github"):
    """Download OpenAPI/Swagger docs for the repo."""
    # For demo: return a static OpenAPI spec. Replace with real generator if needed.
    openapi = {
        "openapi": "3.0.0",
        "info": {"title": f"{repo} API", "version": "1.0.0"},
        "paths": {"/": {"get": {"summary": "Root endpoint", "responses": {"200": {"description": "OK"}}}}}
    }
    return JSONResponse(content=openapi)

@router.get("/drift-report")
async def get_drift_report(owner: str, repo: str, repo_type: str = "github"):
    """Returns documentation drift report analysed from the live repository tree."""
    try:
        files = await _fetch_repo_tree(owner, repo, repo_type)
        if not files:
            return {
                "status": "success",
                "data": {
                    "summary": {"total_findings": 1, "high_severity": 0, "medium_severity": 0, "low_severity": 1, "files_analyzed": 0, "code_files": 0, "doc_files": 0},
                    "findings": [{"id": "info-1", "type": "Info", "severity": "low",
                                  "description": f"Could not fetch the repository tree for {owner}/{repo}. It may be private or the GitHub API rate-limit was hit.",
                                  "file": ""}],
                },
            }
        return {"status": "success", "data": _generate_drift_findings(files)}
    except Exception as e:
        logger.error(f"Error generating drift report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/semantic-insights")
async def get_semantic_insights(owner: str, repo: str, repo_type: str = "github"):
    """Returns semantic insights derived from the live repository tree."""
    try:
        files = await _fetch_repo_tree(owner, repo, repo_type)
        if not files:
            return {"status": "success", "data": {"symbols": [], "relations": [], "primary_language": "Unknown", "total_code_files": 0}}
        return {"status": "success", "data": _generate_semantic_insights(files)}
    except Exception as e:
        logger.error(f"Error generating semantic insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dependency-analysis")
async def get_dependency_analysis(owner: str, repo: str, repo_type: str = "github"):
    """Returns dependency analysis from the live repository tree."""
    try:
        files = await _fetch_repo_tree(owner, repo, repo_type)
        if not files:
            return {"status": "success", "data": {"modules": [], "external_packages": [], "total_files": 0, "primary_language": "Unknown"}}
        return {
            "status": "success",
            "data": {
                "modules": _extract_modules(files),
                "external_packages": _detect_external_packages(files),
                "total_files": len(files),
                "primary_language": _infer_language(files),
            },
        }
    except Exception as e:
        logger.error(f"Error generating dependency analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── AI-Enhanced Diagrams ─────────────────────────────────────────────────────

def _sanitize_mermaid_id(name: str) -> str:
    """Sanitize a module name into a valid Mermaid node identifier (alphanumeric + underscore)."""
    import re as _re
    sid = _re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Ensure it doesn't start with a digit
    if sid and sid[0].isdigit():
        sid = "m_" + sid
    return sid or "mod"


def _detect_framework(files: List[str]) -> Dict[str, Any]:
    """Detect the web framework and project type from file paths."""
    basenames = {os.path.basename(f) for f in files}
    all_paths = "\n".join(files).lower()

    info: Dict[str, Any] = {"framework": "unknown", "type": "generic"}

    # Django
    if "manage.py" in basenames and ("settings.py" in basenames or "wsgi.py" in basenames):
        info["framework"] = "django"
        info["type"] = "web"
    # Flask
    elif any(f.endswith("app.py") or f.endswith("flask_app.py") for f in files) and "requirements.txt" in basenames:
        if "templates" in all_paths or "flask" in all_paths:
            info["framework"] = "flask"
            info["type"] = "web"
    # FastAPI
    if "main.py" in basenames and ("uvicorn" in all_paths or "fastapi" in all_paths):
        info["framework"] = "fastapi"
        info["type"] = "api"
    # Next.js
    if "next.config.ts" in basenames or "next.config.js" in basenames or "next.config.mjs" in basenames:
        info["framework"] = "nextjs"
        info["type"] = "web"
    # Express
    elif "package.json" in basenames and ("routes" in all_paths or "controllers" in all_paths) and "server" in all_paths:
        info["framework"] = "express"
        info["type"] = "api"
    # React (generic)
    elif "package.json" in basenames and ("src/app" in all_paths or "src/components" in all_paths):
        info["framework"] = "react"
        info["type"] = "web"
    # Spring Boot
    if any("application.properties" in f or "application.yml" in f for f in files):
        info["framework"] = "spring"
        info["type"] = "web"
    # Rails
    if "Gemfile" in basenames and "config/routes.rb" in files:
        info["framework"] = "rails"
        info["type"] = "web"

    return info


def _analyze_modules(files: List[str]) -> List[Dict[str, Any]]:
    """Deep analysis of each top-level module from file paths."""
    skip = {"node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".git", ".github", ".vscode"}
    modules: Dict[str, Dict[str, Any]] = {}

    for f in files:
        parts = f.split("/")
        if len(parts) < 2 or parts[0].startswith(".") or parts[0] in skip:
            continue
        top = parts[0]
        if top not in modules:
            modules[top] = {
                "name": top,
                "files": [],
                "basenames": set(),
                "subdirs": set(),
                "extensions": {},
                "has_models": False,
                "has_views": False,
                "has_urls": False,
                "has_serializers": False,
                "has_admin": False,
                "has_forms": False,
                "has_tests": False,
                "has_templates": False,
                "has_migrations": False,
                "has_services": False,
                "has_controllers": False,
                "has_routes": False,
                "has_middleware": False,
                "has_config": False,
                "has_static": False,
                "role": "module",
            }
        m = modules[top]
        m["files"].append(f)
        bn = os.path.basename(f).lower()
        m["basenames"].add(bn)
        if len(parts) >= 3:
            m["subdirs"].add(parts[1])
        ext = os.path.splitext(f)[1].lower()
        if ext:
            m["extensions"][ext] = m["extensions"].get(ext, 0) + 1

        # Detect key file types
        if bn in ("models.py", "model.py", "models.ts", "models.js", "schema.py", "schemas.py"):
            m["has_models"] = True
        if bn in ("views.py", "view.py", "views.ts"):
            m["has_views"] = True
        if bn in ("urls.py", "routes.py", "router.py", "routes.ts", "routes.js"):
            m["has_urls"] = True
        if bn in ("serializers.py", "serializer.py"):
            m["has_serializers"] = True
        if bn in ("admin.py",):
            m["has_admin"] = True
        if bn in ("forms.py", "form.py"):
            m["has_forms"] = True
        if bn.startswith("test") or "tests" in parts:
            m["has_tests"] = True
        if "templates" in parts or "template" in parts:
            m["has_templates"] = True
        if "migrations" in parts:
            m["has_migrations"] = True
        if bn in ("services.py", "service.py", "services.ts", "service.ts"):
            m["has_services"] = True
        if bn in ("controllers.py", "controller.py", "controllers.ts", "controller.ts"):
            m["has_controllers"] = True
        if bn in ("middleware.py", "middleware.ts", "middleware.js"):
            m["has_middleware"] = True
        if _classify_file(f) == "config":
            m["has_config"] = True
        if "static" in parts or ext in (".css", ".scss", ".less"):
            m["has_static"] = True

    # Infer roles
    for m in modules.values():
        bn = m["basenames"]
        name_lower = m["name"].lower()
        fc = len(m["files"])

        if any(x in bn for x in ("settings.py", "wsgi.py", "asgi.py")) or name_lower.endswith("_backend"):
            m["role"] = "config"
        elif name_lower in ("static", "staticfiles", "assets", "public", "media"):
            m["role"] = "static"
        elif name_lower in ("templates",):
            m["role"] = "templates"
        elif name_lower in ("tests", "test", "spec", "specs", "__tests__"):
            m["role"] = "tests"
        elif name_lower in ("docs", "documentation", "doc"):
            m["role"] = "docs"
        elif name_lower in ("frontend", "client", "web", "ui", "app"):
            m["role"] = "frontend"
        elif m["has_models"] and m["has_views"]:
            m["role"] = "app"
        elif m["has_models"]:
            m["role"] = "data"
        elif m["has_controllers"] or m["has_routes"]:
            m["role"] = "api"
        elif m["has_services"]:
            m["role"] = "service"
        elif fc <= 3 and m["has_config"]:
            m["role"] = "config"
        else:
            m["role"] = "module"

    result = list(modules.values())
    # Clean up non-serializable sets
    for m in result:
        m["basenames"] = sorted(m["basenames"])
        m["subdirs"] = sorted(m["subdirs"])
        m["file_count"] = len(m["files"])
        del m["files"]
    return sorted(result, key=lambda x: -x["file_count"])


def _generate_diagram_mermaid(files: List[str], diagram_type: str) -> str:
    """Generate meaningful Mermaid diagrams using deep file structure analysis."""
    fw_info = _detect_framework(files)
    modules = _analyze_modules(files)

    if not modules:
        return ""

    if diagram_type == "dependency":
        return _gen_architecture_diagram(modules, fw_info)
    elif diagram_type == "class":
        return _gen_module_structure_diagram(modules, fw_info)
    else:
        return _gen_request_flow_diagram(modules, fw_info)


def _gen_architecture_diagram(modules: List[Dict], fw_info: Dict) -> str:
    """Generate a layered architecture / dependency diagram."""
    lines = ["graph TD"]

    # Classify modules into architectural layers
    config_mods = [m for m in modules if m["role"] == "config"]
    app_mods = [m for m in modules if m["role"] in ("app", "module", "data", "service", "api")]
    frontend_mods = [m for m in modules if m["role"] == "frontend"]
    static_mods = [m for m in modules if m["role"] in ("static", "templates")]
    test_mods = [m for m in modules if m["role"] == "tests"]
    other_mods = [m for m in modules if m["role"] in ("docs",)]

    framework = fw_info.get("framework", "unknown")

    # Entry point
    lines.append('    Client(["fa:fa-user Client / Browser"])')

    # Config layer
    if config_mods:
        lines.append("    subgraph CONFIG[\"Configuration\"]")
        for m in config_mods:
            sid = _sanitize_mermaid_id(m["name"])
            lines.append(f'        {sid}["{m["name"]}"]')
        lines.append("    end")

    # Application layer
    if app_mods:
        label = "Django Apps" if framework == "django" else "Application Modules"
        lines.append(f'    subgraph APPS["{label}"]')
        for m in app_mods:
            sid = _sanitize_mermaid_id(m["name"])
            components = []
            if m.get("has_models"):
                components.append("Models")
            if m.get("has_views"):
                components.append("Views")
            if m.get("has_serializers"):
                components.append("Serializers")
            if m.get("has_urls"):
                components.append("URLs")
            if m.get("has_services"):
                components.append("Services")
            if m.get("has_controllers"):
                components.append("Controllers")
            comp_str = " | ".join(components) if components else f'{m["file_count"]} files'
            lines.append(f'        {sid}["{m["name"]}<br/><small>{comp_str}</small>"]')
        lines.append("    end")

    # Frontend / Static layer
    if frontend_mods or static_mods:
        lines.append('    subgraph UI["Frontend / Static"]')
        for m in frontend_mods + static_mods:
            sid = _sanitize_mermaid_id(m["name"])
            lines.append(f'        {sid}["{m["name"]} - {m["file_count"]} files"]')
        lines.append("    end")

    # Data layer
    lines.append('    DB[("fa:fa-database Database")]')

    # Draw connections
    if config_mods:
        lines.append(f"    Client --> CONFIG")
        lines.append(f"    CONFIG --> APPS")
    elif app_mods:
        first_app = _sanitize_mermaid_id(app_mods[0]["name"])
        lines.append(f"    Client --> {first_app}")

    # Inter-app dependencies: check if module name appears in another module's subdirs or basenames
    app_names = {m["name"] for m in app_mods}
    for m in app_mods:
        sid = _sanitize_mermaid_id(m["name"])
        # Models → Database
        if m.get("has_models"):
            lines.append(f"    {sid} --> DB")
        # Cross-module references (check if other module names appear in subdirs/basenames)
        for other in app_mods:
            if other["name"] == m["name"]:
                continue
            other_lower = other["name"].lower()
            # Check if this module references the other through its basenames or subdirectories
            all_names_str = " ".join(m.get("basenames", []) + m.get("subdirs", []))
            if other_lower in all_names_str:
                oid = _sanitize_mermaid_id(other["name"])
                lines.append(f"    {sid} -.-> {oid}")

    if app_mods and (frontend_mods or static_mods):
        lines.append("    APPS --> UI")

    # Styling
    lines.append("    style Client fill:#e1d5e7,stroke:#9673a6,color:#333")
    lines.append("    style DB fill:#dae8fc,stroke:#6c8ebf,color:#333")
    if config_mods:
        lines.append("    style CONFIG fill:#fff2cc,stroke:#d6b656,color:#333")
    if app_mods:
        lines.append("    style APPS fill:#d5e8d4,stroke:#82b366,color:#333")
    if frontend_mods or static_mods:
        lines.append("    style UI fill:#f8cecc,stroke:#b85450,color:#333")

    return "\n".join(lines)


def _gen_module_structure_diagram(modules: List[Dict], fw_info: Dict) -> str:
    """Generate a module structure diagram showing internal components of each module."""
    lines = ["graph LR"]
    framework = fw_info.get("framework", "unknown")

    app_mods = [m for m in modules if m["role"] in ("app", "module", "data", "service", "api", "config")]
    if not app_mods:
        app_mods = modules[:6]

    for m in app_mods[:8]:  # Limit to 8 modules for readability
        sid = _sanitize_mermaid_id(m["name"])
        role_label = m["role"].capitalize()
        lines.append(f'    subgraph {sid}_grp["{m["name"]} ({role_label})"]')

        # Show detected components as nodes
        comp_idx = 0
        components = []
        if m.get("has_models"):
            components.append(("models", "fa:fa-database Models"))
        if m.get("has_views"):
            components.append(("views", "fa:fa-eye Views"))
        if m.get("has_urls"):
            components.append(("urls", "fa:fa-link URLs / Routes"))
        if m.get("has_serializers"):
            components.append(("serial", "fa:fa-exchange-alt Serializers"))
        if m.get("has_admin"):
            components.append(("admin", "fa:fa-cog Admin"))
        if m.get("has_forms"):
            components.append(("forms", "fa:fa-wpforms Forms"))
        if m.get("has_templates"):
            components.append(("tpl", "fa:fa-file-code Templates"))
        if m.get("has_services"):
            components.append(("svc", "fa:fa-server Services"))
        if m.get("has_controllers"):
            components.append(("ctrl", "fa:fa-gamepad Controllers"))
        if m.get("has_tests"):
            components.append(("tests", "fa:fa-flask Tests"))
        if m.get("has_migrations"):
            components.append(("migr", "fa:fa-history Migrations"))
        if m.get("has_middleware"):
            components.append(("mw", "fa:fa-filter Middleware"))

        if not components:
            # Show file extension breakdown instead
            top_exts = sorted(m.get("extensions", {}).items(), key=lambda x: -x[1])[:4]
            for ext, cnt in top_exts:
                comp_idx += 1
                cid = f"{sid}_f{comp_idx}"
                lines.append(f'        {cid}["{ext} - {cnt} files"]')
        else:
            for comp_key, comp_label in components:
                cid = f"{sid}_{comp_key}"
                lines.append(f'        {cid}["{comp_label}"]')

            # Internal arrows (if it's an app with the typical Django flow)
            if m.get("has_urls") and m.get("has_views"):
                lines.append(f"        {sid}_urls --> {sid}_views")
            if m.get("has_views") and m.get("has_models"):
                lines.append(f"        {sid}_views --> {sid}_models")
            if m.get("has_views") and m.get("has_serializers"):
                lines.append(f"        {sid}_views --> {sid}_serial")
            if m.get("has_serializers") and m.get("has_models"):
                lines.append(f"        {sid}_serial --> {sid}_models")

        lines.append("    end")

    # Cross-module connections
    app_names = {m["name"].lower() for m in app_mods[:8]}
    for m in app_mods[:8]:
        sid = _sanitize_mermaid_id(m["name"])
        all_names_str = " ".join(m.get("basenames", []) + m.get("subdirs", []))
        for other in app_mods[:8]:
            if other["name"] == m["name"]:
                continue
            if other["name"].lower() in all_names_str:
                oid = _sanitize_mermaid_id(other["name"])
                lines.append(f"    {sid}_grp -.-> {oid}_grp")

    return "\n".join(lines)


def _gen_request_flow_diagram(modules: List[Dict], fw_info: Dict) -> str:
    """Generate a request flow / sequence diagram based on detected framework."""
    lines = ["sequenceDiagram"]
    framework = fw_info.get("framework", "unknown")

    # Find relevant modules
    config_mod = next((m for m in modules if m["role"] == "config"), None)
    app_mods = [m for m in modules if m["role"] in ("app", "module", "data", "service", "api")][:4]

    if not app_mods:
        app_mods = [m for m in modules if m["role"] != "static"][:4]

    if not app_mods:
        return ""

    # Participants
    lines.append("    actor User")

    if framework == "django":
        lines.append("    participant Router as URL Router")
        for m in app_mods:
            sid = _sanitize_mermaid_id(m["name"])
            lines.append(f"    participant {sid} as {m['name']}")
        lines.append("    participant DB as Database")

        primary = _sanitize_mermaid_id(app_mods[0]["name"])
        lines.append("    User->>Router: HTTP Request")
        lines.append(f"    Router->>+{primary}: Route to view")

        if app_mods[0].get("has_serializers"):
            lines.append(f"    {primary}->>+{primary}: Validate via Serializer")

        if app_mods[0].get("has_models"):
            lines.append(f"    {primary}->>+DB: Query Model")
            lines.append(f"    DB-->>-{primary}: QuerySet result")

        # Inter-app calls
        if len(app_mods) > 1:
            second = _sanitize_mermaid_id(app_mods[1]["name"])
            lines.append(f"    {primary}->>+{second}: Reference {app_mods[1]['name']} data")
            if app_mods[1].get("has_models"):
                lines.append(f"    {second}->>DB: Query {app_mods[1]['name']} Model")
                lines.append(f"    DB-->>{second}: Result")
            lines.append(f"    {second}-->>-{primary}: Return data")

        if app_mods[0].get("has_templates"):
            lines.append(f"    {primary}->>+{primary}: Render Template")

        lines.append(f"    {primary}-->>-Router: HTTP Response")
        lines.append("    Router-->>User: Rendered Page / JSON")

    elif framework in ("fastapi", "flask", "express"):
        lines.append("    participant API as API Router")
        for m in app_mods:
            sid = _sanitize_mermaid_id(m["name"])
            lines.append(f"    participant {sid} as {m['name']}")
        lines.append("    participant DB as Database")

        primary = _sanitize_mermaid_id(app_mods[0]["name"])
        lines.append("    User->>API: REST Request")
        lines.append(f"    API->>+{primary}: Route handler")

        if app_mods[0].get("has_services"):
            lines.append(f"    {primary}->>+{primary}: Service logic")

        lines.append(f"    {primary}->>+DB: Data operation")
        lines.append(f"    DB-->>-{primary}: Result")
        lines.append(f"    {primary}-->>-API: Response data")
        lines.append("    API-->>User: JSON Response")

    elif framework == "nextjs":
        lines.append("    participant Next as Next.js Server")
        lines.append("    participant Pages as Pages / Routes")
        lines.append("    participant Components as Components")
        lines.append("    participant API as API Routes")
        lines.append("    participant Backend as Backend / DB")

        lines.append("    User->>Next: Page Request")
        lines.append("    Next->>+Pages: Route to Page")
        lines.append("    Pages->>+Components: Render Components")
        lines.append("    Components->>+API: Fetch Data (Client)")
        lines.append("    API->>+Backend: Forward Request")
        lines.append("    Backend-->>-API: Data")
        lines.append("    API-->>-Components: JSON Response")
        lines.append("    Components-->>-Pages: Rendered UI")
        lines.append("    Pages-->>-Next: HTML + JS")
        lines.append("    Next-->>User: Rendered Page")

    else:
        # Generic flow
        for m in app_mods:
            sid = _sanitize_mermaid_id(m["name"])
            lines.append(f"    participant {sid} as {m['name']}")
        lines.append("    participant DB as Database")

        primary = _sanitize_mermaid_id(app_mods[0]["name"])
        lines.append(f"    User->>+{primary}: Request")

        for i in range(len(app_mods) - 1):
            si = _sanitize_mermaid_id(app_mods[i]["name"])
            si1 = _sanitize_mermaid_id(app_mods[i + 1]["name"])
            lines.append(f"    {si}->>+{si1}: Process {app_mods[i + 1]['name']}")

        last = _sanitize_mermaid_id(app_mods[-1]["name"])
        lines.append(f"    {last}->>+DB: Data operation")
        lines.append(f"    DB-->>-{last}: Result")

        for i in range(len(app_mods) - 1, 0, -1):
            si = _sanitize_mermaid_id(app_mods[i]["name"])
            si_prev = _sanitize_mermaid_id(app_mods[i - 1]["name"])
            lines.append(f"    {si}-->>-{si_prev}: Return result")

        lines.append(f"    {primary}-->>-User: Response")

    return "\n".join(lines)


@router.get("/diagrams")
async def get_diagrams(owner: str, repo: str, repo_type: str = "github"):
    """Returns AI-enhanced Mermaid diagrams for the repository."""
    try:
        files = await _fetch_repo_tree(owner, repo, repo_type)
        if not files:
            return {
                "status": "success",
                "data": {
                    "class_diagram": "",
                    "dependency_diagram": "",
                    "call_diagram": "",
                    "diagram_types": ["class", "dependency", "call"],
                }
            }
        return {
            "status": "success",
            "data": {
                "class_diagram": _generate_diagram_mermaid(files, "class"),
                "dependency_diagram": _generate_diagram_mermaid(files, "dependency"),
                "call_diagram": _generate_diagram_mermaid(files, "call"),
                "diagram_types": ["class", "dependency", "call"],
            }
        }
    except Exception as e:
        logger.error(f"Error generating diagrams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── NLP Summarizer ───────────────────────────────────────────────────────────

def _generate_nlp_summary(files: List[str]) -> Dict[str, Any]:
    """Generate NLP-style summary of the repository."""
    code_files = [f for f in files if _classify_file(f) == "code"]
    doc_files = [f for f in files if _classify_file(f) == "docs"]
    config_files = [f for f in files if _classify_file(f) == "config"]
    frontend_files = [f for f in files if _classify_file(f) == "frontend"]
    lang = _infer_language(files)

    # Identify modules
    skip = {"node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".git"}
    modules: Dict[str, Dict[str, Any]] = {}
    for f in code_files:
        parts = f.split("/")
        if len(parts) >= 2 and not parts[0].startswith(".") and parts[0] not in skip:
            top = parts[0]
            if top not in modules:
                modules[top] = {"files": [], "extensions": set()}
            modules[top]["files"].append(f)
            modules[top]["extensions"].add(os.path.splitext(f)[1])

    # Build summary
    module_summaries = []
    for name, info in sorted(modules.items(), key=lambda x: -len(x[1]["files"])):
        exts = ", ".join(sorted(info["extensions"]))
        file_count = len(info["files"])
        complexity = "high" if file_count > 15 else ("medium" if file_count > 5 else "low")
        module_summaries.append({
            "name": name,
            "file_count": file_count,
            "extensions": exts,
            "complexity": complexity,
            "description": f"Module '{name}' contains {file_count} source file(s) ({exts}). Complexity: {complexity}.",
        })

    # Generate overall narrative
    overview = f"This repository contains {len(files)} total files: {len(code_files)} source code, {len(doc_files)} documentation, {len(config_files)} configuration, and {len(frontend_files)} frontend files."
    overview += f" The primary language is {lang}."
    overview += f" The codebase is organized into {len(modules)} main modules."

    key_findings = []
    if len(code_files) > 50:
        key_findings.append("Large codebase with significant engineering investment.")
    if doc_files:
        key_findings.append(f"Documentation is present with {len(doc_files)} doc file(s).")
    else:
        key_findings.append("No dedicated documentation files found — documentation may be inline or missing.")
    if config_files:
        key_findings.append(f"{len(config_files)} configuration file(s) detected, suggesting configurable deployment.")
    if frontend_files:
        key_findings.append(f"Frontend layer detected with {len(frontend_files)} file(s).")

    return {
        "overview": overview,
        "primary_language": lang,
        "total_files": len(files),
        "code_files": len(code_files),
        "doc_files": len(doc_files),
        "config_files": len(config_files),
        "frontend_files": len(frontend_files),
        "module_count": len(modules),
        "module_summaries": module_summaries[:15],
        "key_findings": key_findings,
    }


@router.get("/nlp-summary")
async def get_nlp_summary(owner: str, repo: str, repo_type: str = "github"):
    """Returns NLP-generated summary of the repository."""
    try:
        files = await _fetch_repo_tree(owner, repo, repo_type)
        if not files:
            return {
                "status": "success",
                "data": {
                    "overview": "Could not fetch repository data.",
                    "primary_language": "Unknown",
                    "total_files": 0,
                    "code_files": 0,
                    "doc_files": 0,
                    "config_files": 0,
                    "frontend_files": 0,
                    "module_count": 0,
                    "module_summaries": [],
                    "key_findings": [],
                }
            }
        return {"status": "success", "data": _generate_nlp_summary(files)}
    except Exception as e:
        logger.error(f"Error generating NLP summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Pull Request Management ─────────────────────────────────────────────────

# In-memory PR store (tracks both local and GitHub PRs)
_pr_store: Dict[str, Dict[str, Any]] = {}
_pr_counter: int = 0

# Track last-seen commit per repo (for auto-detection)
_repo_last_commit: Dict[str, str] = {}


def _github_headers() -> Dict[str, str]:
    """Build GitHub API headers with auth if token is set."""
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


class PRCreateRequest(BaseModel):
    title: str
    description: str
    doc_content: str
    author: str
    repo_owner: str
    repo_name: str


class PRReviewRequest(BaseModel):
    reviewer: str
    status: str  # "APPROVED" or "CHANGES_REQUESTED"
    comment: Optional[str] = None


async def _get_latest_commit(owner: str, repo: str) -> Optional[Dict[str, Any]]:
    """Fetch the latest commit from the default branch."""
    headers = _github_headers()
    async with aiohttp.ClientSession() as session:
        for branch in ("main", "master"):
            url = f"https://api.github.com/repos/{owner}/{repo}/commits?sha={branch}&per_page=1"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    commits = await resp.json()
                    if commits:
                        c = commits[0]
                        return {
                            "sha": c["sha"],
                            "message": c["commit"]["message"],
                            "author": c["commit"]["author"]["name"],
                            "date": c["commit"]["author"]["date"],
                            "branch": branch,
                        }
    return None


async def _get_current_readme(owner: str, repo: str, branch: str = "main") -> Optional[Dict[str, str]]:
    """Fetch the current README content and its SHA."""
    headers = _github_headers()
    async with aiohttp.ClientSession() as session:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md?ref={branch}"
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                content = base64.b64decode(data["content"]).decode("utf-8")
                return {"content": content, "sha": data["sha"], "branch": branch}
    return None


async def _create_github_pr(owner: str, repo: str, title: str, body: str,
                             doc_content: str, base_branch: str) -> Optional[Dict[str, Any]]:
    """Create a real GitHub PR with updated README content.

    Steps: create branch → update README on that branch → open PR.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN not set — cannot create real GitHub PR")
        return None

    headers = _github_headers()
    branch_name = f"docs/auto-update-{int(time.time())}"

    async with aiohttp.ClientSession() as session:
        # 1. Get base branch HEAD SHA
        ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{base_branch}"
        async with session.get(ref_url, headers=headers) as resp:
            if resp.status != 200:
                logger.error(f"Failed to get base branch ref: {resp.status}")
                return None
            base_sha = (await resp.json())["object"]["sha"]

        # 2. Create new branch
        create_ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        async with session.post(create_ref_url, headers=headers, json={
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha,
        }) as resp:
            if resp.status not in (200, 201):
                err = await resp.text()
                logger.error(f"Failed to create branch: {resp.status} {err}")
                return None

        # 3. Get current README SHA on the new branch (needed for update)
        readme_info = await _get_current_readme(owner, repo, branch_name)
        readme_sha = readme_info["sha"] if readme_info else None

        # 4. Update README.md on the new branch
        content_url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
        encoded_content = base64.b64encode(doc_content.encode("utf-8")).decode("utf-8")
        update_body: Dict[str, Any] = {
            "message": f"docs: {title}",
            "content": encoded_content,
            "branch": branch_name,
        }
        if readme_sha:
            update_body["sha"] = readme_sha

        async with session.put(content_url, headers=headers, json=update_body) as resp:
            if resp.status not in (200, 201):
                err = await resp.text()
                logger.error(f"Failed to update README: {resp.status} {err}")
                return None

        # 5. Create Pull Request
        pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        async with session.post(pr_url, headers=headers, json={
            "title": title,
            "body": body,
            "head": branch_name,
            "base": base_branch,
        }) as resp:
            if resp.status in (200, 201):
                pr_data = await resp.json()
                return {
                    "number": pr_data["number"],
                    "html_url": pr_data["html_url"],
                    "branch": branch_name,
                    "state": pr_data["state"],
                }
            else:
                err = await resp.text()
                logger.error(f"Failed to create PR: {resp.status} {err}")
                return None


async def _generate_updated_readme(owner: str, repo: str, files: List[str],
                                    current_readme: str, commit_info: Dict) -> str:
    """Generate a rich README with diagrams, architecture insights, and NLP summary.

    Pulls together all analysis pipelines to produce a comprehensive README.
    """
    fw = _detect_framework(files)
    modules = _analyze_modules(files)
    nlp = _generate_nlp_summary(files)

    framework = fw.get("framework", "unknown")
    lang = nlp.get("primary_language", "Unknown")
    total_files = nlp.get("total_files", 0)
    mod_count = nlp.get("module_count", 0)
    overview = nlp.get("overview", f"A {lang} project.")
    project_name = repo.replace("-", " ").replace("_", " ").title()

    # ── Generate all three Mermaid diagrams ──
    arch_diagram = _generate_diagram_mermaid(files, "dependency")
    module_diagram = _generate_diagram_mermaid(files, "class")
    flow_diagram = _generate_diagram_mermaid(files, "sequence")

    # ── Module descriptions ──
    mod_lines = []
    for ms in nlp.get("module_summaries", [])[:12]:
        components = ms.get("components", [])
        comp_str = f" — contains: {', '.join(components[:5])}" if components else ""
        mod_lines.append(f"| **{ms['name']}/** | {ms['description']} | {ms['file_count']} files |{comp_str}")

    # ── Key findings ──
    findings = nlp.get("key_findings", [])

    # ── External packages ──
    ext_pkgs = _detect_external_packages(files)
    has_deps = ext_pkgs and ext_pkgs[0] != "No manifest files detected"

    # ── File type breakdown from NLP stats ──
    stats = nlp.get("stats", {})
    src_count = stats.get("source_files", 0)
    doc_count = stats.get("documentation_files", 0)
    config_count = stats.get("config_files", 0)
    frontend_count = stats.get("frontend_files", 0)
    test_count = stats.get("test_files", 0)

    # ──────── Build the README ────────

    readme = f"""# {project_name}

> {overview}

[![Auto-docs](https://img.shields.io/badge/docs-auto--generated-blue)]() [![Framework](https://img.shields.io/badge/framework-{framework}-green)]() [![Language](https://img.shields.io/badge/language-{lang}-orange)]()

## Tech Stack

| | |
|---|---|
| **Language** | {lang} |
| **Framework** | {framework.capitalize() if framework != 'unknown' else 'Not detected'} |
| **Total Files** | {total_files} |
| **Modules** | {mod_count} |
| **Source Files** | {src_count} |
| **Frontend Files** | {frontend_count} |
| **Test Files** | {test_count} |
| **Config Files** | {config_count} |
| **Documentation** | {doc_count} |

"""

    # ── Architecture Diagram ──
    if arch_diagram:
        readme += f"""## System Architecture

The following diagram shows the high-level architecture and how modules relate to each other:

```mermaid
{arch_diagram}
```

"""

    # ── Project Structure ──
    if mod_lines:
        readme += "## Project Structure\n\n"
        readme += "| Module | Description | Size | Key Components |\n"
        readme += "|--------|-------------|------|----------------|\n"
        readme += "\n".join(mod_lines) + "\n\n"
    else:
        readme += "## Project Structure\n\nNo distinct modules detected.\n\n"

    # ── Module Detail Diagram ──
    if module_diagram:
        readme += f"""## Module Internals

Shows the internal components and relationships within each module:

```mermaid
{module_diagram}
```

"""

    # ── Request / Data Flow ──
    if flow_diagram:
        readme += f"""## Request Flow

How a typical request flows through the system:

```mermaid
{flow_diagram}
```

"""

    # ── Key Insights ──
    if findings:
        readme += "## Key Insights\n\n"
        for f in findings[:8]:
            readme += f"- {f}\n"
        readme += "\n"

    # ── Dependencies ──
    if has_deps:
        readme += "## Dependencies\n\n"
        for pkg in ext_pkgs:
            readme += f"- `{pkg}`\n"
        readme += "\n"

    # ── Getting Started ──
    if framework != "unknown":
        readme += "## Getting Started\n\n"
        start_cmds = {
            "django": "```bash\\npip install -r requirements.txt\\npython manage.py migrate\\npython manage.py runserver\\n```",
            "flask": "```bash\\npip install -r requirements.txt\\npython app.py\\n```",
            "fastapi": "```bash\\npip install -r requirements.txt\\nuvicorn main:app --reload\\n```",
            "nextjs": "```bash\\nnpm install\\nnpm run dev\\n```",
            "express": "```bash\\nnpm install\\nnpm start\\n```",
            "react": "```bash\\nnpm install\\nnpm start\\n```",
            "spring": "```bash\\n./mvnw spring-boot:run\\n```",
            "rails": "```bash\\nbundle install\\nrails server\\n```",
        }
        cmd = start_cmds.get(framework, "```bash\\n# Install dependencies and run the project\\n```")
        # Unescape the \\n for actual newlines
        readme += cmd.replace("\\n", "\n") + "\n\n"

    # ── Footer ──
    readme += f"""---

<sub>Auto-generated by [Living Documentation System](https://github.com/Shan713/Living-Documentation-System) on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} — triggered by commit [`{commit_info.get('sha', 'N/A')[:7]}`] — {commit_info.get('message', 'N/A')}</sub>
"""

    return readme


async def _auto_update_docs(owner: str, repo: str, commit_info: Dict[str, Any]):
    """Background task: regenerate docs and create a GitHub PR."""
    try:
        logger.info(f"Auto-update triggered for {owner}/{repo} by commit {commit_info.get('sha', '?')[:7]}")

        files = await _fetch_repo_tree(owner, repo, "github")
        if not files:
            logger.warning(f"Could not fetch tree for {owner}/{repo}")
            return

        branch = commit_info.get("branch", "main")
        current = await _get_current_readme(owner, repo, branch)
        current_readme = current["content"] if current else ""

        new_readme = await _generate_updated_readme(owner, repo, files, current_readme, commit_info)

        # Don't create PR if README hasn't meaningfully changed
        if current_readme.strip() == new_readme.strip():
            logger.info(f"README unchanged for {owner}/{repo}, skipping PR")
            return

        title = f"docs: update README for commit {commit_info.get('sha', '?')[:7]}"
        body = (
            f"## Automated Documentation Update\n\n"
            f"This PR was automatically generated by the Living Documentation System.\n\n"
            f"**Trigger**: Commit `{commit_info.get('sha', '?')[:7]}` — {commit_info.get('message', 'N/A')}\n"
            f"**Author**: {commit_info.get('author', 'unknown')}\n\n"
            f"### Changes\n"
            f"- Updated project structure documentation\n"
            f"- Refreshed module descriptions based on current codebase\n"
            f"- Auto-generated tech stack and dependency information\n"
        )

        # Create real GitHub PR
        gh_pr = await _create_github_pr(owner, repo, title, body, new_readme, branch)

        # Store in local tracker too
        global _pr_counter
        _pr_counter += 1
        pr_id = f"pr-{_pr_counter}"
        now = datetime.now(timezone.utc).isoformat()

        pr = {
            "id": pr_id,
            "title": title,
            "description": body,
            "doc_content": new_readme,
            "author": "LDS Bot",
            "repo_owner": owner,
            "repo_name": repo,
            "status": "OPEN",
            "reviews": [],
            "created_at": now,
            "updated_at": now,
            "merged_at": None,
            "merged_by": None,
            "commit_sha": commit_info.get("sha"),
            "github_pr": gh_pr,  # None if no token, else {number, html_url, branch, state}
            "auto_generated": True,
        }
        _pr_store[pr_id] = pr
        logger.info(f"Created PR {pr_id} for {owner}/{repo}" +
                     (f" (GitHub PR #{gh_pr['number']})" if gh_pr else " (local only, no GITHUB_TOKEN)"))

    except Exception as e:
        logger.error(f"Auto-update failed for {owner}/{repo}: {e}", exc_info=True)


# ── Webhook Endpoint ────────────────────────────────────────────────────────

@router.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive GitHub push webhooks and trigger auto-doc-update.

    Set up in GitHub repo settings → Webhooks:
      Payload URL: https://<your-host>/api/lds/webhook/github
      Content type: application/json
      Secret: (optional, set LDS_WEBHOOK_SECRET env var)
      Events: Just the push event
    """
    body = await request.body()

    # Verify webhook signature if secret is configured
    secret = os.environ.get("LDS_WEBHOOK_SECRET")
    if secret:
        signature = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    event_type = request.headers.get("X-GitHub-Event", "")
    if event_type == "ping":
        return {"status": "pong"}

    if event_type != "push":
        return {"status": "ignored", "reason": f"Event type '{event_type}' not handled"}

    payload = await request.json()

    # Extract repo info from payload
    repo_data = payload.get("repository", {})
    owner = repo_data.get("owner", {}).get("login", "")
    repo_name = repo_data.get("name", "")
    ref = payload.get("ref", "")

    # Only act on pushes to default branch
    default_branch = repo_data.get("default_branch", "main")
    if ref != f"refs/heads/{default_branch}":
        return {"status": "ignored", "reason": f"Push to non-default branch: {ref}"}

    # Get commit info
    head_commit = payload.get("head_commit", {})
    commit_info = {
        "sha": head_commit.get("id", ""),
        "message": head_commit.get("message", ""),
        "author": head_commit.get("author", {}).get("name", "unknown"),
        "date": head_commit.get("timestamp", ""),
        "branch": default_branch,
    }

    # Skip if this commit was by our bot (avoid infinite loops)
    if "Auto-generated by Living Documentation System" in head_commit.get("message", ""):
        return {"status": "ignored", "reason": "Skipping bot-generated commit"}
    if head_commit.get("message", "").startswith("docs: update README"):
        return {"status": "ignored", "reason": "Skipping docs commit"}

    # Schedule background doc update
    background_tasks.add_task(_auto_update_docs, owner, repo_name, commit_info)

    return {
        "status": "accepted",
        "repo": f"{owner}/{repo_name}",
        "commit": commit_info["sha"][:7],
    }


# ── Manual check for new commits (polling alternative) ──────────────────────

@router.post("/check-updates")
async def check_for_updates(
    owner: str, repo: str, background_tasks: BackgroundTasks, repo_type: str = "github"
):
    """Manually trigger a check for new commits. If there's a new commit since
    the last check, auto-generate a doc update PR.

    This is an alternative to webhooks — the frontend can call this periodically
    or the user can trigger it manually.
    """
    commit_info = await _get_latest_commit(owner, repo)
    if not commit_info:
        return {"status": "error", "message": "Could not fetch latest commit"}

    cache_key = f"{owner}/{repo}"
    last_sha = _repo_last_commit.get(cache_key)

    if last_sha == commit_info["sha"]:
        return {"status": "no_change", "message": "No new commits", "last_commit": commit_info["sha"][:7]}

    _repo_last_commit[cache_key] = commit_info["sha"]

    # If this is the first check, just record the commit without creating a PR
    if last_sha is None:
        return {
            "status": "initialized",
            "message": "Tracking started. Will create PR on next new commit.",
            "current_commit": commit_info["sha"][:7],
        }

    # New commit detected — schedule auto-update
    background_tasks.add_task(_auto_update_docs, owner, repo, commit_info)

    return {
        "status": "update_triggered",
        "message": f"New commit detected ({commit_info['sha'][:7]}). Generating doc update...",
        "previous_commit": last_sha[:7],
        "new_commit": commit_info["sha"][:7],
    }


# ── PR CRUD Endpoints ───────────────────────────────────────────────────────

@router.post("/pull-requests")
async def create_pr(request: PRCreateRequest, background_tasks: BackgroundTasks):
    """Create a new documentation pull request (optionally pushes to GitHub)."""
    global _pr_counter
    try:
        _pr_counter += 1
        pr_id = f"pr-{_pr_counter}"
        now = datetime.now(timezone.utc).isoformat()

        # Try to create a real GitHub PR
        commit_info_data = await _get_latest_commit(request.repo_owner, request.repo_name)
        branch = commit_info_data.get("branch", "main") if commit_info_data else "main"

        gh_pr = await _create_github_pr(
            request.repo_owner, request.repo_name,
            request.title, request.description,
            request.doc_content, branch,
        )

        pr = {
            "id": pr_id,
            "title": request.title,
            "description": request.description,
            "doc_content": request.doc_content,
            "author": request.author,
            "repo_owner": request.repo_owner,
            "repo_name": request.repo_name,
            "status": "OPEN",
            "reviews": [],
            "created_at": now,
            "updated_at": now,
            "merged_at": None,
            "merged_by": None,
            "commit_sha": commit_info_data.get("sha") if commit_info_data else None,
            "github_pr": gh_pr,
            "auto_generated": False,
        }
        _pr_store[pr_id] = pr
        return {"status": "success", "data": pr}
    except Exception as e:
        logger.error(f"Error creating PR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pull-requests")
async def list_prs(repo_owner: Optional[str] = None, repo_name: Optional[str] = None):
    """List all documentation pull requests."""
    prs = list(_pr_store.values())
    if repo_owner:
        prs = [p for p in prs if p["repo_owner"] == repo_owner]
    if repo_name:
        prs = [p for p in prs if p["repo_name"] == repo_name]
    return {"status": "success", "data": prs}


@router.get("/pull-requests/{pr_id}")
async def get_pr(pr_id: str):
    """Get a specific pull request."""
    pr = _pr_store.get(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    return {"status": "success", "data": pr}


@router.post("/pull-requests/{pr_id}/review")
async def review_pr(pr_id: str, request: PRReviewRequest):
    """Add a review to a pull request."""
    pr = _pr_store.get(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    if pr["status"] in ("MERGED", "CLOSED"):
        raise HTTPException(status_code=400, detail="Cannot review a closed or merged PR")

    now = datetime.now(timezone.utc).isoformat()
    review = {
        "reviewer": request.reviewer,
        "status": request.status,
        "comment": request.comment,
        "created_at": now,
    }
    pr["reviews"].append(review)

    if request.status == "APPROVED":
        pr["status"] = "APPROVED"
    elif request.status == "CHANGES_REQUESTED":
        pr["status"] = "REJECTED"
    pr["updated_at"] = now

    return {"status": "success", "data": pr}


@router.post("/pull-requests/{pr_id}/merge")
async def merge_pr(pr_id: str, merged_by: str = "user"):
    """Merge a pull request. If linked to a GitHub PR, merges that too."""
    pr = _pr_store.get(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    if pr["status"] in ("MERGED", "CLOSED"):
        raise HTTPException(status_code=400, detail="PR is already merged or closed")

    # Merge on GitHub if linked
    gh_pr = pr.get("github_pr")
    if gh_pr and gh_pr.get("number"):
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers = _github_headers()
            merge_url = f"https://api.github.com/repos/{pr['repo_owner']}/{pr['repo_name']}/pulls/{gh_pr['number']}/merge"
            async with aiohttp.ClientSession() as session:
                async with session.put(merge_url, headers=headers, json={
                    "merge_method": "squash",
                    "commit_title": f"docs: {pr['title']}",
                }) as resp:
                    if resp.status in (200, 201):
                        gh_pr["state"] = "closed"
                        logger.info(f"Merged GitHub PR #{gh_pr['number']} for {pr['repo_owner']}/{pr['repo_name']}")
                    else:
                        err = await resp.text()
                        logger.warning(f"GitHub merge failed: {resp.status} {err}")

    now = datetime.now(timezone.utc).isoformat()
    pr["status"] = "MERGED"
    pr["merged_at"] = now
    pr["merged_by"] = merged_by
    pr["updated_at"] = now

    # Invalidate repo tree cache so next fetch picks up the merge
    cache_key = f"github:{pr['repo_owner']}/{pr['repo_name']}"
    _repo_tree_cache.pop(cache_key, None)

    return {"status": "success", "data": pr}


@router.post("/pull-requests/{pr_id}/close")
async def close_pr(pr_id: str):
    """Close a pull request. If linked to a GitHub PR, closes that too."""
    pr = _pr_store.get(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    if pr["status"] in ("MERGED", "CLOSED"):
        raise HTTPException(status_code=400, detail="PR is already merged or closed")

    # Close on GitHub if linked
    gh_pr = pr.get("github_pr")
    if gh_pr and gh_pr.get("number"):
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers = _github_headers()
            patch_url = f"https://api.github.com/repos/{pr['repo_owner']}/{pr['repo_name']}/pulls/{gh_pr['number']}"
            async with aiohttp.ClientSession() as session:
                async with session.patch(patch_url, headers=headers, json={"state": "closed"}) as resp:
                    if resp.status == 200:
                        gh_pr["state"] = "closed"

    now = datetime.now(timezone.utc).isoformat()
    pr["status"] = "CLOSED"
    pr["updated_at"] = now

    return {"status": "success", "data": pr}
