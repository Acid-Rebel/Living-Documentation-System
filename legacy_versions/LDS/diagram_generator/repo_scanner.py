import os

SUPPORTED_EXTENSIONS = (".py", ".java")

def scan_repo(repo_path):
    files = []
    for root, _, filenames in os.walk(repo_path):
        for name in filenames:
            if name.endswith(SUPPORTED_EXTENSIONS):
                files.append(os.path.join(root, name))
    return files
