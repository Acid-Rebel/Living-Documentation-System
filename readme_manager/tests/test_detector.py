import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from readme_manager.src.detector.classifier import Classifier

class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = Classifier()

    def test_classify_web_app(self):
        metadata = {
            "dependencies": ["express", "react"],
            "scripts": {"start": "node index.js"}
        }
        self.assertEqual(self.classifier.classify(metadata), "web-app")

    def test_classify_cli(self):
        metadata = {
            "dependencies": ["commander"],
            "scripts": {"build": "tsc"},
            "bin": "./dist/cli.js"
        }
        self.assertEqual(self.classifier.classify(metadata), "cli")

    def test_classify_library(self):
        metadata = {
            "dependencies": ["lodash"],
            "scripts": {"test": "jest"},
            "name": "my-utils"
        }
        self.assertEqual(self.classifier.classify(metadata), "library")

if __name__ == "__main__":
    unittest.main()
