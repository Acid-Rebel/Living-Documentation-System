import unittest
import os
import shutil
import tempfile
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from architecture_docs_manager.src.config.config import Config
from architecture_docs_manager.src.analyzer.structure_analyzer import StructureAnalyzer
from architecture_docs_manager.src.detector.pattern_detector import PatternDetector

class TestArchitectureComponents(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = Config() # Use defaults

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_dummy_structure(self, structure):
        for path in structure:
            full_path = os.path.join(self.test_dir, path)
            os.makedirs(full_path, exist_ok=True)
            # Create a dummy file to ensure dir isn't empty if analyzer checks
            with open(os.path.join(full_path, ".keep"), "w") as f:
                f.write("")

    def test_structure_analyzer_layered(self):
        # Setup standard layered folders
        structure = [
            "src/controllers", # Presentation
            "src/services",    # Business Logic
            "src/repositories" # Data Access
        ]
        self.create_dummy_structure(structure)
        
        analyzer = StructureAnalyzer(self.config)
        result = analyzer.analyze(self.test_dir)
        
        layers = result["layers"]
        self.assertTrue(len(layers["presentation"]) > 0)
        self.assertTrue(len(layers["business_logic"]) > 0)
        self.assertTrue(len(layers["data_access"]) > 0)
        
        # Verify specific component mapping
        pres_comps = [c["name"] for c in layers["presentation"]]
        self.assertIn("controllers", pres_comps)

    def test_pattern_detector_mvc(self):
        # Mock structure result
        structure = {
            "layers": {
                "presentation": [{"name": "controllers", "path": "src/controllers", "type": "LayerComponent"}],
                "business_logic": [{"name": "models", "path": "src/models", "type": "LayerComponent"}],
                "data_access": [],
                "infrastructure": []
            }
        }
        
        detector = PatternDetector()
        patterns = detector.detect(structure)
        
        pattern_names = [p["name"] for p in patterns]
        self.assertTrue(any("MVC" in p for p in pattern_names))

    def test_pattern_detector_layered(self):
         # Mock layered structure
        structure = {
            "layers": {
                "presentation": [{"name": "api", "path": "src/api", "type": "LayerComponent"}],
                "business_logic": [{"name": "domain", "path": "src/domain", "type": "LayerComponent"}],
                "data_access": [{"name": "db", "path": "src/db", "type": "LayerComponent"}],
                "infrastructure": []
            }
        }
        
        detector = PatternDetector()
        patterns = detector.detect(structure)
        
        pattern_names = [p["name"] for p in patterns]
        self.assertTrue(any("Layered Architecture" in p for p in pattern_names))

if __name__ == "__main__":
    unittest.main()
