import os
import sys
import argparse
from readme_manager.generator import ReadmeGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate README documentation')
    parser.add_argument('api_key', nargs='?', help='Gemini API Key')
    parser.add_argument('--provider', choices=['gemini', 'ollama'], default='gemini', help='Model provider')
    parser.add_argument('--model', help='Model name override')
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    
    if args.provider == 'gemini' and not api_key:
        print("Error: GEMINI_API_KEY environment variable not set and not provided as argument for Gemini provider.")
        sys.exit(1)

    print(f"Generating README for current directory: {os.getcwd()}")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model or 'default'}")
    
    try:
        generator = ReadmeGenerator(os.getcwd(), api_key, args.provider, args.model)
        generator.render("README_gen.md")
        print("Done! Check README_gen.md")
    except Exception as e:
        print(f"Failed to generate documentation: {e}")

if __name__ == "__main__":
    main()
