import google.generativeai as genai

# --- PASTE YOUR KEY HERE ---
API_KEY =""

genai.configure(api_key=API_KEY)

print("Checking for available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
            
    print("\nDone! Copy one of the names above (like 'models/gemini-pro')")
except Exception as e:
    print(f"Error: {e}")