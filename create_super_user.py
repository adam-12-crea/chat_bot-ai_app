import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

# 1. Connect to DB
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["chatbot_ai_app"]
    print("✅ Connected to Database")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

def create_dual_role_user():
    print("\n--- CREATE DUAL-ROLE USER ---")
    email = input("Enter Email: ")
    full_name = input("Enter Full Name: ")
    
    # 2. Ask for TWO passwords
    print("\n🔐 PASSWORD 1 (For TEACHER Access)")
    pass_teacher = input("Set Teacher Password: ")
    
    print("\n🔐 PASSWORD 2 (For ADMIN Access)")
    pass_admin = input("Set Admin Password: ")

    if not email or not pass_teacher or not pass_admin:
        print("❌ Error: All fields required.")
        return

    # 3. Create the special user document
    # Note: We do NOT use the standard 'password' or 'role' fields here.
    # We use specific fields that the login logic will look for.
    user_data = {
        "email": email,
        "full_name": full_name,
        "password_teacher": generate_password_hash(pass_teacher),
        "password_admin": generate_password_hash(pass_admin),
        "is_dual_role": True  # Flag to help identify this user type
    }

    # 4. Insert into DB (Upsert to prevent duplicates)
    db.users.update_one(
        {"email": email},
        {"$set": user_data},
        upsert=True
    )
    
    print(f"\n✅ SUCCESS! User '{email}' created.")
    print(f"👉 Log in with '{pass_teacher}' -> Goes to Teacher Dashboard")
    print(f"👉 Log in with '{pass_admin}'   -> Goes to Admin Panel")

if __name__ == "__main__":
    create_dual_role_user()