import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import zlib
import base64
import urllib.request
import unittest
from dotenv import load_dotenv

# Load env before any local imports to ensure keys are ready
load_dotenv()

# We map the Google API Key to OpenAI format to use Gemini's OpenAI-compatible endpoint
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    os.environ["OPENAI_API_KEY"] = google_key
    os.environ["OPENAI_BASE_URL"] = "https://generativelanguage.googleapis.com/v1beta/openai/"

from living_docs_engine.diagram_generator import DiagramGenerator

def render_mermaid_to_image(mermaid_code: str, output_file: str):
    """Uses kroki.io to render Mermaid code to an SVG file."""
    # Ensure no backticks are surrounding the diagram
    clean_code = mermaid_code.strip()
    if clean_code.startswith("```mermaid"):
        clean_code = clean_code[10:]
    if clean_code.startswith("```"):
        clean_code = clean_code[3:]
    if clean_code.endswith("```"):
        clean_code = clean_code[:-3]
    clean_code = clean_code.strip()

    compressed = zlib.compress(clean_code.encode('utf-8'))
    payload = base64.urlsafe_b64encode(compressed).decode('ascii')
    
    # Kroki URL for mermaid SVG
    url = f"https://kroki.io/mermaid/svg/{payload}"
    
    try:
        print(f"Fetching diagram image from: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(output_file, 'wb') as f:
                f.write(response.read())
        print(f"Successfully saved diagram to {output_file}")
    except Exception as e:
        print(f"Failed to render diagram for {output_file}: {e}")

class TestDiagramGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Determine paths
        cls.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # We will point the diagram generator to a small sub-module to avoid massive context counts.
        # Let's test it on the diagram_generator module itself!
        cls.target_dir = os.path.join(cls.root_dir, "living_docs_engine", "diagram_generator")
        
        cls.output_dir = os.path.join(cls.root_dir, "diagram_outputs")
        os.makedirs(cls.output_dir, exist_ok=True)
        
        # We use gemini-2.5-flash or gemini-1.5-flash as the model on the OpenAI-compatible endpoint
        cls.generator = DiagramGenerator(model="gemini-2.5-flash")
        
    def test_class_diagram_generation(self):
        print("\nGenerating Class Diagram...")
        result = self.generator.generate_class_diagram(self.target_dir)
        self.assertIn("classDiagram", result)
        
        output_path = os.path.join(self.output_dir, "class_diagram.svg")
        render_mermaid_to_image(result, output_path)
        self.assertTrue(os.path.exists(output_path), "Class diagram SVG was not created.")
        
    def test_dependency_diagram_generation(self):
        print("\nGenerating Dependency Diagram...")
        result = self.generator.generate_dependency_diagram(self.target_dir)
        self.assertIn("graph", result)
        
        output_path = os.path.join(self.output_dir, "dependency_diagram.svg")
        render_mermaid_to_image(result, output_path)
        self.assertTrue(os.path.exists(output_path), "Dependency diagram SVG was not created.")

    def test_call_diagram_generation(self):
        print("\nGenerating Call Diagram...")
        result = self.generator.generate_call_diagram(self.target_dir)
        self.assertIn("sequenceDiagram", result)
        
        output_path = os.path.join(self.output_dir, "call_diagram.svg")
        render_mermaid_to_image(result, output_path)
        self.assertTrue(os.path.exists(output_path), "Call diagram SVG was not created.")

if __name__ == '__main__':
    unittest.main()
