import argparse
import os
import sys
from api_docs_manager.extractor import EndpointExtractor
from api_docs_manager.version_control import APIVersionManager
from api_docs_manager.generator import APIDocGenerator

def main():
    parser = argparse.ArgumentParser(description="Manage API Documentation")
    parser.add_argument("--framework", required=True, choices=["django", "flask", "fastapi"])
    parser.add_argument("--entry", required=True, help="Entry point (e.g. backend.urls)")
    parser.add_argument("--output", default="API_DOCS.md", help="Output Markdown file")
    parser.add_argument("--storage", default=".api_docs_version.json", help="Version storage file")
    
    args = parser.parse_args()
    
    # 1. Extract
    print(f"Extracting endpoints from {args.entry} ({args.framework})...")
    extractor = EndpointExtractor(os.getcwd())
    
    entry_point = args.entry
    if args.framework in ['flask', 'fastapi']:
        # Load app instance from string "module:app"
        try:
            if ":" not in args.entry:
                print("Error: For Flask/FastAPI, entry must be 'module:app'")
                sys.exit(1)
            module_name, app_name = args.entry.split(":")
            import importlib
            import sys
            sys.path.insert(0, os.getcwd()) # Add CWD to path
            module = importlib.import_module(module_name)
            entry_point = getattr(module, app_name)
        except Exception as e:
            print(f"Error loading app '{args.entry}': {e}")
            sys.exit(1)

    try:
        endpoints = extractor.extract(args.framework, entry_point)
    except Exception as e:
        print(f"Extraction failed: {e}")
        sys.exit(1)
        
    print(f"Found {len(endpoints)} endpoints.")
    
    # 2. Version Control
    version_manager = APIVersionManager(args.storage)
    diff = version_manager.diff_versions(endpoints)
    
    if diff['added'] or diff['removed'] or diff['deprecated']:
        print("Changes detected:")
        print(f"  Added: {len(diff['added'])}")
        print(f"  Removed: {len(diff['removed'])}")
        print(f"  Deprecated: {len(diff['deprecated'])}")
    else:
        print("No changes detected.")
        
    # 3. Generate Docs
    generator = APIDocGenerator()
    markdown = generator.generate_markdown(endpoints, diff)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    print(f"Documentation generated at {args.output}")
    
    # 4. Save Version
    version_manager.save_version(endpoints)
    print("Version info saved.")

if __name__ == "__main__":
    main()
