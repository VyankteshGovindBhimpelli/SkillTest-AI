import os
import gradio as gr
from google import genai
import speech_recognition as sr
from gtts import gTTS

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a Senior Full Stack AI Technical Interviewer.
Ask clear, domain-specific technical questions (Java, Python, React, SQL, Cloud).
Keep answers structured and brief. Evaluation should cover clarity and technical correctness.
"""

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except Exception:
        return None

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    output_audio = "response.mp3"
    tts.save(output_audio)
    return output_audio

def respond(audio_input, text_input, domain, history):
    user_message = ""
    if audio_input is not None:
        user_message = transcribe_audio(audio_input)
    elif text_input:
        user_message = text_input

    if not user_message:
        return history, None, "", "Mic madhun awaz ala nahi, punha prayatna kara."

    prompt = f"{SYSTEM_PROMPT}\nTarget Domain: {domain}\nConversation History: {history}\nUser: {user_message}\nAI:"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"API Error: {str(e)}"

    audio_reply = text_to_speech(bot_reply)
    history.append((user_message, bot_reply))

    return history, audio_reply, "", "Interview Session Active 🟢"

# Custom Modern Dark Theme UI
custom_css = """
body { background: #0b0f19; font-family: 'Inter', sans-serif; color: #f3f4f6; }
.gradio-container { max-width: 1000px !important; margin: auto; }
.header-box { text-align: center; padding: 20px; background: linear-gradient(135deg, #1e1b4b, #0f172a); border-radius: 12px; margin-bottom: 20px; border: 1px solid #312e81; }
.header-title { font-size: 30px; font-weight: 800; color: #38bdf8; letter-spacing: -0.5px; }
.header-sub { color: #94a3b8; font-size: 14px; margin-top: 5px; }
"""

with gr.Blocks(css=custom_css, title="SkillTest AI — Pro") as demo:
    gr.HTML("""
    <div class="header-box">
        <div class="header-title">⚡ SkillTest AI — Full Stack Mock Interviewer</div>
        <div class="header-sub">Practice Java, Python, React & Database Interviews with Real-time Voice AI</div>
    </div>
    """)

    with gr.Row():
        domain_selector = gr.Dropdown(
            choices=["Java Full Stack", "Python & AI/ML", "React & Frontend", "SQL & Database", "System Design"],
            value="Java Full Stack",
            label="🎯 Select Target Job Role / Domain"
        )
        status = gr.Textbox(value="Ready", label="Session Status 📡", interactive=False)

    chatbot = gr.Chatbot(label="💬 Live AI Interview Transcript", height=380)

    with gr.Row():
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Voice Answer (Speak Here)")
        text_input = gr.Textbox(placeholder="Type your technical response here...", label="⌨️ Text Answer")

    audio_output = gr.Audio(label="🔊 AI Interviewer Response Audio", autoplay=True)

    with gr.Row():
        submit_btn = gr.Button("Submit Response 🚀", variant="primary")
        clear_btn = gr.Button("Reset Conversation 🔄")

    submit_btn.click(
        fn=respond,
        inputs=[audio_input, text_input, domain_selector, chatbot],
        outputs=[chatbot, audio_output, text_input, status]
    )

    clear_btn.click(lambda: ([], None, "", "Session Reset"), None, [chatbot, audio_output, text_input, status])

if __name__ == "__main__":
    demo.launch(share=False)