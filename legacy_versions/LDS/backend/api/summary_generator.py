import os
import google.generativeai as genai
import typing
import traceback

class SummaryGenerator:
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
                return f.read()[:5000] 
        except Exception:
            return ""

    def generate_summary(self) -> str:
        """Generates a high-level project summary Markdown using Gemini."""
        
        # Context Gathering
        code_context = ""
        # Prioritize files likely to contain architectural info
        files_to_scan = [
            'README.md', 'package.json', 'requirements.txt', 'docker-compose.yml',
            'app.py', 'main.py', 'server.js', 'index.js', 'views.py', 'models.py', 'routes.py'
        ]
        
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file in files_to_scan:
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, self.project_root)
                    content = self._read_file_content(rel_path)
                    if content:
                        code_context += f"\n--- File: {rel_path} ---\n{content}\n"
        
        prompt = f"""
        You are a senior software architect. Provide a concise but comprehensive EXECUTIVE SUMMARY of the following codebase.
        
        The audience is a developer or stakeholder joining the project.
        
        Focus on:
        1. **Core Purpose**: What does this application do?
        2. **Key Technologies**: What stack is used?
        3. **Architecture**: High-level design patterns (MVC, Microservices, etc.).
        4. **Main Capabilities**: What are the primary features?
        
        Format as Markdown. Keep it strictly summary-focused. 
        
        Code Context:
        {code_context[:25000]} 
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            traceback.print_exc()
            return f"# Project Summary\n\nError generating summary: {str(e)}"
