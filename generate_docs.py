import os
import sys
from readme_manager.generator import ReadmeGenerator

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set and not provided as argument.")
        sys.exit(1)

    print(f"Generating README for current directory: {os.getcwd()}")
    
    try:
        generator = ReadmeGenerator(os.getcwd(), api_key)
        generator.render("README_gen.md")
        print("Done! Check README_gen.md")
    except Exception as e:
        print(f"Failed to generate documentation: {e}")

if __name__ == "__main__":
    main()
