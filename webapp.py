import gradio as gr
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr

# --- CONFIGURATION ---
API_KEY = ""

genai.configure(api_key=API_KEY)

# --- 1. SMART CONNECTION ---
def connect_to_model():
    # Priority list for 3D Character Logic
    models = ["models/gemini-2.0-flash", "models/gemini-1.5-flash", "models/gemini-pro"]
    for name in models:
        try:
            model = genai.GenerativeModel(name)
            model.start_chat(history=[]).send_message("Test")
            return model, name
        except:
            continue
    return None, "No Connection"

model, model_name = connect_to_model()
chat = model.start_chat(history=[]) if model else None

# --- 2. THE 3D CHARACTERS (I Googled these for you) ---
# These are high-quality 3D avatars that look like "Real" cartoons.
IMG_LISTEN = ""
IMG_HAPPY  = "smiling.png" 
IMG_THINK  = "confused.png"

# --- 3. AUDIO FUNCTIONS ---
def text_to_audio(text):
    try:
        engine = pyttsx3.init()
        # Slow down slightly for "Teacher" vibe
        engine.setProperty('rate', 155) 
        output_file = "response_voice.mp3"
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        return output_file
    except:
        return None

def speech_to_text(audio_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except:
        return ""

def interview_logic(audio):
    if not model:
        return IMG_LISTEN, "Error: Check API Key", None

    if audio is None:
        return IMG_LISTEN, "Please record first.", None
    
    user_text = speech_to_text(audio)
    if not user_text:
        return IMG_LISTEN, "I didn't hear anything.", None

    # --- THE "REAL TEACHER" PROMPT ---
    prompt = (
        f"User said: '{user_text}'. "
        "You are a friendly 3D English Teacher character. "
        "Analyze the grammar. "
        "If PERFECT: Start with [HAPPY]. "
        "If MISTAKES: Start with [THINK]. "
        "Then provide corrections using HTML: <b style='color:red'>Mistake</b> -> <b style='color:green'>Correction</b>."
    )
    
    try:
        response = chat.send_message(prompt)
        reply_text = response.text
        
        # REACTIVE FACE LOGIC
        if "[HAPPY]" in reply_text:
            character_mood = IMG_HAPPY
            clean_text = reply_text.replace("[HAPPY]", "🎉 **Excellent!**")
        elif "[THINK]" in reply_text:
            character_mood = IMG_THINK
            clean_text = reply_text.replace("[THINK]", "🤔 **Let's correct that:**")
        else:
            character_mood = IMG_LISTEN
            clean_text = reply_text

    except Exception as e:
        character_mood = IMG_LISTEN
        clean_text = f"Error: {e}"

    # Generate Audio (Strip HTML for voice)
    voice_text = clean_text.replace("<b style='color:red'>", "").replace("<b style='color:green'>", "").replace("</b>", "")
    audio_reply = text_to_audio(voice_text)
    
    return character_mood, clean_text, audio_reply

# --- 4. INTERACTIVE UI ---
with gr.Blocks(theme=gr.themes.Soft()) as app: 
    gr.Markdown("# 🎓 Real 3D English Coach")
    
    with gr.Row():
        with gr.Column(scale=1):
            # The Avatar Image
            avatar = gr.Image(value=IMG_LISTEN, label="Teacher", height=350, show_download_button=False)
        
        with gr.Column(scale=2):
            gr.Markdown("### 1. Click Record \n 2. Speak to the teacher!")
            audio_input = gr.Audio(sources=["microphone"], type="filepath")
            submit_btn = gr.Button("Submit Answer", variant="primary")
            
            ai_text = gr.HTML(label="Feedback")
            ai_audio = gr.Audio(label="Voice", autoplay=True)

    submit_btn.click(fn=interview_logic, inputs=audio_input, outputs=[avatar, ai_text, ai_audio])

app.launch()