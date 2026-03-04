
import pytest
import os
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
    
    # scan_repo uses os.path.join, so on Windows we get backslashes
    expected_py = os.path.join("/repo", "main.py")
    expected_java = os.path.join("/repo", "Service.java")
    unexpected_md = os.path.join("/repo", "readme.md")
    
    assert expected_py in files
    assert expected_java in files
    assert unexpected_md not in files

@patch("os.walk")
def test_scan_repo_ignores_nothing_by_default_logic(mock_walk):
    # The current implementation of scan_repo is very simple.
    mock_walk.return_value = [
        ("/repo", ["src"], []),
        ("/repo/src", [], ["utils.py"])
    ]
    
    files = scan_repo("/repo")
    expected_utils = os.path.join("/repo/src", "utils.py")
    assert expected_utils in files
