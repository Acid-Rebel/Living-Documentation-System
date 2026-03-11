import unittest
import pytest
try:
    from api_docs_manager.generator import APIDocGenerator
except ImportError:
    pytest.skip("api_docs_manager.generator requires markdown which is not installed", allow_module_level=True)

class TestAPIDocGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = APIDocGenerator()

    def test_generate_simple_markdown(self):
        endpoints = [
            {'path': '/api/test', 'method': ['GET'], 'name': 'test_view', 'description': 'Test description'}
        ]
        md = self.generator.generate_markdown(endpoints)
        
        self.assertIn("# API Documentation", md)
        self.assertIn("### GET /api/test", md)
        self.assertIn("**Name:** `test_view`", md)
        self.assertIn("Test description", md)

    def test_generate_with_diff(self):
        endpoints = [
            {'path': '/api/new', 'method': ['POST'], 'name': 'new_view', 'description': 'New view'}
        ]
        diff = {
            'added': [{'path': '/api/new', 'method': ['POST']}],
            'removed': [{'path': '/api/old', 'method': ['GET']}],
            'deprecated': [],
            'unchanged': []
        }
        
        md = self.generator.generate_markdown(endpoints, diff=diff)
        
        self.assertIn("## Recent Changes", md)
        self.assertIn("### 🆕 Added Endpoints", md)
        self.assertIn("- `/api/new` (POST)", md)
        self.assertIn("### ❌ Removed Endpoints", md)
        self.assertIn("- `/api/old` (GET)", md)

if __name__ == '__main__':
    unittest.main()
