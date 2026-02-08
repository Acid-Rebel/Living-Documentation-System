import os
import unittest
from unittest.mock import MagicMock, patch
from readme_manager.generator import ReadmeGenerator

class TestReadmeGenerator(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.api_key = "test_api_key"
        self.generator = ReadmeGenerator(self.project_root, self.api_key)

    @patch('readme_manager.generator.genai.GenerativeModel')
    def test_generate_content(self, mock_model):
        # Mock the response from Gemini
        mock_response = MagicMock()
        mock_response.text = '{"project_name": "Test Project", "overview": "A test project", "features": [], "architecture_summary": "Test arch", "usage_instructions": "Run it", "api_endpoints": [], "language": "Python"}'
        
        mock_model_instance = mock_model.return_value
        mock_model_instance.generate_content.return_value = mock_response
        
        # Inject the mock model into the generator
        self.generator.model = mock_model_instance
        
        content = self.generator.generate_content()
        self.assertEqual(content['project_name'], "Test Project")
        self.assertEqual(content['overview'], "A test project")


    def test_analyze_structure(self):
        structure = self.generator.analyze_structure()
        self.assertIsInstance(structure, str)
        # Check if basic files are present (this test file itself might show up if we scan the whole repo, 
        # but let's just check for non-empty string for now as logic depends on file system)
        self.assertTrue(len(structure) > 0)

if __name__ == '__main__':
    unittest.main()
