import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: API Key not found in .env file.")
    exit()

print(f"🔑 Using API Key: {api_key[:5]}... (hidden)")
genai.configure(api_key=api_key)

print("\n📡 Connecting to Google servers to fetch YOUR available models...")

try:
    # 2. List all models available to your specific Key
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f"   • Found: {m.name}")

    if not available_models:
        print("❌ No text generation models found for this API Key.")
        print("👉 Solution: Create a new API Key at https://aistudio.google.com/")
        exit()

    print("\n🧪 Testing each model to find one that works...")

    # 3. Test each model to see which one actually generates text
    working_model = None
    
    for model_name in available_models:
        # Remove 'models/' prefix if present for the initialization
        short_name = model_name.replace("models/", "")
        
        print(f"   Testing '{short_name}'...", end=" ")
        try:
            model = genai.GenerativeModel(short_name)
            response = model.generate_content("Hello")
            print("✅ WORKS!")
            working_model = short_name
            break # Stop after finding the first working one
        except Exception as e:
            if "429" in str(e):
                print("⚠️ Quota Exceeded (Wait a bit)")
            else:
                print(f"❌ Failed ({str(e)[:50]}...)")

    print("\n" + "="*40)
    if working_model:
        print(f"🎉 SUCCES! Update your code to use this line:")
        print(f"model = genai.GenerativeModel('{working_model}')")
    else:
        print("😞 None of the models worked right now.")
    print("="*40)

except Exception as e:
    print(f"❌ Connection Error: {e}")