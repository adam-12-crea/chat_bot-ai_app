import os
import time
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

# Connect
client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot_ai_app"]

def init_db():
    print("🗑️  Clearing old data...")
    db.users.drop()
    db.materials.drop()
    db.chat_logs.drop()

    print("👥 Creating Users...")
    users = [
        {
            "full_name": "Sarah Student",
            "email": "student@test.com",
            "password": generate_password_hash("password123"),
            "role": "student",
            "created_at": time.time()
        },
        {
            "full_name": "Prof. Walter White",
            "email": "teacher@test.com",
            "password": generate_password_hash("password123"),
            "role": "teacher",
            "created_at": time.time()
        },
        {
            "full_name": "System Admin",
            "email": "admin@test.com",
            "password": generate_password_hash("password123"),
            "role": "admin",
            "created_at": time.time()
        }
    ]
    db.users.insert_many(users)

    print("📚 Adding Sample Course Material...")
    db.materials.insert_one({
        "title": "Course Syllabus - CS101",
        "type": "Syllabus",
        "text_content": "CS101 Introduction to Python. Grading: 40% Final Exam, 30% Midterm, 30% Projects. Professor: Walter White. Office: Building C, Room 304.",
        "uploaded_by": "System",
        "uploaded_at": time.time()
    })

    print("✅ Database Initialized!")
    print("👉 Login with: student@test.com / password123")

if __name__ == "__main__":
    init_db()