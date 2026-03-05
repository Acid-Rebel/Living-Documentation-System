import os
import pytest
from unittest.mock import patch, MagicMock
from core.data_pipeline import count_tokens, download_repo, read_all_documents

def test_count_tokens_openai():
    text = "Hello, world!"
    count = count_tokens(text, embedder_type="openai")
    assert count > 0

def test_count_tokens_fallback():
    text = "This is a longer sentence to test fallback logic."
    with patch("tiktoken.get_encoding", side_effect=Exception("Mock error")):
        with patch("tiktoken.encoding_for_model", side_effect=Exception("Mock error")):
            count = count_tokens(text, embedder_type="unknown")
            # Fallback is len(text) // 4 = 49 // 4 = 12
            assert count == len(text) // 4

@patch("subprocess.run")
def test_download_repo_success(mock_run, tmp_path):
    mock_run.return_value = MagicMock(stdout=b"Cloning into...", check=True)
    local_path = str(tmp_path / "repo")
    result = download_repo("https://github.com/user/repo", local_path)
    assert "Cloning into" in result or "Using existing repository" in result

@patch("subprocess.run")
def test_download_repo_git_missing(mock_run):
    mock_run.side_effect = Exception("git not found")
    with pytest.raises(ValueError, match="An unexpected error occurred"):
        download_repo("https://github.com/user/repo", "/tmp/path")

def test_read_all_documents_basic(tmp_path):
    # Create some dummy files in a non-excluded directory
    docs_dir = tmp_path / "test_data_dir"
    docs_dir.mkdir()
    (docs_dir / "test.py").write_text("print('hello')")
    (docs_dir / "readme.md").write_text("# Project")
    
    with patch("core.data_pipeline.configs", {"file_filters": {"excluded_dirs": [], "excluded_files": []}}):
        documents = read_all_documents(str(docs_dir), embedder_type="openai")
        
        # Should find 1 py and 1 md
        exts = [doc.meta_data["type"] for doc in documents]
        assert "py" in exts
        assert "md" in exts
        assert len(documents) == 2

def test_read_all_documents_exclusion(tmp_path):
    docs_dir = tmp_path / "test_data_excl_dir"
    docs_dir.mkdir()
    (docs_dir / "test.py").write_text("print('hello')")
    (docs_dir / "exclude.py").write_text("secret")
    
    with patch("core.data_pipeline.configs", {"file_filters": {"excluded_dirs": [], "excluded_files": []}}):
        documents = read_all_documents(
            str(docs_dir), 
            embedder_type="openai", 
            excluded_files=["exclude.py"]
        )
        assert len(documents) == 1
        assert documents[0].meta_data["file_path"] == "test.py"
