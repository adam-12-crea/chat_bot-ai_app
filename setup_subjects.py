import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["chatbot_ai_app"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

# Subjects Configuration
subjects_data = [
    {
        "name": "Machine Learning",
        "major": "AI",
        "year": "4",
        "weights": { "cc": 20, "labs": 20, "projects": 10 },
        "columns": [
            {"id": "lab1", "name": "Lab KNN", "type": "lab"},
            {"id": "proj1", "name": "Projet Kaggle", "type": "project"}
        ]
    },
    {
        "name": "Deep Learning",
        "major": "AI",
        "year": "4",
        "weights": { "cc": 25, "labs": 25, "projects": 0 },
        "columns": [{"id": "lab1", "name": "Lab CNN", "type": "lab"}]
    },
    {
        "name": "Big Data Analytics",
        "major": "AI",
        "year": "4",
        "weights": { "cc": 15, "labs": 15, "projects": 20 },
        "columns": [{"id": "lab1", "name": "Spark", "type": "lab"}]
    }
]

print("🔄 Updating Subjects...")
for sub in subjects_data:
    db.subjects.update_one(
        {"name": sub["name"], "major": sub["major"], "year": sub["year"]}, 
        {"$set": sub}, 
        upsert=True
    )
    print(f"   -> Configured: {sub['name']}")