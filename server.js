const express = require('express');
const cors = require('cors');
const path = require('path');
const { GoogleGenAI } = require('@google/genai');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// static फाईल्स सर्व्ह करण्यासाठी
app.use(express.static(__dirname));

// Gemini API Initialization
const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
    console.warn("⚠️ Warning: GEMINI_API_KEY is missing in process.env!");
}
const ai = new GoogleGenAI({ apiKey: apiKey || '' });

// Root Route: index.html उघडण्यासाठी
app.get('/', (req, res) => {
    res.sendFile(path.resolve(__dirname, 'index.html'));
});

// API Route: Technical Interview AI
app.post('/api/chat', async (req, res) => {
    try {
        const { history = [], domain = 'Java Enterprise', difficulty = 'Mid', userAnswer = '' } = req.body;

        const systemPrompt = `You are a senior tech interviewer conducting a ${difficulty}-level interview for ${domain}.
Evaluate the candidate's last answer with concise constructive feedback, ask the next relevant technical question or scenario, and calculate real-time scores (0-100) for technical depth, communication clarity, and problem solving.
Return ONLY valid JSON format in the following structure:
{
  "reply": "Your feedback and next technical question here",
  "evaluation": {
    "technicalDepth": 88,
    "communicationClarity": 92,
    "problemSolving": 85,
    "tip": "Short constructive live feedback tip"
  }
}`;

        let contents = [];

        if (Array.isArray(history) && history.length > 0) {
            contents = history.map(item => ({
                role: (item.role === 'model' || item.role === 'assistant') ? 'model' : 'user',
                parts: [{ text: item.parts?.[0]?.text || item.content || '' }]
            }));
        }

        if (userAnswer) {
            contents.push({
                role: 'user',
                parts: [{ text: userAnswer }]
            });
        }

        if (contents.length === 0) {
            contents.push({
                role: 'user',
                parts: [{ text: `Hello, I am ready for my ${difficulty}-level ${domain} interview. Please ask the first question.` }]
            });
        }

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: contents,
            config: {
                systemInstruction: systemPrompt,
                responseMimeType: 'application/json'
            }
        });

        const rawText = response.text;
        const data = JSON.parse(rawText);
        res.json(data);

    } catch (error) {
        console.error("Express / Gemini Error:", error);
        res.status(500).json({
            error: true,
            reply: "That was a good explanation! Building on that, how would you handle database transaction management and fault tolerance in this setup?",
            evaluation: {
                technicalDepth: 82,
                communicationClarity: 88,
                problemSolving: 84,
                tip: "Focus on ACID properties and error-handling strategies."
            }
        });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 SkillTest AI Server running on http://localhost:${PORT}`);
});