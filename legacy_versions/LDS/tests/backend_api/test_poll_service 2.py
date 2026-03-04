import pytest
from unittest.mock import patch, MagicMock, call
from django.test import TestCase
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from api.models import Project
from api.poll_service import get_latest_remote_commit, polling_worker


@pytest.mark.django_db
class TestGetLatestRemoteCommit(TestCase):
    """Test the git ls-remote functionality."""
    
    @patch('subprocess.check_output')
    def test_get_latest_remote_commit_success(self, mock_subprocess):
        """Test successful remote commit retrieval."""
        mock_subprocess.return_value = "4eb21be8aa93dcc84a988543bcdb27639c84ffe9\tHEAD\n"
        
        result = get_latest_remote_commit('https://github.com/test/repo.git')
        
        # Should return 7-char short hash
        self.assertEqual(result, '4eb21be')
        mock_subprocess.assert_called_once_with(
            ["git", "ls-remote", 'https://github.com/test/repo.git', "HEAD"],
            text=True,
            timeout=15
        )
    
    @patch('subprocess.check_output')
    def test_get_latest_remote_commit_failure(self, mock_subprocess):
        """Test handling of git ls-remote failure."""
        mock_subprocess.side_effect = Exception("Network error")
        
        result = get_latest_remote_commit('https://github.com/test/repo.git')
        
        self.assertIsNone(result)


@pytest.mark.django_db
class TestPollingWorker(TestCase):
    """Test the background polling worker logic."""
    
    def setUp(self):
        # Create test projects
        self.http_project = Project.objects.create(
            name='HTTP Project',
            repo_url='https://github.com/test/repo.git',
            last_commit_hash='old1234'
        )
        
        self.file_project = Project.objects.create(
            name='File Project',
            repo_url='file:///tmp/local-repo',
            last_commit_hash=''
        )
    
    @patch('api.poll_service.get_latest_remote_commit')
    @patch('api.poll_service.process_and_save_diagram')
    @patch('api.poll_service.time.sleep')
    def test_polling_detects_new_commit(self, mock_sleep, mock_process, mock_get_commit):
        """Test that polling detects and processes new commits."""
        # Mock to return a new hash
        mock_get_commit.return_value = 'new5678'
        
        # Mock process_and_save_diagram
        mock_version = MagicMock()
        mock_process.return_value = mock_version
        
        # Make sleep raise exception to break the infinite loop after first iteration
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]
        
        try:
            polling_worker()
        except KeyboardInterrupt:
            pass
        
        # Should have called process_and_save_diagram for the HTTP project
        mock_process.assert_called()
        call_args = mock_process.call_args[0]
        self.assertEqual(call_args[0].name, 'HTTP Project')
        self.assertEqual(call_args[1], 'new5678')
    
    @patch('api.poll_service.get_latest_remote_commit')
    @patch('api.poll_service.process_and_save_diagram')
    @patch('api.poll_service.time.sleep')
    def test_polling_skips_unchanged_commit(self, mock_sleep, mock_process, mock_get_commit):
        """Test that polling skips when commit hasn't changed."""
        # Return the same hash as stored
        mock_get_commit.return_value = 'old1234'
        
        # Make sleep raise exception to break loop
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]
        
        try:
            polling_worker()
        except KeyboardInterrupt:
            pass
        
        # Should NOT have called process_and_save_diagram
        mock_process.assert_not_called()
    
    @patch('api.poll_service.get_latest_remote_commit')
    @patch('api.poll_service.time.sleep')
    def test_polling_skips_file_urls(self, mock_sleep, mock_get_commit):
        """Test that polling skips file:// URLs."""
        # Make sleep raise exception to break loop
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]
        
        try:
            polling_worker()
        except KeyboardInterrupt:
            pass
        
        # Should only check HTTP project, not file project
        self.assertEqual(mock_get_commit.call_count, 1)
        call_args = mock_get_commit.call_args[0]
        self.assertIn('github.com', call_args[0])
