import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os

from diagram_generator.generate_repo_diagrams import (
    generate_repo_diagrams,
    clone_repo,
    latest_commit,
    repo_name_from_url
)


class TestRepoNameFromUrl:
    """Test extracting repository name from URL."""
    
    def test_https_url(self):
        """Test HTTPS GitHub URL."""
        result = repo_name_from_url('https://github.com/user/repo.git')
        assert result == 'repo'
    
    def test_ssh_url(self):
        """Test SSH GitHub URL."""
        result = repo_name_from_url('git@github.com:user/repo.git')
        assert result == 'repo'
    
    def test_url_without_git_extension(self):
        """Test URL without .git extension."""
        result = repo_name_from_url('https://github.com/user/myproject')
        assert result == 'myproject'


class TestLatestCommit:
    """Test getting latest commit hash from remote."""
    
    @patch('subprocess.check_output')
    def test_latest_commit_success(self, mock_subprocess):
        """Test successful commit hash retrieval."""
        mock_subprocess.return_value = "4eb21be8aa93dcc84a988543bcdb27639c84ffe9\tHEAD\n"
        
        result = latest_commit('https://github.com/test/repo.git')
        
        # Should return 7-char short hash
        assert result == '4eb21be'
    
    @patch('subprocess.check_output')
    def test_latest_commit_failure(self, mock_subprocess):
        """Test handling of failure."""
        mock_subprocess.side_effect = Exception("Network error")
        
        result = latest_commit('https://github.com/test/repo.git')
        
        assert result == 'unknown'


class TestCloneRepo:
    """Test repository cloning functionality."""
    
    @patch('subprocess.run')
    def test_clone_repo_success(self, mock_run):
        """Test successful repository clone."""
        mock_run.return_value = MagicMock(returncode=0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, 'test-repo')
            clone_repo('https://github.com/test/repo.git', dest)
            
            mock_run.assert_called_once_with(
                ["git", "clone", "--depth", "1", 'https://github.com/test/repo.git', dest],
                check=True
            )


class TestGenerateRepoDiagrams:
    """Test the main diagram generation orchestration."""
    
    @patch('diagram_generator.generate_repo_diagrams.clone_repo')
    @patch('diagram_generator.generate_repo_diagrams.latest_commit')
    @patch('diagram_generator.generate_repo_diagrams.scan_repo')
    @patch('diagram_generator.generate_repo_diagrams.render_dot_to_png')
    @patch('os.makedirs')
    def test_generate_creates_all_diagram_types(
        self, mock_makedirs, mock_render_png, mock_scan, mock_commit, mock_clone
    ):
        """Test that all diagram types are generated."""
        mock_commit.return_value = 'abc1234'
        mock_scan.return_value = []
        
        result = generate_repo_diagrams('https://github.com/test/repo.git')
        
        # Should have called render_dot_to_png at least twice
        assert mock_render_png.call_count >= 2
        
        # Result should be output directory path
        assert 'output' in result
        assert 'repo' in result
        assert 'abc1234' in result
    
    @patch('diagram_generator.generate_repo_diagrams.clone_repo')
    @patch('diagram_generator.generate_repo_diagrams.latest_commit')
    @patch('tempfile.TemporaryDirectory')
    def test_generate_uses_unique_temp_directory(self, mock_tempdir, mock_commit, mock_clone):
        """Test that each generation uses a unique temporary directory."""
        mock_commit.return_value = 'xyz7890'
        
        # Mock TemporaryDirectory context manager
        mock_temp_ctx = MagicMock()
        mock_temp_ctx.__enter__.return_value = '/tmp/unique_temp_dir'
        mock_temp_ctx.__exit__.return_value = None
        mock_tempdir.return_value = mock_temp_ctx
        
        with patch('diagram_generator.generate_repo_diagrams.scan_repo', return_value=[]):
            generate_repo_diagrams('https://github.com/test/repo.git')
        
        # Should have created temp directory with prefix
        mock_tempdir.assert_called_once()
        call_kwargs = mock_tempdir.call_args[1]
        assert 'prefix' in call_kwargs
        assert 'tmp_repo_' in call_kwargs['prefix']
