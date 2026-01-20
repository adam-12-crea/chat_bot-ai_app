import os
import time
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

# Connect to Database
client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot_ai_app"]

def add_specific_student():
    # Student Data Object
    new_student = {
        # Essential fields for the App's Login system
        "full_name": "Amine Lassri", 
        "email": "amine.lassri@uir.ac.ma",
        "password": generate_password_hash("Gor67563"), # Securely hashed
        "role": "student",
        
        # Specific Student Details
        "first_name": "Amine",
        "last_name": "Lassri",
        "student_id": "119747",
        "major": "Computer Engineering-AI",
        "age": 21,
        "semester_of_study": 7,
        "gender": "M",
        "has_a_subscriptions": True,
        "subscriptions": "transport",
        "due_payment": 0.0,
        "emergency_contact": "062868954",
        "has_a_scholarship": False,
        "clubs": [],
        "department": "ING",
        "faculty": "ESIN",
        "created_at": time.time()
    }

    # Check if user already exists to avoid duplicates
    if db.users.find_one({"email": new_student["email"]}):
        print("❌ Error: A student with this email already exists.")
    else:
        db.users.insert_one(new_student)
        print(f"✅ Student '{new_student['full_name']}' created successfully!")

if __name__ == "__main__":
    add_specific_student()