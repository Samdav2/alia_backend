import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

async def summarize_text(text: str) -> str:
    """Summarizes academic text into bullet points."""
    if not model:
        return "Gemini API key not configured. Summary unavailable."

    prompt = f"""
    You are an expert tutor in the Agentic LMS.
    Summarize the following academic text into 5 simple bullet points suitable for a first-year student.

    Text:
    {text}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

async def generate_adaptive_question(topic: str, current_score: int) -> str:
    """Generates a question based on user's current score/difficulty."""
    if not model:
        return "Gemini API key not configured. Question unavailable."

    difficulty = "easy"
    if current_score > 70:
        difficulty = "hard"
    elif current_score > 40:
        difficulty = "medium"

    prompt = f"""
    You are an Assessment Agent in the Agentic LMS.
    The student is studying the topic: "{topic}".
    Their current score is {current_score} out of 100, indicating a {difficulty} level of understanding.

    Generate a multiple-choice question at a {difficulty} level.
    Provide the question, 4 options (A, B, C, D), and the correct answer in JSON format.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating question: {str(e)}"
