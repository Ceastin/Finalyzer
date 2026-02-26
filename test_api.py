import os
import google.generativeai as genai
from dotenv import load_dotenv

# Force load the .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: The API key is blank. Python is not reading your .env file properly.")
elif api_key == "your-google-gemini-key-here":
    print("❌ ERROR: You are still using the placeholder text instead of a real key.")
else:
    print(f"✅ Key detected (starts with {api_key[:5]}). Attempting connection...")
    try:
        genai.configure(api_key=api_key)
        # 👇 THIS IS THE CRITICAL CHANGE - Using the active 2.5 architecture
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Reply with the word 'Success'")
        print(f"🤖 Gemini Connection: {response.text}")
    except Exception as e:
        print(f"❌ Actual API Error: {e}")