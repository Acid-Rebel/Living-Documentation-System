import argparse
import os
import sys

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config.config import Config
from src.analyzer.structure_analyzer import StructureAnalyzer
from src.analyzer.dependency_analyzer import DependencyAnalyzer
from src.detector.pattern_detector import PatternDetector
from src.generator.doc_generator import DocGenerator

def main():
    parser = argparse.ArgumentParser(description="Architecture Docs Manager")
    parser.add_argument("command", choices=["generate", "info"], help="Command to run")
    parser.add_argument("--path", default=".", help="Project root")
    
    args = parser.parse_args()
    project_root = os.path.abspath(args.path)
    config = Config()
    
    if args.command == "generate":
        print(f"Analyzing {project_root}...")
        
        # 1. Structure
        struct_analyzer = StructureAnalyzer(config)
        structure = struct_analyzer.analyze(project_root)
        
        # 2. Dependencies
        dep_analyzer = DependencyAnalyzer()
        deps = dep_analyzer.analyze(project_root)
        
        # 3. Patterns
        detector = PatternDetector()
        patterns = detector.detect(structure)
        
        # 4. Generate
        gen = DocGenerator()
        content = gen.generate(structure, deps, patterns)
        
        out_file = os.path.join(project_root, "ARCHITECTURE.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Generated {out_file}")
        
    elif args.command == "info":
        struct_analyzer = StructureAnalyzer(config)
        structure = struct_analyzer.analyze(project_root)
        print("Detected Structure:")
        for k, v in structure['layers'].items():
            if v:
                print(f"  {k}: {len(v)} components")

if __name__ == "__main__":
    main()
