import unittest
from unittest.mock import MagicMock, patch
from api_docs_manager.extractor import EndpointExtractor

class TestDjangoExtraction(unittest.TestCase):
    def setUp(self):
        self.extractor = EndpointExtractor(".")

    def test_parse_simple_pattern(self):
        # Mock a simple Django URL pattern
        mock_pattern = MagicMock()
        mock_pattern.pattern = "api/test/"
        mock_pattern.callback.__name__ = "test_view"
        mock_pattern.callback.__doc__ = "Test view docstring"
        mock_pattern.name = "test-view"
        # Ensure it doesn't look like a resolver (include)
        del mock_pattern.url_patterns 

        # Mock the importlib.import_module call
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value.urlpatterns = [mock_pattern]
            
            endpoints = self.extractor.extract(framework="django", entry_point="dummy.urls")
            
            self.assertEqual(len(endpoints), 1)
            self.assertEqual(endpoints[0]['path'], "api/test/")
            self.assertEqual(endpoints[0]['name'], "test-view")
            self.assertEqual(endpoints[0]['description'], "Test view docstring")

    def test_parse_nested_patterns(self):
        # Mock nested patterns (include)
        mock_view = MagicMock()
        mock_view.pattern = "users/"
        mock_view.callback.__name__ = "list_users"
        del mock_view.url_patterns

        mock_resolver = MagicMock()
        mock_resolver.pattern = "api/v1/"
        mock_resolver.url_patterns = [mock_view]
        # Ensure it DOES look like a resolver
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value.urlpatterns = [mock_resolver]
            
            endpoints = self.extractor.extract(framework="django", entry_point="dummy.urls")
            
            self.assertEqual(len(endpoints), 1)
            self.assertEqual(endpoints[0]['path'], "api/v1/users/")

if __name__ == '__main__':
    unittest.main()
