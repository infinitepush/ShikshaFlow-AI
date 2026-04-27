
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or 'YOUR_API_KEY_HERE' in GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found or not updated in .env file.")
    print("   Please open 'backend/.env' and paste your new API key.")
else:
    print("API Key found in .env file.")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("genai.configure() successful.")
        print("\nAttempting to list available models...")
        
        # This is the crucial test.
        # We list models and check if they support the 'generateContent' method.
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            print("\nERROR: Your API key is valid, but no models were found for your project.")
            print("   This almost always means you need to do one of these things in your Google Cloud Project:")
            print("   1. Enable the 'Generative Language API'.")
            print("   2. Make sure a Billing Account is linked to your project.")
        else:
            print("\nSUCCESS! Your API key and project are configured correctly.")
            print("   Found the following usable models:")
            for m in models:
                print(f"   - {m.name}")

    except Exception as e:
        print("\nAn error occurred while trying to connect to the Google API.")
        print(f"   Error details: {e}")
        print("\n   This usually means the API key itself is invalid or has been copied incorrectly.")

