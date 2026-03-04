import os
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader
import typing
import json
import traceback
from dotenv import load_dotenv

class ReadmeGenerator:
    def __init__(self, project_root: str, api_key: str):
        self.project_root = project_root
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API Key is required")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

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
                return f.read()[:3000] # Increased limit for better context
        except Exception:
            return ""

    def generate_content(self) -> typing.Dict[str, typing.Any]:
        """Generates content for the README using Gemini."""
        
        # Gather context
        structure = self.analyze_structure()
        requirements = self._read_file_content('requirements.txt')
        
        # Enhanced Context Gathering
        code_context = ""
        files_to_scan = ['app.py', 'views.py', 'models.py', 'urls.py', 'serializers.py', 'manage.py', 'package.json']
        
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file in files_to_scan:
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, self.project_root)
                    content = self._read_file_content(path)
                    if content:
                        code_context += f"\n--- File: {rel_path} ---\n{content}\n"
        
        prompt = f"""
        You are an expert technical writer. Generate content for a README.md file based on the following project context.
        
        Project Structure:
        {structure}
        
        Requirements:
        {requirements}
        
        Code Context:
        {code_context[:8000]} 
        
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
            response = self.model.generate_content(prompt)
            import re
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                cleaned_text = match.group(0)
                return json.loads(cleaned_text)
            else:
                 # Try cleaning standard markdown
                cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned_text)
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
    import sys
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if api_key:
        generator = ReadmeGenerator(os.getcwd(), api_key)
        generator.render("README_gen.md")
    else:
        print("Please provide GEMINI_API_KEY in .env or as argument")
