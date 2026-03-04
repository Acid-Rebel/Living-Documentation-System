import os
import google.generativeai as genai
import typing
import json
import traceback

class ApiDocGenerator:
    def __init__(self, project_root: str, api_key: str):
        self.project_root = project_root
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API Key is required")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def _read_file_content(self, relative_path: str) -> str:
        """Reads content of a file, returning empty string if not found."""
        try:
            with open(os.path.join(self.project_root, relative_path), 'r', encoding='utf-8') as f:
                return f.read()[:5000] # Increased limit for API context
        except Exception:
            return ""

    def generate_api_docs(self) -> str:
        """Generates API documentation markdown using Gemini."""
        
        # Enhanced Context Gathering for APIs
        code_context = ""
        # Prioritize files likely to contain API definitions
        files_to_scan = [
            'views.py', 'urls.py', 'serializers.py', 'models.py', 'api.py', 'main.py', 'app.py',
            'routes.py', 'controllers.py', 'server.js', 'app.js', 'routes.js', 'index.js'
        ]
        
        found_files = []
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file in files_to_scan or file.endswith(('views.py', 'urls.py', 'serializers.py')):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, self.project_root)
                    content = self._read_file_content(rel_path)
                    if content:
                        code_context += f"\n--- File: {rel_path} ---\n{content}\n"
                        found_files.append(rel_path)
        
        if not code_context:
            return "# API Documentation\n\nNo API definition files found to analyze."

        prompt = f"""
        You are an expert technical writer specializing in API documentation.
        Generate a comprehensive API Documentation summary in Markdown format based on the following code context.
        
        Focus on:
        1.  **Overview**: High-level purpose of the API.
        2.  **Authentication**: How to authenticate (if detected).
        3.  **Endpoints**: List endpoints with Methods (GET, POST, etc.), URLs, Description, and expected Payload/Response if inferable.
        4.  **Error Handling**: Standard error codes used.
        
        Format the output as clean, professional Markdown suitable for conversion to PDF. 
        Use clear headings (H1, H2, H3). Use tables for endpoint lists if appropriate.
        
        Code Context:
        {code_context[:30000]} 
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating API docs: {e}")
            traceback.print_exc()
            return f"# API Documentation\n\nError generating documentation: {str(e)}"
