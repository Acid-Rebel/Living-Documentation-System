import importlib
import inspect
from typing import List, Dict, Any, Optional

class EndpointExtractor:
    """
    Extracts API endpoints from various frameworks (Django, Flask, FastAPI).
    """
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.endpoints = []

    def extract(self, framework: str = "django", entry_point: Any = "backend.urls") -> List[Dict[str, Any]]:
        """
        Main method to extract endpoints.
        :param framework: 'django', 'flask', 'fastapi'
        :param entry_point: Python path (Django) or App instance (Flask/FastAPI)
        """
        if framework.lower() == 'django':
            return self._extract_django(entry_point)
        elif framework.lower() == 'flask':
            return self._extract_flask(entry_point)
        elif framework.lower() == 'fastapi':
            return self._extract_fastapi(entry_point)
        else:
            raise NotImplementedError(f"Framework '{framework}' not supported yet.")

    def _extract_django(self, urlconf_path: str) -> List[Dict[str, Any]]:
        # ... (implementation remains same, skipping for brevity in this replacement block if I could, but I need to replace the extract method too)
        try:
            urlconf = importlib.import_module(urlconf_path)
            patterns = getattr(urlconf, 'urlpatterns', [])
            return self._parse_django_patterns(patterns)
        except (ImportError, AttributeError) as e:
            print(f"Error importing URLconf {urlconf_path}: {e}")
            return []

    def _extract_flask(self, app) -> List[Dict[str, Any]]:
        """
        Extracts endpoints from a Flask app instance.
        """
        endpoints = []
        for rule in app.url_map.iter_rules():
            view_func = app.view_functions[rule.endpoint]
            methods = list(rule.methods - {'HEAD', 'OPTIONS'}) if rule.methods else ['GET']
            
            endpoints.append({
                'path': str(rule),
                'method': methods,
                'name': rule.endpoint,
                'description': inspect.getdoc(view_func) or "",
                'source': f"{view_func.__module__}.{view_func.__name__}"
            })
        return endpoints

    def _extract_fastapi(self, app) -> List[Dict[str, Any]]:
        """
        Extracts endpoints from a FastAPI app instance.
        """
        endpoints = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                endpoints.append({
                    'path': route.path,
                    'method': list(route.methods),
                    'name': route.name,
                    'description': route.description or "",
                    'source': f"{route.endpoint.__module__}.{route.endpoint.__name__}" if hasattr(route, 'endpoint') else "unknown"
                })
        return endpoints

    def _parse_django_patterns(self, patterns, prefix: str = "") -> List[Dict[str, Any]]:
        endpoints = []
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):  # It's an include() / URLResolver
                # Django 2.0+ uses 'pattern.pattern', older uses 'pattern.regex.pattern'
                route = str(pattern.pattern) if hasattr(pattern, 'pattern') else str(pattern.regex.pattern)
                new_prefix = prefix + route
                endpoints.extend(self._parse_django_patterns(pattern.url_patterns, new_prefix))
            elif hasattr(pattern, 'callback'):  # It's a view / URLPattern
                route = str(pattern.pattern) if hasattr(pattern, 'pattern') else str(pattern.regex.pattern)
                full_path = prefix + route
                
                view_func = pattern.callback
                docstring = inspect.getdoc(view_func) or ""
                view_name = pattern.name or view_func.__name__
                
                # Basic method detection (heuristic)
                methods = ['GET'] # Default
                if hasattr(view_func, 'cls'): # Class-based view
                    methods = [m.upper() for m in ['get', 'post', 'put', 'delete', 'patch'] if hasattr(view_func.cls, m)]
                
                endpoints.append({
                    'path': full_path,
                    'method': methods,
                    'name': view_name,
                    'description': docstring,
                    'source': f"{view_func.__module__}.{view_func.__name__}"
                })
        return endpoints
