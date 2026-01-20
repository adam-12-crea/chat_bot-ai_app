import os
from datetime import datetime
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

# 1. SETUP
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))

# Database Connection
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["chatbot_ai_app"]
except Exception as e:
    print(f"❌ Chatbot DB Error: {e}")

# 2. CHECK API KEY
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("⚠️ CRITICAL ERROR: GOOGLE_API_KEY is missing!")
    print("Please check your .env file.")
    # Dummy key to prevent immediate crash, but calls will fail
    api_key = "dummy_key"

# Initialize Gemini AI
llm = ChatGoogleGenerativeAI(
    model="gemma-3-1b-it", # Using the Flash model as requested
    temperature=0.7,
    google_api_key=api_key,
    convert_system_message_to_human=True # Helper for some Gemini versions
)

# ==============================================================================
#                                HELPER: GET TEACHERS
# ==============================================================================

def get_staff_context():
    """
    Fetches all teachers/admins from MongoDB and formats them as a text string.
    """
    try:
        staff_members = list(db.staff.find({}, {"full_name": 1, "teaching_assignments": 1}))
        
        if not staff_members:
            return "No staff information available."

        text = "### UNIVERSITY STAFF DIRECTORY ###\n"
        for staff in staff_members:
            name = staff.get('full_name', 'Unknown')
            
            subjects = set()
            assignments = staff.get('teaching_assignments', [])
            
            if assignments:
                for assignment in assignments:
                    sub_name = assignment.get('subject', '')
                    sub_type = assignment.get('type', '')
                    if sub_name:
                        subjects.add(f"{sub_name} ({sub_type})")
            
            subjects_str = ", ".join(subjects) if subjects else "General Staff"
            text += f"- Name: {name} | Teaches: {subjects_str}\n"
        
        return text
    except Exception as e:
        print(f"Error fetching staff context: {e}")
        return "Error retrieving staff information."

# ==============================================================================
#                                MAIN CHAT FUNCTION
# ==============================================================================

def get_ai_response(user_message, session_id, user_id=None):
    if api_key == "dummy_key":
        return "⚠️ Error: Google API Key is missing. Please check your .env file."

    # 1. Fetch Chat History
    history = []
    if session_id:
        convo = db.conversations.find_one({"session_id": session_id})
        if convo:
            for msg in convo.get('messages', [])[-10:]:
                history.append(HumanMessage(content=msg['user']))
                history.append(AIMessage(content=msg['ai']))

    # 2. Fetch Dynamic Context (Teachers)
    staff_info = get_staff_context()
    
    # 3. Construct System Prompt
    # Gemini handles SystemMessages, but sometimes prefers them merged.
    # LangChain handles this automatically with the ChatGoogleGenerativeAI class.
    system_instruction = f"""
    You are a helpful University AI Assistant.
    
    ### KNOWLEDGE BASE:
    {staff_info}
    
    ### INSTRUCTIONS:
    - Use the knowledge base above to answer questions about teachers and subjects.
    - If the user asks "Who teaches X?", look for the subject in the directory.
    - Be polite, concise, and helpful.
    - If you don't know the answer, strictly say "I don't have that information."
    """

    messages = [SystemMessage(content=system_instruction)] + history + [HumanMessage(content=user_message)]

    # 4. Generate Response
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"I'm having trouble connecting to Gemini right now. Error: {e}"

def generate_chat_title(first_message, ai_response):
    if api_key == "dummy_key": return "New Chat"
    try:
        prompt = f"Summarize this conversation start into a short title (max 5 words):\nUser: {first_message}\nAI: {ai_response}"
        return llm.invoke([HumanMessage(content=prompt)]).content.strip().replace('"', '')
    except:
        return "New Chat"