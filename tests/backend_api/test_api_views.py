import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from api.models import Project, DiagramVersion
from api.views import process_and_save_diagram


@pytest.mark.django_db
class TestProjectViewSet(TestCase):
    """Test the ProjectViewSet CRUD operations."""
    
    def setUp(self):
        self.client = APIClient()
        self.project_data = {
            'name': 'Test Project',
            'repo_url': 'https://github.com/test/repo.git'
        }
    
    def test_create_project(self):
        """Test creating a new project."""
        response = self.client.post('/api/projects/', self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'Test Project')
    
    def test_list_projects(self):
        """Test listing all projects."""
        Project.objects.create(**self.project_data)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_delete_project(self):
        """Test deleting a project."""
        project = Project.objects.create(**self.project_data)
        response = self.client.delete(f'/api/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)
    
    @patch('api.views.process_and_save_diagram')
    def test_refresh_action(self, mock_process):
        """Test the refresh action triggers diagram generation."""
        project = Project.objects.create(**self.project_data)
        mock_version = MagicMock()
        mock_process.return_value = mock_version
        
        response = self.client.post(f'/api/projects/{project.id}/refresh/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_process.assert_called_once()


@pytest.mark.django_db
class TestWebhookView(TestCase):
    """Test the webhook endpoint for commit notifications."""
    
    def setUp(self):
        self.client = APIClient()
        self.project = Project.objects.create(
            name='Webhook Test',
            repo_url='https://github.com/test/webhook.git'
        )
    
    @patch('api.views.process_and_save_diagram')
    def test_webhook_with_project_id(self, mock_process):
        """Test webhook with project_id in payload."""
        mock_version = MagicMock()
        mock_process.return_value = mock_version
        
        payload = {
            'project_id': str(self.project.id),
            'commit_sha': 'abc1234',
            'message': 'Test commit',
            'author': 'Test Author'
        }
        
        response = self.client.post('/api/webhook/commit/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_process.assert_called_once_with(
            self.project, 'abc1234', 'Test commit', 'Test Author'
        )
    
    @patch('api.views.process_and_save_diagram')
    def test_webhook_with_repo_url(self, mock_process):
        """Test webhook with repository_url in payload."""
        mock_version = MagicMock()
        mock_process.return_value = mock_version
        
        payload = {
            'repository_url': self.project.repo_url,
            'commit_sha': 'def5678',
            'message': 'Another commit',
            'author': 'Another Author'
        }
        
        response = self.client.post('/api/webhook/commit/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_process.assert_called_once()
    
    def test_webhook_project_not_found(self):
        """Test webhook with invalid project returns 400."""
        payload = {
            'project_id': '00000000-0000-0000-0000-000000000000',
            'commit_sha': 'xyz9999'
        }
        
        response = self.client.post('/api/webhook/commit/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class TestProcessAndSaveDiagram(TestCase):
    """Test the core diagram processing function."""
    
    def setUp(self):
        self.project = Project.objects.create(
            name='Process Test',
            repo_url='file:///tmp/test-repo'
        )
    
    @patch('api.views.generate_repo_diagrams')
    @patch('api.views.os.path.exists')
    @patch('api.views.os.listdir')
    @patch('builtins.open', create=True)
    def test_process_updates_last_commit_hash(self, mock_open, mock_listdir, mock_exists, mock_generate):
        """Test that process_and_save_diagram updates project.last_commit_hash."""
        # Mock the generation output
        mock_generate.return_value = '/tmp/output/test-repo/abc1234'
        mock_exists.return_value = True
        mock_listdir.return_value = ['class_diagram_global.png']
        mock_open.return_value.__enter__.return_value.read.return_value = b'fake image data'
        
        version = process_and_save_diagram(
            self.project, 'initial', 'Test commit', 'Test Author'
        )
        
        # Refresh from DB
        self.project.refresh_from_db()
        
        # Should have extracted short hash from path
        self.assertEqual(self.project.last_commit_hash, 'abc1234')
        self.assertEqual(version.commit_hash, 'abc1234')
