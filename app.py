
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import time

# --- PASTE YOUR API KEY HERE ---
API_KEY = "AIzaSyAmqpofnKnIeUl7juM-iQD6oFgcNYofQGg"

# 1. Setup Brain (Using the model from YOUR list)
try:
    genai.configure(api_key=API_KEY)
    
    # We are using 'gemini-2.5-flash' because it appeared in your list
    model = genai.GenerativeModel('models/gemini-2.5-flash') 
    chat = model.start_chat(history=[])
    print("SUCCESS: Connected to Google AI!")
    
except Exception as e:
    print(f"Error connecting to Google: {e}")

# 2. Setup Mouth (Voice)
engine = pyttsx3.init()
engine.setProperty('rate', 160) 

# 3. Setup Ears (Microphone)
recognizer = sr.Recognizer()

def speak(text):
    print(f"AI: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("\nListening... (Speak now!)")
        # Adjust for mobile data/hotspot noise
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        try:
            # Increased timeout for mobile data
            audio = recognizer.listen(source, timeout=10)
            print("Thinking...")
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except Exception:
            return None

# --- MAIN LOOP ---
print("--------------------------------------------------")
print("AI INTERVIEWER IS READY!")
print("--------------------------------------------------")

speak("Hello Venkatesh! I am ready. Please introduce yourself.")

while True:
    user_input = listen()
    
    if user_input is None:
        continue 
        
    if "quit" in user_input.lower():
        speak("Goodbye!")
        break
    
    # Instructions for the AI
    prompt = (
        f"User said: '{user_input}'. "
        "Act as an English interviewer. "
        "Correct my grammar mistakes gently, then ask the next question."
    )
    
    try:
        response = chat.send_message(prompt)
        speak(response.text)
    except Exception as e:
        print(f"Error: {e}")
        # If this happens, it is likely the API Key or Model Name again
        speak("I got an error. Please read the text on the screen.")