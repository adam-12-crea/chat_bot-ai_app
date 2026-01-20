import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Setup Connection
load_dotenv()
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["chatbot_ai_app"]
    print("✅ Connected to Database")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

def setup_academic_data():
    print("🔄 Resetting Academic Data (Subjects & Groups)...")
    
    # Optional: Clear existing collections to prevent duplicates
    db.subjects.delete_many({})
    db.groups.delete_many({})

    # ==========================================
    # DATA DEFINITION (Based on your prompt)
    # ==========================================
    
    faculty = "ESIN"
    department = "College of Engineering et Architecture"
    
    curriculum_data = [
        {
            "major": "AI",
            "year": 4,
            "semester": 7,
            "groups_tp": ["TPA", "TPB", "TPC", "TPD", "TPE"],
            "groups_td": ["TDA", "TDB", "TDC", "TDD"],
            "subjects": [
                {"name": "Anglais", "types": ["TD"], "hours": "2h"},
                {"name": "Data Security", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Machine Learning", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Artificial Intelligence", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "NoSQL Databases", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Cloud Foundations & Virtualization", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Advanced Web Development", "types": ["CM", "TP"], "hours": "2h+2h"}
            ]
        },
        {
            "major": "CCV",
            "year": 4,
            "semester": 7,
            "groups_tp": ["TPA"], # Only one group
            "groups_td": ["TDA"], # Only one group
            "subjects": [
                {"name": "Anglais", "types": ["TD"], "hours": "2h"},
                {"name": "Internet of Things", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "NoSQL Databases", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "SDN & Network Softwarization", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Cloud Foundations & Virtualization", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Parallel Programming", "types": ["CM", "TP"], "hours": "2h+2h"}
            ]
        },
        {
            "major": "CS",
            "year": 4,
            "semester": 7,
            "groups_tp": ["TPA", "TPB", "TPC", "TPD", "TPE"],
            "groups_td": ["TDA", "TDB", "TDC", "TDD"],
            "subjects": [
                {"name": "Anglais", "types": ["TD"], "hours": "2h"},
                {"name": "SDN & Network Softwarization", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Cloud Foundations & Virtualization", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Parallel Programming", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Artificial Intelligence", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Ethical Hacking and Defense", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Applied Cryptography & Blockchain", "types": ["CM", "TP"], "hours": "2h+2h"}
            ]
        },
        {
            "major": "GL",
            "year": 4,
            "semester": 7,
            # Assuming GL has standard groups since not specified, defaulting to large structure
            "groups_tp": ["TPA", "TPB", "TPC", "TPD"], 
            "groups_td": ["TDA", "TDB", "TDC"],
            "subjects": [
                {"name": "Distributed Algorithms and Architectures", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Design Patterns", "types": ["TP"], "hours": "2h"}, # TP Only
                {"name": "Artificial Intelligence", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Anglais", "types": ["TD"], "hours": "2h"},
                {"name": "Internet of Things", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Advanced Software Process", "types": ["CM", "TP"], "hours": "2h+2h"},
                {"name": "Advanced Web Development", "types": ["CM", "TP"], "hours": "2h+2h"}
            ]
        }
    ]

    # ==========================================
    # INSERTION LOGIC
    # ==========================================

    for track in curriculum_data:
        print(f"📂 Processing {track['major']} - Year {track['year']}...")

        # 1. Insert Groups
        for g_tp in track['groups_tp']:
            db.groups.insert_one({
                "name": g_tp,
                "type": "TP",
                "major": track['major'],
                "year": track['year'],
                "department": department
            })
        
        for g_td in track['groups_td']:
            db.groups.insert_one({
                "name": g_td,
                "type": "TD",
                "major": track['major'],
                "year": track['year'],
                "department": department
            })

        # 2. Insert Subjects
        for sub in track['subjects']:
            db.subjects.insert_one({
                "name": sub['name'],
                "types": sub['types'], # e.g. ["CM", "TP"]
                "major": track['major'],
                "year": track['year'],
                "semester": track['semester'],
                "hours": sub['hours'],
                "department": department,
                "faculty": faculty
            })

    print("\n✅ Database populated successfully!")
    print("👉 Collections updated: 'subjects', 'groups'")

if __name__ == "__main__":
    setup_academic_data()