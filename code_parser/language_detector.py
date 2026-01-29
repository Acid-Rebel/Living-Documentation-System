EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
}

def detect_language(file_path: str) -> str | None:
    for ext, lang in EXTENSION_LANGUAGE_MAP.items():
        if file_path.endswith(ext):
            return lang
    return None