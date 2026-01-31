import re
from typing import Dict, Any

class Renderer:
    def __init__(self, template_dir: str):
        self.template_dir = template_dir

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renders a markdown template by replacing {{KEY}} with values from context.
        Supports conditional blocks:
        {% if KEY %}
        ...
        {% endif %}
        """
        # Load template
        # For simplicity, if template_name is a path, read it, else look in dir
        import os
        template_path = os.path.join(self.template_dir, template_name)
        if not os.path.exists(template_path):
             # Fallback to absolute path or just return empty
             if os.path.exists(template_name):
                 template_path = template_name
             else:
                 return f"Error: Template {template_name} not found."

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Handle simple conditionals {% if KEY %} ... {% endif %}
        # This is a naive implementation without recursion
        def eval_condition(match):
            key = match.group(1).strip()
            block = match.group(2)
            if context.get(key):
                return block
            return ""

        content = re.sub(r'{% if (.*?) %}(.*?){% endif %}', eval_condition, content, flags=re.DOTALL)

        # Handle Variable Substitution {{ KEY }}
        def replace_var(match):
            key = match.group(1).strip()
            val = context.get(key, "")
            if isinstance(val, list):
                return "\n".join([f"- {v}" for v in val])
            return str(val)

        content = re.sub(r'{{(.*?)}}', replace_var, content)

        return content
