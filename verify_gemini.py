import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Checking API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    exit(1)

try:
    genai.configure(api_key=api_key)
    print("Listing available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
    print("\nAttempting generation with 'gemini-2.5-flash'...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Hello")
    print(f"Success! Response: {response.text}")

except Exception as e:
    print(f"\nFAILURE: {e}")
