import gradio as gr
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import os

# =========================================================
# 1. CONFIGURATION
# =========================================================

API_KEY = os.getenv("GMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        ""
    )

genai.configure(api_key=API_KEY)


# =========================================================
# 2. CONNECT TO GEMINI
# =========================================================

def connect_to_model():

    models = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-1.5-flash",
        "models/gemini-pro"
    ]

    for name in models:

        try:
            model = genai.GenerativeModel(name)

            # Test connection
            test_chat = model.start_chat(history=[])
            test_chat.send_message("Hello")

            print(f"Connected to: {name}")

            return model, name

        except Exception as e:
            print(f"Failed: {name}")

    return None, "No Connection"


model, model_name = connect_to_model()

if model:
    chat = model.start_chat(history=[])
else:
    chat = None


# =========================================================
# 3. AVATAR IMAGES
# =========================================================

IMG_LISTEN = "listening.png"
IMG_HAPPY = "smiling.png"
IMG_THINK = "confused.png"


# =========================================================
# 4. TEXT TO SPEECH
# =========================================================

def text_to_audio(text):

    try:

        engine = pyttsx3.init()

        engine.setProperty("rate", 155)

        output_file = "response_voice.mp3"

        engine.save_to_file(text, output_file)

        engine.runAndWait()

        return output_file

    except Exception as e:

        print("TTS Error:", e)

        return None


# =========================================================
# 5. SPEECH TO TEXT
# =========================================================

def speech_to_text(audio_path):

    if not audio_path:
        return ""

    try:

        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_path) as source:

            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)

        return text

    except Exception as e:

        print("Speech Recognition Error:", e)

        return ""


# =========================================================
# 6. INTERVIEW FUNCTION
# =========================================================

def interview_logic(audio, interview_type, difficulty):

    # Check microphone input

    if not audio:

        return (
            IMG_LISTEN,
            "⚠️ Please record your answer first.",
            None
        )


    # Convert voice to text

    user_input = speech_to_text(audio)

    if not user_input:

        return (
            IMG_LISTEN,
            "⚠️ I could not understand your voice. Please try again.",
            None
        )


    print("Candidate:", user_input)


    # Quit

    if user_input.lower().strip() in ["quit", "exit", "stop"]:

        message = "Goodbye! Good luck with your interview practice."

        audio_reply = text_to_audio(message)

        return IMG_HAPPY, message, audio_reply


    # =====================================================
    # AI INSTRUCTIONS
    # =====================================================

    system_instruction = f"""
You are a professional AI interview tutor.

Interview Type:
{interview_type}

Difficulty:
{difficulty}

Your job is to conduct a realistic interview.

Rules:

1. Ask only ONE question at a time.

2. Analyze the candidate's latest answer.

3. Check English grammar.

4. If there is a grammar mistake, show:

Original:
[original sentence]

Correct:
[correct sentence]

Explanation:
[simple explanation]

5. Give an English score from 1 to 10.

6. For technical interviews, give a Technical score from 1 to 10.

7. Give short feedback.

8. Ask ONE relevant next interview question.

9. Do not give the answer before the candidate attempts it.

10. Keep the response simple because the candidate is practicing English.

11. At the beginning of the response use exactly one mood tag:

[HAPPY]

if the answer is good.

[THINK]

if the answer needs improvement.

Example:

[HAPPY]

Grammar:
Your sentence is good.

English Score: 8/10

Technical Score: 8/10

Feedback:
Good answer. Try to explain your project with more details.

Next Question:
What is Spring Boot?
"""


    # =====================================================
    # SEND TO GEMINI
    # =====================================================

    try:

        if not chat:

            return (
                IMG_LISTEN,
                "❌ Gemini connection failed.",
                None
            )


        prompt = f"""
{system_instruction}

Candidate's latest answer:

"{user_input}"

Analyze this answer and continue the interview.
"""


        response = chat.send_message(prompt)

        reply_text = response.text


        # =================================================
        # AVATAR MOOD
        # =================================================

        if "[HAPPY]" in reply_text:

            character_mood = IMG_HAPPY

            clean_text = reply_text.replace(
                "[HAPPY]",
                "🎉 <b>Excellent!</b>"
            )

        elif "[THINK]" in reply_text:

            character_mood = IMG_THINK

            clean_text = reply_text.replace(
                "[THINK]",
                "🤔 <b>Let's improve that.</b>"
            )

        else:

            character_mood = IMG_LISTEN

            clean_text = reply_text


        # =================================================
        # AUDIO
        # =================================================

        voice_text = clean_text

        # Remove basic HTML

        voice_text = voice_text.replace(
            "<b>",
            ""
        ).replace(
            "</b>",
            ""
        )

        audio_reply = text_to_audio(voice_text)


        return (
            character_mood,
            clean_text,
            audio_reply
        )


    except Exception as e:

        print("Gemini Error:", e)

        error_message = f"❌ Error: {e}"

        return (
            IMG_LISTEN,
            error_message,
            None
        )


# =========================================================
# 7. GRADIO UI
# =========================================================

with gr.Blocks(
    theme=gr.themes.Soft(),
    title="AI Interview Tutor"
) as app:

    gr.Markdown(
        """
        # 🎓 AI Interview Tutor

        Practice **English + HR + Java + Full Stack Java Interviews**
        with voice.
        """
    )


    # =====================================================
    # SETTINGS
    # =====================================================

    with gr.Row():

        interview_type = gr.Dropdown(

            choices=[
                "HR Interview",
                "Java Interview",
                "Full Stack Java Interview",
                "English Speaking Practice"
            ],

            value="Full Stack Java Interview",

            label="Interview Type"
        )


        difficulty = gr.Dropdown(

            choices=[
                "Beginner",
                "Intermediate",
                "Advanced"
            ],

            value="Beginner",

            label="Difficulty"
        )


    # =====================================================
    # MAIN UI
    # =====================================================

    with gr.Row():

        with gr.Column(scale=1):

            avatar = gr.Image(

                value=IMG_LISTEN,

                label="AI Teacher",

                height=350,

                show_download_button=False
            )


        with gr.Column(scale=2):

            gr.Markdown(
                """
                ### 🎤 Interview Instructions

                1. Select interview type.
                2. Select difficulty.
                3. Click **Record**.
                4. Answer the question.
                5. Click **Submit Answer**.
                """
            )


            audio_input = gr.Audio(

                sources=["microphone"],

                type="filepath",

                label="Your Answer"
            )


            submit_btn = gr.Button(
                "🚀 Submit Answer",
                variant="primary"
            )


            ai_text = gr.Markdown(
                label="AI Feedback"
            )


            ai_audio = gr.Audio(
                label="🔊 AI Voice",
                autoplay=True
            )


    # =====================================================
    # BUTTON EVENT
    # =====================================================

    submit_btn.click(

        fn=interview_logic,

        inputs=[
            audio_input,
            interview_type,
            difficulty
        ],

        outputs=[
            avatar,
            ai_text,
            ai_audio
        ]
    )


# =========================================================
# 8. START APP
# =========================================================

app.launch()