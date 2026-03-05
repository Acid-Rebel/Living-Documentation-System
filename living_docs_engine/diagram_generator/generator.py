import os
import re
from typing import Optional
from openai import OpenAI
from .extractor import CodeExtractor
from .prompts import (
    CLASS_DIAGRAM_SYSTEM_PROMPT,
    DEPENDENCY_DIAGRAM_SYSTEM_PROMPT,
    CALL_DIAGRAM_SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE
)

class DiagramGenerator:
    """Generates codebase diagrams using LLM."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.extractor = CodeExtractor()
        # Initialize client lazily to allow importing without API key during test setup
        self._client = None
    
    @property
    def client(self) -> OpenAI:
        if not self._client:
            if not self.api_key:
                raise ValueError("API Key must be provided for generation.")
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def _call_llm(self, system_prompt: str, codebase_context: str) -> str:
        """Helper to invoke the LLM and extract Mermaid code."""
        user_prompt = USER_PROMPT_TEMPLATE.format(codebase_context=codebase_context)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2, # Low temperature for more deterministic/structured output
        )
        
        content = response.choices[0].message.content
        return self._extract_mermaid(content)
        
    def _extract_mermaid(self, text: str) -> str:
        """Extracts text between ```mermaid and ``` tags."""
        pattern = r"```(?:mermaid)?\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text.strip()

    def generate_class_diagram(self, directory_path: str) -> str:
        """Generates a Class Diagram for the given directory."""
        extracted_files = self.extractor.extract_codebase(directory_path)
        codebase_context = self.extractor.format_for_llm(extracted_files)
        mermaid_code = self._call_llm(CLASS_DIAGRAM_SYSTEM_PROMPT, codebase_context)
        return mermaid_code
