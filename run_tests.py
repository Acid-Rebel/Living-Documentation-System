import sys
import os
import unittest

# Add root to path
sys.path.insert(0, os.getcwd())

# Import the test
from tests.readme_manager.test_generator import TestReadmeGenerator

# Run tests
suite = unittest.TestLoader().loadTestsFromTestCase(TestReadmeGenerator)
unittest.TextTestRunner(verbosity=2).run(suite)
