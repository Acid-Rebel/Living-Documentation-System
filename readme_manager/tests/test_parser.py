import unittest
import os
import shutil
import tempfile
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from readme_manager.src.parser.nodejs import NodeParser
from readme_manager.src.parser.python import PythonParser

class TestParsers(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_nodejs_parser_detect(self):
        parser = NodeParser(self.test_dir)
        self.assertFalse(parser.detect())
        
        with open(os.path.join(self.test_dir, "package.json"), "w") as f:
            f.write("{}")
        self.assertTrue(parser.detect())

    def test_nodejs_parser_parse(self):
        content = """{
            "name": "test-pkg",
            "version": "1.0.0",
            "dependencies": {"react": "^17.0.0"},
            "devDependencies": {"typescript": "^4.0.0"}
        }"""
        with open(os.path.join(self.test_dir, "package.json"), "w") as f:
            f.write(content)
            
        parser = NodeParser(self.test_dir)
        data = parser.parse()
        
        self.assertEqual(data["name"], "test-pkg")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("React", data["frameworks"])
        self.assertEqual(data["language"], "TypeScript")

    def test_python_parser_detect(self):
        parser = PythonParser(self.test_dir)
        self.assertFalse(parser.detect())
        
        with open(os.path.join(self.test_dir, "requirements.txt"), "w") as f:
            f.write("django==3.2")
        self.assertTrue(parser.detect())

    def test_python_parser_parse(self):
        content = "flask==2.0.1\npandas>=1.0"
        with open(os.path.join(self.test_dir, "requirements.txt"), "w") as f:
            f.write(content)
            
        parser = PythonParser(self.test_dir)
        data = parser.parse()
        
        self.assertEqual(data["language"], "Python")
        self.assertIn("flask", data["dependencies"])
        self.assertIn("Flask", data["frameworks"])
        self.assertIn("Pandas", data["frameworks"])

if __name__ == "__main__":
    unittest.main()
