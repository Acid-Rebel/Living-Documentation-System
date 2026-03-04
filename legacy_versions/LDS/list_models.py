import google.generativeai as genai
import os
import sys

api_key = os.environ.get("GEMINI_API_KEY")
if len(sys.argv) > 1:
    api_key = sys.argv[1]

if not api_key:
    print("No API key provided")
    sys.exit(1)

genai.configure(api_key=api_key)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
