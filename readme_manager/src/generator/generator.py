import os
import datetime
from typing import Dict, Any

from ..parser.nodejs import NodeParser
from ..parser.python import PythonParser
from ..parser.go import GoParser
from ..parser.generic import GenericParser
from ..detector.classifier import Classifier
from ..detector.feature_extractor import FeatureExtractor
from ..template.renderer import Renderer
from ..config.config import Config

class Generator:
    def __init__(self, project_root: str, config: Config):
        self.project_root = project_root
        self.config = config
        self.parsers = [
            NodeParser(project_root),
            PythonParser(project_root),
            GoParser(project_root),
            GenericParser(project_root)
        ]
        self.classifier = Classifier()
        self.feature_extractor = FeatureExtractor(project_root)
        
        # Setup template dir relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.renderer = Renderer(os.path.join(base_dir, "templates"))

    def generate(self) -> str:
        # 1. Parse Metadata
        metadata = {}
        for parser in self.parsers:
            if parser.detect():
                metadata = parser.parse()
                break # Stop at first detected language for now
        
        # 2. Detect Project Type
        project_type = self.config.project_type
        if project_type == "auto":
            project_type = self.classifier.classify(metadata)

        # 3. Prepare Context
        context = self._prepare_context(metadata, project_type)
        
        # 4. Render
        template_name = self.config.template
        if template_name == "auto":
            # For this MVP, we map types to templates (mapping to base.md for now)
            template_name = "base.md" 
        
        return self.renderer.render(template_name, context)

    def _prepare_context(self, metadata: Dict[str, Any], project_type: str) -> Dict[str, Any]:
        
        # Derive installation commands based on framework/lang
        install_cmds = "npm install" # Default
        if metadata.get("language") == "Python":
            install_cmds = "pip install -r requirements.txt"
        elif metadata.get("language") == "Go":
            install_cmds = "go mod download"

        # Generate structure preview (simplified)
        structure = ".\n"
        try:
           for item in os.listdir(self.project_root)[:5]:
               structure += f"├── {item}\n"
        except:
           pass


        # Extract features
        detected_features = self.feature_extractor.extract_features()
        if not detected_features and self.config.sections.get("features", True):
             detected_features = [
                "Feature detection not yet implemented.",
                "Automatic documentation generation.",
                "Version tracking."
            ]

        return {
            "PROJECT_NAME": metadata.get("name", "Project Name").title(),
            "VERSION": metadata.get("version", "1.0.0"),
            "DESCRIPTION": metadata.get("description", "A new awesome project."),
            "OVERVIEW": f"This is a {project_type} built with {metadata.get('language', 'Unknown')}.",
            "SETUP": self.config.sections.get("setup", True),
            "PREREQUISITES": metadata.get("language", "Runtime environment"),
            "INSTALL_COMMANDS": install_cmds,
            "FEATURES": detected_features if self.config.sections.get("features", True) else None,
            "TECH_STACK": metadata.get("frameworks", []),
            "STRUCTURE": structure,
            "LICENSE": metadata.get("license", "MIT") 
        }
