from .code_analyzer import CodeAnalyzer

class FileSummarizer:
    """
    Generates a high-level narrative summary of a Python file.
    """

    def __init__(self):
        self.analyzer = CodeAnalyzer()

    def summarize_file(self, code):
        """
        Analyzes the file and produces a natural language summary.
        """
        structure = self.analyzer.get_file_structure(code)
        if not structure:
             return "Could not parse file structure (Syntax Error)."

        summary_lines = []
        
        # 1. Module Level Summary
        if structure['docstring']:
             summary_lines.append(f"**File Overview**: {self._format_docstring(structure['docstring'])}")
        else:
             summary_lines.append("**File Overview**: This module provides utilities and classes.")

        # 2. Key Components (Classes)
        if structure['classes']:
             summary_lines.append("\n**Key Classes:**")
             for cls in structure['classes']:
                 desc = self._format_docstring(cls.get('docstring')) or "Implements core functionality."
                 summary_lines.append(f"- `class {cls['name']}`: {desc}")
                 # Mention key methods if available
                 if cls['methods']:
                     method_names = [m['name'] for m in cls['methods'] if not m['name'].startswith('_')]
                     if method_names:
                         summary_lines.append(f"  - Key methods: {', '.join(method_names[:3])}" + ("..." if len(method_names) > 3 else ""))

        # 3. Global Functions
        if structure['functions']:
             summary_lines.append("\n**Global Functions:**")
             for func in structure['functions']:
                 desc = self._format_docstring(func.get('docstring')) or "Utility function."
                 summary_lines.append(f"- `{func['name']}`: {desc}")

        return "\n".join(summary_lines)

    def _format_docstring(self, docstring):
        """
        Helper to format docstring for summary inclusion.
        Takes the first line.
        """
        if not docstring:
            return ""
        
        # Take first line only
        first_line = docstring.strip().split('\n')[0]
        return first_line.strip()
