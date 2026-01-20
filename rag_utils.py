import os
import time
import pypdf
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot_ai_app"]

# --- THIS FUNCTION WAS MISSING OR NOT EXPORTED ---
def extract_text_from_pdf(file_storage):
    """Extracts text from a Flask FileStorage object (PDF)."""
    try:
        reader = pypdf.PdfReader(file_storage)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        print(f"❌ PDF Read Error: {e}")
        return None

def index_document(file_storage, filename, session_id):
    """Saves a PDF text into the database linked to a Session ID."""
    print(f"🔍 Indexing: {filename} for Session: {session_id}")
    
    # We use the function above to get the text
    text_content = extract_text_from_pdf(file_storage)
    
    if not text_content:
        return False
    
    try:
        db.materials.insert_one({
            "session_id": session_id,
            "title": filename,
            "text_content": text_content,
            "uploaded_at": time.time(),
            "type": "User Upload"
        })
        print(f"✅ File saved successfully.")
        return True
    except Exception as e:
        print(f"❌ Database Insert Error: {e}")
        return False

def search_database(query, session_id):
    """Searches for text inside files belonging to this Session."""
    # Search logic...
    filter_query = {
        "$or": [
            {"uploaded_by": "System"},
            {"session_id": session_id},
            {"session_id": "GLOBAL"} # Include Quizzes
        ]
    }
    
    try:
        # 1. Keyword Search
        keywords = [w.lower() for w in query.split() if len(w) > 3]
        if not keywords: return ""

        materials = db.materials.find(filter_query)
        results = []
        
        for mat in materials:
            score = 0
            content = mat.get('text_content', '').lower()
            for k in keywords:
                if k in content: score += 1
            
            if score > 0:
                snippet = mat['text_content'][:1000]
                results.append(f"SOURCE ({mat.get('title')}): {snippet}...")
        
        if not results: return ""
        return "\n\n".join(results[:2])

    except Exception as e:
        print(f"❌ Search Error: {e}")
        return ""