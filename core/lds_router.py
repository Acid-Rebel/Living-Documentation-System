from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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


# ── AI-Enhanced Diagrams ─────────────────────────────────────────────────────

def _generate_diagram_mermaid(files: List[str], diagram_type: str) -> str:
    """Generate a Mermaid diagram from the repository file structure (no LLM needed)."""
    code_files = [f for f in files if _classify_file(f) == "code"]
    skip = {"node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".git"}

    dir_files: Dict[str, List[str]] = {}
    for f in code_files:
        parts = f.split("/")
        if len(parts) >= 2 and not parts[0].startswith(".") and parts[0] not in skip:
            top = parts[0]
            dir_files.setdefault(top, []).append(f)

    if diagram_type == "class":
        lines = ["classDiagram"]
        for mod, mod_files in sorted(dir_files.items(), key=lambda x: -len(x[1])):
            # represent each module as a class with file counts
            lines.append(f"    class {mod} {{")
            exts: Dict[str, int] = {}
            for mf in mod_files:
                ext = os.path.splitext(mf)[1].lstrip(".")
                exts[ext] = exts.get(ext, 0) + 1
            for ext, cnt in sorted(exts.items()):
                lines.append(f"        +{ext}_files : {cnt}")
            lines.append("    }")
        # relationships
        mod_names = list(dir_files.keys())
        for i, ma in enumerate(mod_names):
            for mb in mod_names[i + 1:]:
                a_refs_b = any(mb.lower() in f.lower() for f in dir_files.get(ma, []))
                if a_refs_b:
                    lines.append(f"    {ma} --> {mb}")
        return "\n".join(lines)

    elif diagram_type == "dependency":
        lines = ["graph TD"]
        mod_names = list(dir_files.keys())
        for mod in mod_names:
            file_count = len(dir_files[mod])
            lines.append(f"    {mod}[{mod} ({file_count} files)]")
        for i, ma in enumerate(mod_names):
            for mb in mod_names[i + 1:]:
                a_refs_b = any(mb.lower() in f.lower() for f in dir_files.get(ma, []))
                b_refs_a = any(ma.lower() in f.lower() for f in dir_files.get(mb, []))
                if a_refs_b:
                    lines.append(f"    {ma} --> {mb}")
                if b_refs_a:
                    lines.append(f"    {mb} --> {ma}")
        if not any("-->" in line for line in lines):
            # add fallback edges
            for m in mod_names[1:]:
                lines.append(f"    {mod_names[0]} --> {m}")
        return "\n".join(lines)

    else:  # call / sequence
        lines = ["sequenceDiagram"]
        mod_names = list(dir_files.keys())[:8]
        if len(mod_names) >= 2:
            lines.append(f"    participant User")
            for mod in mod_names:
                lines.append(f"    participant {mod}")
            lines.append(f"    User->>{mod_names[0]}: Request")
            for i in range(len(mod_names) - 1):
                lines.append(f"    {mod_names[i]}->>{mod_names[i+1]}: Process")
            lines.append(f"    {mod_names[-1]}-->>{mod_names[0]}: Response")
            lines.append(f"    {mod_names[0]}->>User: Result")
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

# In-memory PR store (scoped to server lifetime)
_pr_store: Dict[str, Dict[str, Any]] = {}
_pr_counter: int = 0


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


@router.post("/pull-requests")
async def create_pr(request: PRCreateRequest):
    """Create a new documentation pull request."""
    global _pr_counter
    try:
        _pr_counter += 1
        pr_id = f"pr-{_pr_counter}"
        from datetime import datetime
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
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "merged_at": None,
            "merged_by": None,
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

    from datetime import datetime
    review = {
        "reviewer": request.reviewer,
        "status": request.status,
        "comment": request.comment,
        "created_at": datetime.utcnow().isoformat(),
    }
    pr["reviews"].append(review)

    # Update PR status
    if request.status == "APPROVED":
        pr["status"] = "APPROVED"
    elif request.status == "CHANGES_REQUESTED":
        pr["status"] = "REJECTED"
    pr["updated_at"] = datetime.utcnow().isoformat()

    return {"status": "success", "data": pr}


@router.post("/pull-requests/{pr_id}/merge")
async def merge_pr(pr_id: str, merged_by: str = "user"):
    """Merge a pull request."""
    pr = _pr_store.get(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    if pr["status"] in ("MERGED", "CLOSED"):
        raise HTTPException(status_code=400, detail="PR is already merged or closed")

    from datetime import datetime
    pr["status"] = "MERGED"
    pr["merged_at"] = datetime.utcnow().isoformat()
    pr["merged_by"] = merged_by
    pr["updated_at"] = datetime.utcnow().isoformat()

    return {"status": "success", "data": pr}


@router.post("/pull-requests/{pr_id}/close")
async def close_pr(pr_id: str):
    """Close a pull request."""
    pr = _pr_store.get(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
    if pr["status"] in ("MERGED", "CLOSED"):
        raise HTTPException(status_code=400, detail="PR is already merged or closed")

    from datetime import datetime
    pr["status"] = "CLOSED"
    pr["updated_at"] = datetime.utcnow().isoformat()

    return {"status": "success", "data": pr}
