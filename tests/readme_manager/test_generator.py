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
    def test_generate_content_gemini(self, mock_model):
        # Test Gemini provider
        mock_response = MagicMock()
        mock_response.text = '{"project_name": "Gemini Project", "overview": "Overview"}'
        mock_model_instance = mock_model.return_value
        mock_model_instance.generate_content.return_value = mock_response
        self.generator.model = mock_model_instance
        
        content = self.generator.generate_content()
        self.assertEqual(content['project_name'], "Gemini Project")

    @patch('readme_manager.generator.requests.post')
    def test_generate_content_ollama(self, mock_post):
        # Test Ollama provider
        ollama_generator = ReadmeGenerator(self.project_root, model_provider="ollama")
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': '{"project_name": "Ollama Project", "overview": "Overview"}'}
        mock_post.return_value = mock_response
        
        content = ollama_generator.generate_content()
        self.assertEqual(content['project_name'], "Ollama Project")
        
        # Verify correct URL and model were used
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/generate")
        self.assertEqual(kwargs['json']['model'], "gemma3:4b")


    def test_analyze_structure(self):
        structure = self.generator.analyze_structure()
        self.assertIsInstance(structure, str)
        # Check if basic files are present (this test file itself might show up if we scan the whole repo, 
        # but let's just check for non-empty string for now as logic depends on file system)
        self.assertTrue(len(structure) > 0)

if __name__ == '__main__':
    unittest.main()
