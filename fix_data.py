import os
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# 1. Connect
load_dotenv()
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["chatbot_ai_app"]
except:
    print("❌ Check .env MONGO_URI")
    exit()

# 2. Check Subjects
count = db.subjects.count_documents({"major": "AI", "year": "4"})
if count == 0:
    print("❌ No subjects found for AI Year 4. Run 'setup_subjects.py' first!")
    exit()
print(f"✅ Found {count} subjects for AI Year 4.")

# 3. Fix Student Profile
# REPLACE THIS with the email you use to log in
TARGET_EMAIL = "student@uir.ac.ma" 

print(f"🔄 Syncing student {TARGET_EMAIL} to AI Year 4...")

# Update user to ensure they see the subjects
result = db.students.update_one(
    {"email": TARGET_EMAIL},
    {
        "$set": {
            "major": "AI",      # MATCHES SUBJECTS
            "year": 4,          # MATCHES SUBJECTS
            "role": "student"
        }
    }
)

if result.matched_count > 0:
    print("✅ Success! Student synced. Refresh notes.html.")
else:
    print("⚠️ Student not found. Creating test student...")
    db.students.insert_one({
        "email": TARGET_EMAIL,
        "password": generate_password_hash("123456"),
        "full_name": "Test AI Student",
        "major": "AI",
        "year": 4,
        "role": "student"
    })
    print("✅ Created: student@uir.ac.ma / 123456")