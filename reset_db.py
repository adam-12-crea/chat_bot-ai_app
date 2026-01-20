from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/chatbot_ai_app")
client = MongoClient(MONGO_URI)
db = client["chatbot_ai_app"]

def reset_marks():
    print("🗑️  Deleting all marks...")
    result = db.marks.delete_many({})
    print(f"✅ Deleted {result.deleted_count} marks. Database is clean.")

if __name__ == "__main__":
    reset_marks()