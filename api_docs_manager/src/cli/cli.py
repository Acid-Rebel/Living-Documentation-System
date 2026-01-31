import argparse
import os
import sys

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.parser.express_parser import ExpressParser
from src.parser.fastapi_parser import FastAPIParser
from src.generator.doc_generator import DocGenerator
from src.config.config import Config

def main():
    parser = argparse.ArgumentParser(description="API Docs Manager")
    parser.add_argument("command", choices=["generate", "info"], help="Command to run")
    parser.add_argument("--path", default=".", help="Project root")
    
    args = parser.parse_args()
    project_root = os.path.abspath(args.path)
    
    if args.command == "generate":
        print(f"Scanning {project_root}...")
        
        endpoints = []
        # Run all parsers (naive approach)
        endpoints.extend(ExpressParser().parse(project_root))
        endpoints.extend(FastAPIParser().parse(project_root))
        
        print(f"Found {len(endpoints)} endpoints.")
        
        gen = DocGenerator()
        content = gen.generate_markdown(endpoints)
        
        with open("API_DOCS.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("Generated API_DOCS.md")
        
    elif args.command == "info":
        # Just count
         endpoints = []
         endpoints.extend(ExpressParser().parse(project_root))
         endpoints.extend(FastAPIParser().parse(project_root))
         print(f"Detected {len(endpoints)} endpoints.")

if __name__ == "__main__":
    main()
