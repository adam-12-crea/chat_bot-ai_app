import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Setup
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))

client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbot_ai_app"]

print("\n🎓 --- DEMO STUDENT LOGINS ---")
print("Password for all: 123456\n")

majors = ["AI", "CCV", "CS", "GL"]

for major in majors:
    student = db.students.find_one({"major": major})
    if student:
        print(f"[{major}]")
        print(f"Name:  {student['full_name']}")
        print(f"Email: {student['email']}")
        print(f"Group: {student['groups']['tp']}")
        print("-" * 30)
    else:
        print(f"[{major}] No student found.")

print("\n")