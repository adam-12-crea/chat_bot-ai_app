import os
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import random

# 1. SETUP
load_dotenv()
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["chatbot_ai_app"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

# 2. DELETE OLD STUDENT DATA (Keeping Staff & Subjects)
print("\n🔥 Wiping Student Data...")

# Delete all students
res_s = db.students.delete_many({})
print(f"   - Removed {res_s.deleted_count} students.")

# Delete related collections (Clean slate)
db.marks.delete_many({})
db.presence.delete_many({})
db.document_requests.delete_many({})
db.conversations.delete_many({}) # Optional: Remove student chats
db.quizzes.delete_many({})

print("✅ Cleanup Complete. (Staff and Subjects were NOT touched)")

# 3. CREATE NEW CORRECT STUDENTS
print("\n✨ Creating New Students for AI - Year 4...")

# Configuration for AI Year 4 (Must match setup_subjects.py)
MAJOR = "AI"
YEAR = 4

# List of students to create
students_to_create = [
    {
        "full_name": "Test Student (You)", 
        "email": "student@uir.ac.ma", 
        "scholarship": True,
        "graduated": False
    },
    {
        "full_name": "Alice Martin", 
        "email": "alice@uir.ac.ma", 
        "scholarship": False,
        "graduated": False
    },
    {
        "full_name": "Bob Dupont", 
        "email": "bob@uir.ac.ma", 
        "scholarship": True,
        "graduated": False
    },
    {
        "full_name": "Charlie Ancienne", 
        "email": "charlie@uir.ac.ma", 
        "scholarship": False,
        "graduated": True # Test for diploma documents
    }
]

# Common Password Hash
hashed_pw = generate_password_hash("123456")

for s in students_to_create:
    student_doc = {
        "email": s["email"],
        "password": hashed_pw,
        "full_name": s["full_name"],
        "role": "student",
        
        # CRITICAL: These must match your Subjects
        "major": MAJOR, 
        "year": YEAR,
        
        # For Document Requests
        "has_scholarship": s["scholarship"],
        "is_graduated": s["graduated"],
        
        # For Groups (TP/TD)
        "groups": {
            "td": random.choice(["G1", "G2"]),
            "tp": random.choice(["G1A", "G1B", "G2A", "G2B"])
        }
    }
    
    db.students.insert_one(student_doc)
    print(f"   + Created: {s['full_name']} ({s['email']})")

print("\n🎉 Done! You can now login with:")
print("   Email: student@uir.ac.ma")
print("   Pass:  123456")