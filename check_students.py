import os
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import random

# 1. SETUP & CONNECTION
load_dotenv()
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["chatbot_ai_app"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

# 2. WIPE EVERYTHING (Clean Slate)
print("\n🔥 Wiping Database (Students, Subjects, Marks, Presence)...")
# Deleting older test data
db.students.delete_many({})
db.subjects.delete_many({})
db.marks.delete_many({})
db.presence.delete_many({})
db.document_requests.delete_many({})
db.quizzes.delete_many({})
print("✅ Database cleaned.")

# 3. DEFINE SUBJECTS FOR YOUR 4 MAJORS
print("\n📚 Creating Subjects for AI, CCV, CS, GL...")

# We assume these are Year 4 specializations
YEAR_LEVEL = "4" 

all_subjects = [
    # --- AI (Artificial Intelligence) ---
    {
        "name": "Machine Learning", "major": "AI", "year": YEAR_LEVEL,
        "weights": { "cc": 20, "labs": 20, "projects": 10 },
        "columns": [{"id": "lab1", "name": "Lab KNN", "type": "lab"}, {"id": "proj1", "name": "Kaggle", "type": "project"}]
    },
    {
        "name": "Deep Learning", "major": "AI", "year": YEAR_LEVEL,
        "weights": { "cc": 25, "labs": 25, "projects": 0 },
        "columns": [{"id": "lab1", "name": "Lab CNN", "type": "lab"}]
    },

    # --- CCV (Cloud Computing & Virtualization) ---
    {
        "name": "Cloud Architecture", "major": "CCV", "year": YEAR_LEVEL,
        "weights": { "cc": 30, "labs": 20, "projects": 0 },
        "columns": [{"id": "lab1", "name": "AWS Setup", "type": "lab"}]
    },
    {
        "name": "Virtualization (Docker/K8s)", "major": "CCV", "year": YEAR_LEVEL,
        "weights": { "cc": 15, "labs": 15, "projects": 20 },
        "columns": [{"id": "proj1", "name": "K8s Cluster", "type": "project"}]
    },

    # --- CS (Cyber Security) ---
    {
        "name": "Ethical Hacking", "major": "CS", "year": YEAR_LEVEL,
        "weights": { "cc": 20, "labs": 30, "projects": 0 },
        "columns": [{"id": "lab1", "name": "Pentest Lab", "type": "lab"}, {"id": "lab2", "name": "CTF", "type": "lab"}]
    },
    {
        "name": "Cryptography", "major": "CS", "year": YEAR_LEVEL,
        "weights": { "cc": 40, "labs": 10, "projects": 0 },
        "columns": [{"id": "lab1", "name": "RSA Algo", "type": "lab"}]
    },

    # --- GL (Génie Logiciel) ---
    {
        "name": "Advanced Java/Spring", "major": "GL", "year": YEAR_LEVEL,
        "weights": { "cc": 20, "labs": 10, "projects": 20 },
        "columns": [{"id": "proj1", "name": "E-Commerce App", "type": "project"}]
    },
    {
        "name": "DevOps & CI/CD", "major": "GL", "year": YEAR_LEVEL,
        "weights": { "cc": 20, "labs": 30, "projects": 0 },
        "columns": [{"id": "lab1", "name": "Jenkins Pipeline", "type": "lab"}]
    }
]

db.subjects.insert_many(all_subjects)
print(f"✅ Created {len(all_subjects)} subjects.")


# 4. CREATE STUDENTS FOR EACH MAJOR
print("\n🎓 Creating Students...")

hashed_pw = generate_password_hash("123456")

students_data = [
    # AI
    {"name": "Ahmed AI", "email": "ahmed@uir.ac.ma", "major": "AI"},
    {"name": "Sofia AI", "email": "sofia@uir.ac.ma", "major": "AI"},

    # CCV
    {"name": "Omar CCV", "email": "omar@uir.ac.ma", "major": "CCV"},
    {"name": "Rania CCV", "email": "rania@uir.ac.ma", "major": "CCV"},

    # CS
    {"name": "Hassan CS", "email": "hassan@uir.ac.ma", "major": "CS"},
    {"name": "Leila CS",  "email": "leila@uir.ac.ma",  "major": "CS"},

    # GL
    {"name": "Mehdi GL", "email": "mehdi@uir.ac.ma", "major": "GL"},
    {"name": "Yasmine GL", "email": "yasmine@uir.ac.ma", "major": "GL"}
]

for s in students_data:
    student_doc = {
        "email": s["email"],
        "password": hashed_pw,
        "full_name": s["name"],
        "role": "student",
        "major": s["major"],
        "year": 4, # Matches the subjects
        "has_scholarship": random.choice([True, False]),
        "is_graduated": False,
        "groups": { "td": f"G{random.randint(1,2)}", "tp": f"G{random.randint(1,2)}A" }
    }
    db.students.insert_one(student_doc)
    print(f"   + Created: {s['name']} ({s['major']})")

print("\n🎉 SETUP COMPLETE! Test Accounts:")
print("-------------------------------------------------------")
print("🤖 AI:   ahmed@uir.ac.ma   / 123456")
print("☁️ CCV:  omar@uir.ac.ma    / 123456")
print("🔒 CS:   hassan@uir.ac.ma  / 123456")
print("💻 GL:   mehdi@uir.ac.ma   / 123456")
print("-------------------------------------------------------")