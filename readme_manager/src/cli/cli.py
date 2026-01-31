import argparse
import os
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.generator.generator import Generator
from src.config.config import Config

def main():
    parser = argparse.ArgumentParser(description="Readme Manager CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Generate Command
    gen_parser = subparsers.add_parser("generate", help="Generate a new README")
    gen_parser.add_argument("--path", default=".", help="Project root path")
    
    # Info Command
    info_parser = subparsers.add_parser("info", help="Show detected project info")
    info_parser.add_argument("--path", default=".", help="Project root path")

    args = parser.parse_args()

    project_root = os.path.abspath(args.path)
    config = Config() # Loads .readmerc from CWD or project_root if implemented

    if args.command == "generate":
        print(f"Generating README for {project_root}...")
        generator = Generator(project_root, config)
        content = generator.generate()
        
        output_path = os.path.join(project_root, "README.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"README.md generated at {output_path}")

    elif args.command == "info":
        generator = Generator(project_root, config)
        # Hack to access internal parsers for info
        for p in generator.parsers:
             if p.detect():
                 print(f"Detected: {p.parse()}")
                 break
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
