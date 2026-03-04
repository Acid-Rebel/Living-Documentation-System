from fastapi import APIRouter, HTTPException
import logging
import os
import sys
from typing import Dict, Any, List, Optional
import aiohttp

# Ensure living_docs_engine is in the path
engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'living_docs_engine'))
if engine_path not in sys.path:
    sys.path.insert(0, engine_path)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lds", tags=["Living Docs Engine"])

# ── Helpers ──────────────────────────────────────────────────────────────────

async def _fetch_repo_tree(owner: str, repo: str, repo_type: str) -> List[str]:
    """Fetch repository file paths from the hosting API."""
    headers: Dict[str, str] = {"Accept": "application/json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    if repo_type == "github":
        async with aiohttp.ClientSession() as session:
            for branch in ("main", "master"):
                api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
                async with session.get(api_url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [item["path"] for item in data.get("tree", []) if item.get("type") == "blob"]
    return []


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
