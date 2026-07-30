# 🎓 SkillTest AI - AI English Interviewer & Coach

SkillTest AI is an interactive AI-powered application designed to help job seekers, students, and English learners practice interview skills and improve spoken English. It integrates Google's Gemini AI, speech recognition, voice synthesis (TTS), and an interactive web interface using Gradio.

---

## ✨ Features

- **🎙️ Voice-Based AI Interviewer:** Speak directly using your microphone and receive instant audio and text feedback.
- **🤖 Powered by Google Gemini AI:** Uses smart language models for realistic interview and English grammar coaching.
- **📝 Real-time Grammar & Syntax Correction:** Gentle, constructive corrections highlighting mistakes and providing better phrasing.
- **🌐 Interactive Web Interface:** Built with Gradio featuring dynamic visual character feedback.
- **🔊 Text-to-Speech (TTS):** Natural voice output using `pyttsx3`.

---

## 📁 Project Structure

```text
SkillTest-AI/
├── app.py              # CLI-based voice interviewer application
├── webapp.py           # Gradio-based interactive web application
├── test_gemini.py      # Test script for Gemini API connection
├── check.py            # Model availability scanner script
├── smiling.png         # Visual avatar (Happy state)
├── confused.png        # Visual avatar (Thinking/Feedback state)
├── requirements.txt    # Required Python packages
├── README.md           # Project documentation
└── .gitignore          # Files ignored by Git
