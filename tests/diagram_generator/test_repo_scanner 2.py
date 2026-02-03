
import pytest
from unittest.mock import patch, MagicMock
from diagram_generator.repo_scanner import scan_repo

@patch("os.walk")
def test_scan_repo_finds_python_java(mock_walk):
    # Setup mock filesystem
    # root, dirs, files
    mock_walk.return_value = [
        ("/repo", [], ["main.py", "Service.java", "readme.md", "image.png"])
    ]
    
    files = scan_repo("/repo")
    
    assert "/repo/main.py" in files
    assert "/repo/Service.java" in files
    assert "/repo/readme.md" not in files
    assert "/repo/image.png" not in files

@patch("os.walk")
def test_scan_repo_ignores_nothing_by_default_logic(mock_walk):
    # The current implementation of scan_repo is very simple (see previously viewed file).
    # It just checks extensions. It relies on os.walk.
    # If logic changes to ignore .git, we test it here.
    # For now, just confirming it finds files recursively.
    mock_walk.return_value = [
        ("/repo", ["src"], []),
        ("/repo/src", [], ["utils.py"])
    ]
    
    files = scan_repo("/repo")
    assert "/repo/src/utils.py" in files
