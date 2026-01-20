import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Use the working model
model = genai.GenerativeModel('gemma-3-1b-it') 

def summarize_content(text, summary_type="bullet_points"):
    """
    Summarizes text based on the requested style.
    summary_type options: 'bullet_points', 'paragraph', 'concise'
    """
    
    # Custom instructions based on type
    style_instruction = ""
    if summary_type == "bullet_points":
        style_instruction = "Format: A structured list of bullet points with bold headers for key topics."
    elif summary_type == "concise":
        style_instruction = "Format: A very short, high-level executive summary (max 3-4 sentences)."
    else:
        style_instruction = "Format: A coherent, well-written paragraph explaining the content."

    prompt = f"""
    You are an expert University Note-Taker.
    
    TASK:
    Summarize the following content for a student who needs to study for an exam.
    {style_instruction}
    
    RULES:
    1. Ignore irrelevant text (like page numbers, headers).
    2. Focus on Definitions, Dates, and Core Concepts.
    3. Use **bold** for important terms.
    4. Keep it clear and readable.
    
    CONTENT TO SUMMARIZE:
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Summary Error: {e}")
        return "Désolé, je n'ai pas pu résumer ce contenu. (Erreur AI)"