import unittest
import os
import tempfile
import shutil
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api_docs_manager.src.parser.express_parser import ExpressParser
from api_docs_manager.src.parser.fastapi_parser import FastAPIParser

class TestParsers(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_express_parser(self):
        content = """
        const express = require('express');
        const router = express.Router();
        router.get('/users', (req, res) => {});
        app.post('/login', (req, res) => {});
        """
        with open(os.path.join(self.test_dir, "routes.js"), "w") as f:
            f.write(content)

        parser = ExpressParser()
        endpoints = parser.parse(self.test_dir)
        
        self.assertEqual(len(endpoints), 2)
        methods = sorted([ep.method for ep in endpoints])
        self.assertEqual(methods, ['GET', 'POST'])
        paths = sorted([ep.path for ep in endpoints])
        self.assertEqual(paths, ['/login', '/users'])

    def test_fastapi_parser(self):
        content = """
from fastapi import FastAPI
app = FastAPI()

@app.get("/items")
def read_items():
    '''List items.'''
    pass

@app.put("/items/{id}")
def update_item(id: int):
    pass
        """
        with open(os.path.join(self.test_dir, "main.py"), "w") as f:
            f.write(content)

        parser = FastAPIParser()
        endpoints = parser.parse(self.test_dir)
        
        self.assertEqual(len(endpoints), 2)
        methods = sorted([ep.method for ep in endpoints])
        self.assertEqual(methods, ['GET', 'PUT'])
        
        # Check description extraction
        get_ep = next(e for e in endpoints if e.method == 'GET')
        self.assertEqual(get_ep.description, "List items.")

if __name__ == "__main__":
    unittest.main()
