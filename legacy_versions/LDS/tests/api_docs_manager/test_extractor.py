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

    def test_extract_flask(self):
        # Mock Flask App
        mock_app = MagicMock()
        mock_rule = MagicMock()
        mock_rule.__str__.return_value = "/flask/api"
        mock_rule.endpoint = "flask_view"
        mock_rule.methods = {'GET', 'POST'}
        
        mock_view_func = MagicMock()
        mock_view_func.__name__ = "flask_view_func"
        mock_view_func.__module__ = "app.views"
        mock_view_func.__doc__ = "Flask docstring"

        mock_app.url_map.iter_rules.return_value = [mock_rule]
        mock_app.view_functions = {"flask_view": mock_view_func}

        endpoints = self.extractor.extract(framework="flask", entry_point=mock_app)
        
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]['path'], "/flask/api")
        self.assertEqual(sorted(endpoints[0]['method']), ['GET', 'POST'])
        self.assertEqual(endpoints[0]['name'], "flask_view")

    def test_extract_fastapi(self):
        # Mock FastAPI App
        mock_app = MagicMock()
        mock_route = MagicMock()
        mock_route.path = "/fastapi/items"
        mock_route.methods = {'GET'}
        mock_route.name = "read_items"
        mock_route.description = "FastAPI docstring"
        mock_route.endpoint.__name__ = "read_items_func"
        mock_route.endpoint.__module__ = "app.main"

        mock_app.routes = [mock_route]

        endpoints = self.extractor.extract(framework="fastapi", entry_point=mock_app)

        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]['path'], "/fastapi/items")
        self.assertEqual(endpoints[0]['method'], ['GET'])

if __name__ == '__main__':
    unittest.main()
