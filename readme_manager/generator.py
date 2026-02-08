import os
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader
import typing
import requests
import json
import traceback

class ReadmeGenerator:
    def __init__(self, project_root: str, api_key: str = None, model_provider: str = "gemini", model_name: str = None):
        self.project_root = project_root
        self.api_key = api_key
        self.model_provider = model_provider
        
        if self.model_provider == "gemini":
            if not self.api_key:
                raise ValueError("API Key is required for Gemini provider")
            genai.configure(api_key=self.api_key)
            self.model_name = model_name or 'gemini-2.0-flash'
            self.model = genai.GenerativeModel(self.model_name)
        elif self.model_provider == "ollama":
            self.model_name = model_name or 'gemma3:4b'
            self.ollama_url = "http://localhost:11434/api/generate"
        else:
            raise ValueError(f"Unsupported provider: {self.model_provider}")

    def analyze_structure(self) -> str:
        """Generates a string representation of the project structure."""
        structure = []
        for root, dirs, files in os.walk(self.project_root):
             # Skip hidden directories and virtual environments
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', 'env', '__pycache__', 'node_modules']]
            level = root.replace(self.project_root, '').count(os.sep)
            indent = ' ' * 4 * (level)
            structure.append(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if not f.startswith('.') and not f.endswith('.pyc'):
                    structure.append(f'{subindent}{f}')
        return '\n'.join(structure[:50]) # Limit to 50 lines to avoid token limits

    def _read_file_content(self, relative_path: str) -> str:
        """Reads content of a file, returning empty string if not found."""
        try:
            with open(os.path.join(self.project_root, relative_path), 'r', encoding='utf-8') as f:
                return f.read()[:2000] # Limit content
        except Exception:
            return ""

    def _generate_with_gemini(self, prompt: str) -> typing.Dict[str, typing.Any]:
        response = self.model.generate_content(prompt)
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_text)

    def _generate_with_ollama(self, prompt: str) -> typing.Dict[str, typing.Any]:
        payload = {
            "model": self.model_name,
            "prompt": prompt + "\nRespond ONLY with valid JSON. Do not include markdown formatting.",
            "stream": False,
            "format": "json"
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return json.loads(data['response'])
        except Exception as e:
            print(f"Ollama generation error: {e}")
            raise

    def generate_content(self) -> typing.Dict[str, typing.Any]:
        """Generates content for the README."""
        
        # Gather context
        structure = self.analyze_structure()
        requirements = self._read_file_content('requirements.txt')
        
        # Heuristic for main logic
        main_code_content = ""
        # Try to find some key files
        for root, _, files in os.walk(self.project_root):
             if 'app.py' in files:
                 main_code_content += self._read_file_content(os.path.join(root, 'app.py'))
             if 'views.py' in files:
                 main_code_content += self._read_file_content(os.path.join(root, 'views.py'))
             if 'models.py' in files:
                 main_code_content += self._read_file_content(os.path.join(root, 'models.py'))
        
        prompt = f"""
        You are an expert technical writer. Generate content for a README.md file based on the following project context.
        
        Project Structure:
        {structure}
        
        Requirements:
        {requirements}
        
        Code Snippets:
        {main_code_content[:2000]}
        
        Return a valid JSON object with the following keys:
        - project_name: str
        - overview: str (2-3 sentences)
        - features: list of objects {{ "name": str, "description": str }}
        - architecture_summary: str (brief explanation of how it works)
        - usage_instructions: str (basic usage)
        - api_endpoints: list of objects {{ "method": str, "path": str, "description": str }} (infer from code if possible, else empty)
        - language: str (e.g., Python)
        
        Do not include markdown formatting in the JSON.
        """
        
        try:
            if self.model_provider == "gemini":
                return self._generate_with_gemini(prompt)
            elif self.model_provider == "ollama":
                return self._generate_with_ollama(prompt)
        except Exception as e:
            print(f"Error generating content: {e}")
            traceback.print_exc()
            # Fallback data
            return {
                "project_name": "Project",
                "overview": "Automated documentation generation failed.",
                "features": [],
                "architecture_summary": "N/A",
                "usage_instructions": "N/A",
                "api_endpoints": [],
                "language": "Python"
            }

    def render(self, output_path: str):
        """Renders the README template."""
        data = self.generate_content()
        data['structure'] = self.analyze_structure() # Add structure explicitly
        data['repo_url'] = "https://github.com/yourusername/project" # Placeholder
        
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
        template = env.get_template('README.md.j2')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template.render(**data))
        print(f"README generated at {output_path}")

if __name__ == "__main__":
    # For testing
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate README')
    parser.add_argument('--key', help='Gemini API Key')
    parser.add_argument('--provider', default='gemini', choices=['gemini', 'ollama'])
    parser.add_argument('--model', help='Model name')
    args = parser.parse_args()

    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    
    if args.provider == 'gemini' and not api_key:
         print("Please provide GEMINI_API_KEY for Gemini provider")
         sys.exit(1)
         
    generator = ReadmeGenerator(os.getcwd(), api_key, args.provider, args.model)
    generator.render("README_gen.md")

