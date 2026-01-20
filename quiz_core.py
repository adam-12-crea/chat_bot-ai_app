import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# 1. SETUP
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️ GOOGLE_API_KEY missing in .env")

# Use the model you specified
# Note: If 'gemini-2.5-flash' throws an error, try 'gemini-1.5-flash'
try:
    model = genai.GenerativeModel('gemma-3-1b-it')
except:
    model = genai.GenerativeModel('gemma-3-1b-it')

def clean_json_response(text):
    """
    Cleans Gemini response to ensure valid JSON.
    Removes Markdown (```json ... ```) and extra text.
    """
    try:
        # Remove Markdown backticks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```', '', text)
        
        # Extract content between first { and last }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            return text[start:end+1]
        return text.strip()
    except:
        return text

def get_mock_quiz(subject):
    """Fallback if AI fails."""
    return {
        "subject": subject,
        "questions": [
            {
                "id": "1",
                "question": f"Question de secours sur {subject} ?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "hint": "L'IA n'a pas pu générer le quiz.",
                "explanation": "Ceci est un mode hors ligne."
            }
        ]
    }

def generate_quiz_ai(subject, difficulty, language):
    """
    Generates a quiz using Google Gemini.
    """
    if not api_key:
        return get_mock_quiz(subject)

    prompt = f"""
    Act as a professional Quiz Generator API.
    
    Task: Create a multiple-choice quiz.
    - Subject: "{subject}"
    - Difficulty: {difficulty}
    - Language: {language}
    - Question Count: 5
    
    OUTPUT FORMAT REQUIREMENTS:
    1. Return ONLY raw JSON. No markdown, no intro text.
    2. Structure:
    {{
        "subject": "{subject}",
        "questions": [
            {{
                "id": "1",
                "question": "Question text?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "Exact string of correct option",
                "hint": "Helpful hint",
                "explanation": "Why it is correct"
            }}
        ]
    }}
    """

    try:
        # Call Gemini
        response = model.generate_content(prompt)
        
        # Clean and Parse
        cleaned_text = clean_json_response(response.text)
        quiz_data = json.loads(cleaned_text)

        # Validate Structure
        if "questions" not in quiz_data:
            raise ValueError("Missing 'questions' key")

        # Ensure IDs are strings
        for i, q in enumerate(quiz_data['questions']):
            q['id'] = str(i)

        return quiz_data

    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return get_mock_quiz(subject)

def grade_quiz_ai(quiz_content, user_answers):
    """
    Grades the quiz (Logic remains the same, no AI needed here).
    """
    questions = quiz_content.get('questions', []) if isinstance(quiz_content, dict) else quiz_content
    score = 0
    corrections = []

    for q in questions:
        q_id = str(q.get('id'))
        user_ans = (user_answers.get(q_id) or "").strip()
        correct_ans = (q.get('correct_answer') or "").strip()

        is_correct = (user_ans == correct_ans)
        if is_correct: score += 1

        corrections.append({
            "question_id": q_id,
            "correct_answer": correct_ans,
            "explanation": q.get('explanation', '')
        })

    total = len(questions)
    percentage = round((score / total) * 100) if total > 0 else 0

    return {
        "score": percentage,
        "total": total,
        "corrections": corrections
    }