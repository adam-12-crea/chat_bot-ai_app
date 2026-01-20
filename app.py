import os
import time
import uuid
import json
import re
import random
import pandas as pd  # Required for Excel Import
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from dotenv import load_dotenv

# --- CUSTOM MODULES ---
try:
    from chatbot_core import get_ai_response, generate_chat_title
    from quiz_core import generate_quiz_ai, grade_quiz_ai
    from summary_core import summarize_content
    from planner_core import generate_study_plan
    from rag_utils import index_document, extract_text_from_pdf
except ImportError:
    print("⚠️ AI Modules not found. AI features will not work.")

# 1. SETUP & CONFIGURATION
base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, ".env"))

app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))

app.secret_key = "university_secret_key_123"

# --- SETUP UPLOAD FOLDERS ---
UPLOAD_FOLDER_EDT = os.path.join(base_dir, 'static', 'schedules')
UPLOAD_FOLDER_COURSES = os.path.join(base_dir, 'static', 'courses')
UPLOAD_FOLDER_ADMIN_DOCS = os.path.join(base_dir, 'static', 'admin_docs')
UPLOAD_FOLDER_ANNOUNCEMENTS = os.path.join(base_dir, 'static', 'announcements')

for folder in [UPLOAD_FOLDER_EDT, UPLOAD_FOLDER_COURSES, UPLOAD_FOLDER_ADMIN_DOCS, UPLOAD_FOLDER_ANNOUNCEMENTS]:
    os.makedirs(folder, exist_ok=True)

# --- DATABASE CONNECTION (UPDATED) ---
import certifi  # Add this import at the top if missing

try:
    # 1. Load the URI
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is missing from .env file")

    # 2. Connect with SSL Certificate handling (Fixes Windows/SSL Errors)
    client = MongoClient(
        mongo_uri, 
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000  # Fail fast (5 seconds) if network is down
    )
    
    # 3. Force a connection check immediately
    client.admin.command('ping')
    
    # 4. Define the database
    db = client["chatbot_ai_app"]
    print("✅ Successfully connected to MongoDB Atlas!")

except Exception as e:
    print("\n" + "="*50)
    print(f"❌ CRITICAL DATABASE ERROR: {e}")
    print("="*50 + "\n")
    # Stop the app immediately so you don't get 'NameError' later
    raise SystemExit("Application stopped because Database connection failed.")

# ==============================================================================
#                                HELPER FUNCTIONS
# ==============================================================================

def parse_edt_filename(filename):
    match = re.search(r'EDT-([A-Za-z]+)(\d+)-(.+)\.xlsx?', filename, re.IGNORECASE)
    if match:
        return match.group(1).upper(), match.group(2), match.group(3)
    return None, None, None

def safe_float(value):
    try:
        if value is None or value == "" or value == "-": return 0.0
        return float(value)
    except:
        return 0.0

# ==============================================================================
#                                PAGE ROUTES
# ==============================================================================

@app.route('/')
def home():
    session.clear()
    return render_template('accueil.html')

@app.route('/<page_name>.html')
def serve_page(page_name):
    if page_name == 'accueil':
        session.clear()
        return render_template('accueil.html')

    if page_name in ['signup', 'signin']:
        return render_template(f'{page_name}.html')

    protected_pages = [
        'dashboard', 'assistant', 'quiz', 'quiz-taking', 
        'summary', 'planner', 'cours', 'documents', 'notes', 
        'teacher', 'teacher-presence', 'teacher-upload', 'teacher-ressources', 
        'teacher-rapports', 'teacher-notes', 
        'admin', 'admin-demandes', 'admin-users', 'admin-presence', 'EDT-upload', 'admin-annonce'
    ]
    
    if page_name in protected_pages and 'user_id' not in session:
        return redirect('/signin.html')
    
    role = session.get('role', 'student')
    dashboard_map = {'admin': 'admin.html', 'teacher': 'teacher.html', 'student': 'dashboard.html'}
    
    try:
        return render_template(f'{page_name}.html', 
                               user_name=session.get('name', ''), 
                               dashboard_link=dashboard_map.get(role, 'dashboard.html'),
                               user_role=role)
    except:
        return "Page not found (404)", 404

# ==============================================================================
#                                AUTHENTICATION API
# ==============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    staff_user = db.staff.find_one({"email": email})
    if staff_user:
        if 'password_admin' in staff_user and check_password_hash(staff_user['password_admin'], password):
            session['user_id'] = str(staff_user['_id'])
            session['role'] = 'admin'
            session['name'] = staff_user.get('full_name', 'Admin')
            return jsonify({"success": True, "redirect": "admin.html"})

        pwd_hash = staff_user.get('password_teacher')
        if pwd_hash and check_password_hash(pwd_hash, password):
            session['user_id'] = str(staff_user['_id'])
            session['role'] = 'teacher'
            session['name'] = staff_user.get('full_name', 'Teacher')
            return jsonify({"success": True, "redirect": "teacher.html"})

    student_user = db.students.find_one({"email": email})
    if student_user:
        if check_password_hash(student_user['password'], password):
            session['user_id'] = str(student_user['_id'])
            session['role'] = 'student'
            session['name'] = student_user.get('full_name', 'Student')
            return jsonify({"success": True, "redirect": "dashboard.html"})
    
    return jsonify({"success": False, "error": "Identifiants incorrects"}), 401

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect('/')

# ==============================================================================
#                                ADMIN APIs
# ==============================================================================

@app.route('/api/admin/get_users/<role>', methods=['GET'])
def get_users(role):
    if session.get('role') != 'admin': return jsonify([]), 403
    collection = db.students if role == 'student' else db.staff
    query = {} if role == 'student' else {"password_teacher": {"$exists": True}}
    users = list(collection.find(query))
    for u in users:
        u['_id'] = str(u['_id'])
        u.pop('password', None)
        u.pop('password_teacher', None)
        u.pop('password_admin', None)
    return jsonify(users)

@app.route('/api/admin/add_user', methods=['POST'])
def add_user():
    if session.get('role') != 'admin': return jsonify({"success": False}), 403
    data = request.json
    hashed_pw = generate_password_hash(data.get('password', '123456'))
    
    if data.get('role') == 'student':
        db.students.insert_one({
            "full_name": data.get('full_name'), "email": data.get('email'), "password": hashed_pw,
            "major": data.get('major'), "year": data.get('year'), "role": "student"
        })
    else:
        db.staff.insert_one({
            "full_name": data.get('full_name'), "email": data.get('email'), "password_teacher": hashed_pw,
            "role": "teacher", "department": data.get('major', 'General')
        })
    return jsonify({"success": True})

@app.route('/api/admin/update_user', methods=['POST'])
def update_user():
    if session.get('role') != 'admin': return jsonify({"success": False}), 403
    data = request.json
    role, user_id = data.get('role'), data.get('id')
    updates = {"full_name": data.get('full_name'), "email": data.get('email')}
    if data.get('password'):
        field = "password" if role == 'student' else "password_teacher"
        updates[field] = generate_password_hash(data.get('password'))
    
    if role == 'student':
        updates.update({"major": data.get('major'), "year": data.get('year')})
        db.students.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    else:
        updates["department"] = data.get('major')
        db.staff.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return jsonify({"success": True})

@app.route('/api/admin/delete_user', methods=['POST'])
def delete_user():
    if session.get('role') != 'admin': return jsonify({"success": False}), 403
    collection = db.students if request.json.get('role') == 'student' else db.staff
    collection.delete_one({"_id": ObjectId(request.json.get('id'))})
    return jsonify({"success": True})

@app.route('/api/admin/upload_users', methods=['POST'])
def upload_users_excel():
    if session.get('role') != 'admin': return jsonify({"success": False}), 403
    file = request.files['file']
    role = request.form.get('role')
    if not file: return jsonify({"success": False, "error": "No file"}), 400
    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.lower().str.strip()
        count = 0
        for _, row in df.iterrows():
            email = row.get('email')
            if not email: continue
            password = str(row.get('password', '123456'))
            hashed = generate_password_hash(password)
            if role == 'student':
                user_doc = {
                    "full_name": row.get('name') or row.get('nom'), "email": email, "password": hashed,
                    "major": row.get('major') or row.get('filiere'), "year": row.get('year') or row.get('annee'),
                    "role": "student"
                }
                db.students.update_one({"email": email}, {"$set": user_doc}, upsert=True)
            else:
                user_doc = {
                    "full_name": row.get('name') or row.get('nom'), "email": email, "password_teacher": hashed,
                    "department": row.get('department') or row.get('departement'), "role": "teacher"
                }
                db.staff.update_one({"email": email}, {"$set": user_doc}, upsert=True)
            count += 1
        return jsonify({"success": True, "count": count})
    except Exception as e: return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/post_announcement', methods=['POST'])
def post_announcement():
    if session.get('role') != 'admin': return jsonify({"success": False}), 403
    title, content = request.form.get('title'), request.form.get('content')
    file = request.files.get('file')
    if not title: return jsonify({"success": False, "error": "Title required"}), 400
    
    file_path, file_type = None, None
    if file and file.filename:
        filename = secure_filename(f"{int(time.time())}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER_ANNOUNCEMENTS, filename))
        file_path = f"/static/announcements/{filename}"
        file_type = 'image' if filename.split('.')[-1].lower() in ['jpg', 'png', 'jpeg'] else 'file'

    db.annonces.insert_one({
        "title": title, "content": content, "file_path": file_path, "file_type": file_type,
        "date": time.time(), "author": session.get('name', 'Admin')
    })
    return jsonify({"success": True})

@app.route('/api/admin/upload_edt', methods=['POST'])
def upload_edt():
    if session.get('role') != 'admin': return jsonify({"success": False}), 403
    for f in request.files.getlist('files[]'):
        if f.filename:
            fn = secure_filename(f.filename)
            mj, yr, dr = parse_edt_filename(fn)
            if mj:
                f.save(os.path.join(UPLOAD_FOLDER_EDT, fn))
                db.schedules.insert_one({"filename": fn, "major": mj, "year": yr, "date_range": dr, "upload_date": time.time(), "file_path": f"/static/schedules/{fn}"})
    return jsonify({"success": True})

@app.route('/api/admin/get_global_absences', methods=['GET'])
def get_global_absences():
    if session.get('role') != 'admin': return jsonify([]), 403
    cursor = db.presence.find().sort("date_submitted", -1)
    absences = []
    for sheet in cursor:
        for student in sheet.get('students', []):
            if student.get('status') == 'absent':
                absences.append({
                    "date": datetime.fromtimestamp(sheet['date_submitted']).strftime("%d/%m"), 
                    "student_name": student.get('name'), "subject": sheet.get('subject'), 
                    "group": sheet.get('group'), "teacher": sheet.get('teacher_name')
                })
    return jsonify(absences)

@app.route('/api/admin/get_all_requests', methods=['GET'])
def get_all_requests():
    if session.get('role') != 'admin': return jsonify([])
    reqs = list(db.document_requests.find().sort("request_date", -1))
    return jsonify([{"id": str(r['_id']), "student": r['student_name'], "type": r['doc_type'], "status": r['status'], "date": datetime.fromtimestamp(r['request_date']).strftime("%d/%m")} for r in reqs])

@app.route('/api/admin/process_request', methods=['POST'])
def process_request():
    if session.get('role') != 'admin': return jsonify({"success": False}), 403
    rid = request.form.get('request_id')
    if request.form.get('action') == 'reject':
        db.document_requests.update_one({"_id": ObjectId(rid)}, {"$set": {"status": "rejected", "rejection_reason": request.form.get('reason')}})
    else:
        f = request.files['file']
        fn = secure_filename(f"DOC_{rid}_{f.filename}")
        f.save(os.path.join(UPLOAD_FOLDER_ADMIN_DOCS, fn))
        db.document_requests.update_one({"_id": ObjectId(rid)}, {"$set": {"status": "completed", "file_path": f"/static/admin_docs/{fn}"}})
    return jsonify({"success": True})

# ==============================================================================
#                                TEACHER APIs
# ==============================================================================

@app.route('/api/teacher/get_presence_sessions', methods=['GET'])
def get_teacher_sessions():
    """Returns sessions list + status + year for Presence Page."""
    if session.get('role') not in ['teacher', 'admin']: return jsonify([])
    teacher = db.staff.find_one({"_id": ObjectId(session.get('user_id'))})
    if not teacher: return jsonify([])
    
    assignments = teacher.get('teaching_assignments', [])
    sessions = []
    
    # 1. Fetch Schedules
    schedules = list(db.schedules.find().sort("upload_date", -1).limit(20))
    
    def get_status(sid):
        exists = db.presence.find_one({"session_id": sid})
        if exists: return "postponed" if exists.get('postponed') else "submitted"
        return "pending"

    if not schedules:
        current_week = f"Semaine {datetime.now().strftime('%V')}"
        for assign in assignments:
            groups = ["Promo Entière"] if assign.get('type') == 'CM' else assign.get('groups', [])
            for grp in groups:
                sid = f"mock_{assign.get('subject')}_{assign.get('type')}_{grp}_{current_week}"
                sessions.append({
                    "session_id": sid, "week": current_week, "subject": assign.get('subject'),
                    "type": assign.get('type'), "group": grp, "major": assign.get('major'),
                    "year": 4, 
                    "status": get_status(sid)
                })
    else:
        for sch in schedules:
            sch_mjr = str(sch.get('major','')).upper().strip()
            sch_year = sch.get('year', 4)
            for assign in assignments:
                if str(assign.get('major','')).upper().strip() == sch_mjr:
                    groups = ["Promo Entière"] if assign.get('type') == 'CM' else assign.get('groups', [])
                    for grp in groups:
                        sid = f"{str(sch['_id'])}_{assign.get('subject')}_{assign.get('type')}_{grp}"
                        sessions.append({
                            "session_id": sid, "week": sch.get('date_range'), "subject": assign.get('subject'),
                            "type": assign.get('type'), "group": grp, "major": sch_mjr,
                            "year": sch_year, 
                            "status": get_status(sid)
                        })
    return jsonify(sessions)

@app.route('/api/teacher/get_students_for_session', methods=['POST'])
def get_students_for_session():
    data = request.json
    year_val = data.get('year')
    # Robust year check
    year_query = year_val
    if str(year_val).isdigit(): year_query = {"$in": [str(year_val), int(year_val)]}
    
    query = {"major": data.get('major'), "year": year_query}
    if data.get('group') and data.get('group') != "Promo Entière":
        group_val = data.get('group')
        query["$or"] = [{"groups.tp": group_val}, {"groups.td": group_val}]
        
    students = list(db.students.find(query).sort("full_name", 1))
    return jsonify([{"id": str(s['_id']), "name": s['full_name']} for s in students])

@app.route('/api/teacher/grading_data', methods=['POST'])
def get_teacher_grading_data():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    subject, group, major = data.get('subject'), data.get('group'), data.get('major')
    current_role = "CM" if group == "Promo Entière" else "TP"
    
    sub_config = db.subjects.find_one({"name": subject, "major": major})
    if not sub_config: sub_config = db.subjects.find_one({"name": subject})
    if not sub_config: return jsonify({"error": "Matière introuvable"}), 404

    target_year = sub_config.get('year')
    year_query = {"$in": [str(target_year), int(target_year)]} if str(target_year).isdigit() else target_year
    query = {"major": major, "year": year_query}
    
    if current_role == "TP":
        query["$or"] = [{"groups.tp": group}, {"groups.td": group}]

    students = list(db.students.find(query).sort("full_name", 1))
    student_list = []
    for s in students:
        marks = db.marks.find_one({"student_id": str(s['_id']), "subject_id": str(sub_config['_id'])})
        student_list.append({
            "id": str(s['_id']), "name": s['full_name'], "groups": s.get('groups', {}),
            "marks": marks.get('marks', {}) if marks else {}
        })

    weights = sub_config.get('weights', {'cc': 20, 'labs': 20, 'projects': 10})

    return jsonify({
        "current_role": current_role, 
        "weights": weights,
        "columns": sub_config.get('columns', []),
        "students": student_list,
        "subject_id": str(sub_config['_id'])
    })

@app.route('/api/teacher/save_config', methods=['POST'])
def save_config():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"success": False}), 403
    w = request.json.get('weights', {})
    total = safe_float(w.get('cc')) + safe_float(w.get('labs')) + safe_float(w.get('projects'))
    if total != 50: return jsonify({"success": False, "error": f"Total CC+Labs+Projets doit faire 50%. Actuel: {total}%"}), 400
    db.subjects.update_one({"_id": ObjectId(request.json.get('subject_id'))}, {"$set": {"weights": w}})
    return jsonify({"success": True})

@app.route('/api/teacher/add_column', methods=['POST'])
def add_column():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"success": False}), 403
    d = request.json
    col_id = f"{d.get('type')}_{int(time.time())}"
    db.subjects.update_one({"_id": ObjectId(d.get('subject_id'))}, {"$push": {"columns": {"id": col_id, "name": d.get('name'), "type": d.get('type')}}})
    return jsonify({"success": True})

@app.route('/api/teacher/delete_column', methods=['POST'])
def delete_column():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"success": False}), 403
    d = request.json
    db.subjects.update_one({"_id": ObjectId(d.get('subject_id'))}, {"$pull": {"columns": {"id": d.get('column_id')}}})
    db.marks.update_many({"subject_id": d.get('subject_id')}, {"$unset": {f"marks.{d.get('column_id')}": ""}})
    return jsonify({"success": True})

@app.route('/api/teacher/save_marks', methods=['POST'])
def save_marks():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"success": False}), 403
    d = request.json
    for up in d.get('updates'):
        db.marks.update_one(
            {"student_id": up['student_id'], "subject_id": d.get('subject_id')},
            {"$set": {f"marks.{up['key']}": up['value']}}, upsert=True
        )
    return jsonify({"success": True})

@app.route('/api/teacher/submit_attendance', methods=['POST'])
def submit_attendance():
    data = request.json
    if db.presence.find_one({"session_id": data.get('session_id')}): return jsonify({"success": False, "error": "Duplicate"})
    db.presence.insert_one({
        "session_id": data.get('session_id'), "teacher_id": session.get('user_id'), 
        "teacher_name": session.get('name'), "date_submitted": time.time(),
        "students": data.get('students', []), "postponed": data.get('postponed', False), 
        "subject": data.get('subject'), "type": data.get('type'),
        "group": data.get('group'), "week": data.get('week')
    })
    return jsonify({"success": True})

@app.route('/api/teacher/upload_material', methods=['POST'])
def upload_material():
    if session.get('role') not in ['teacher', 'admin']: return jsonify({"success": False}), 403
    for f in request.files.getlist('files'):
        fn = secure_filename(f.filename)
        save_name = f"{int(time.time())}_{fn}"
        f.save(os.path.join(UPLOAD_FOLDER_COURSES, save_name))
        db.course_materials.insert_one({
            "subject": request.form.get('subject'), "major": request.form.get('major'),
            "category": request.form.get('category'), "filename": fn,
            "file_path": f"/static/courses/{save_name}", "uploaded_by": session.get('user_id'),
            "teacher_name": session.get('name'), "upload_date": time.time(), "file_type": fn.split('.')[-1].lower()
        })
    return jsonify({"success": True})

@app.route('/api/teacher/get_upload_options', methods=['GET'])
def get_upload_opts():
    if session.get('role') not in ['teacher', 'admin']: return jsonify([])
    teacher = db.staff.find_one({"_id": ObjectId(session.get('user_id'))})
    options = []
    seen = set()
    for a in teacher.get('teaching_assignments', []):
        key = f"{a['subject']}|{a['major']}"
        if key not in seen:
            options.append({"subject": a['subject'], "major": a['major']})
            seen.add(key)
    return jsonify(options)

# ==============================================================================
#                                STUDENT APIs
# ==============================================================================

@app.route('/api/student/marks', methods=['GET'])
def get_student_marks():
    if session.get('role') != 'student': return jsonify({})
    uid = session.get('user_id')
    stu = db.students.find_one({"_id": ObjectId(uid)})
    if not stu: return jsonify({})
    
    major = stu.get('major')
    year = str(stu.get('year', '4'))
    results = {"subjects": [], "general_average": 0}
    subs = list(db.subjects.find({"major": major, "year": year}))
    total_avg, count = 0, 0
    
    for sub in subs:
        w = sub.get('weights', {'cc': 20, 'labs': 20, 'projects': 10})
        w_cc = safe_float(w.get('cc', 20))
        w_labs = safe_float(w.get('labs', 20))
        w_proj = safe_float(w.get('projects', 10))

        cols = sub.get('columns', [])
        m_doc = db.marks.find_one({"student_id": uid, "subject_id": str(sub['_id'])})
        raw = m_doc.get('marks', {}) if m_doc else {}
        
        detailed = []
        lab_vals, proj_vals = [], []
        
        for col in cols:
            val = raw.get(col['id'])
            detailed.append({"name": col['name'], "val": val if val is not None else '-'})
            if val is not None and val != "":
                f_val = safe_float(val)
                if col['type'] == 'lab': lab_vals.append(f_val)
                if col['type'] == 'project': proj_vals.append(f_val)
        
        cc = safe_float(raw.get('cc'))
        cf = safe_float(raw.get('cf'))
        
        avg_lab = sum(lab_vals)/len(lab_vals) if lab_vals else 0.0
        avg_proj = sum(proj_vals)/len(proj_vals) if proj_vals else 0.0
        
        grade = (cf * 0.50) + (cc * w_cc/100) + (avg_lab * w_labs/100) + (avg_proj * w_proj/100)
        if sub.get('type') == 'TD': grade = cc
        
        final = round(grade, 2)
        statut = ("V" if final >= 12 else "R") if m_doc else "pending"
        
        results["subjects"].append({
            "name": sub['name'], "columns": detailed, "cc": raw.get('cc', '-'), "cf": raw.get('cf', '-'),
            "final_grade": final if m_doc else "-", "statut": statut, "ratt": raw.get('ratt', '-')
        })
        if m_doc:
            total_avg += final
            count += 1
            
    if count: results["general_average"] = round(total_avg / count, 2)
    else: results["general_average"] = "-"
    
    return jsonify({major: results})

@app.route('/api/student/get_attendance', methods=['GET'])
def get_attendance():
    if session.get('role') != 'student': return jsonify([])
    uid = session.get('user_id')
    cursor = db.presence.find({"students.id": uid})
    stats = {}
    for doc in cursor:
        sub = doc['subject']
        if sub not in stats: stats[sub] = {"subject": sub, "absences": 0, "history": []}
        stu = next((s for s in doc['students'] if s['id'] == uid), None)
        if stu:
            st = str(stu.get('status', '')).lower().strip()
            if st == 'absent': stats[sub]['absences'] += 2
            stats[sub]['history'].append({"date": datetime.fromtimestamp(doc['date_submitted']).strftime("%d/%m"), "status": st, "type": doc.get('type')})
    return jsonify(list(stats.values()))

@app.route('/api/student/get_materials/<subject>', methods=['GET'])
def get_materials(subject):
    if session.get('role') != 'student': return jsonify([])
    stu = db.students.find_one({"_id": ObjectId(session.get('user_id'))})
    mats = list(db.course_materials.find({"subject": subject, "major": stu.get('major')}).sort("upload_date", -1))
    return jsonify([{"filename": m['filename'], "link": m['file_path'], "category": m.get('category'), "date": datetime.fromtimestamp(m['upload_date']).strftime("%d/%m"), "teacher": m['teacher_name'], "type": m['file_type']} for m in mats])

@app.route('/api/student/subjects', methods=['GET'])
def get_student_subjects():
    if session.get('role') != 'student': return jsonify([])
    s = db.students.find_one({"_id": ObjectId(session.get('user_id'))})
    subs = list(db.subjects.find({"major": s.get('major')}))
    return jsonify([sub['name'] for sub in subs])

@app.route('/api/student/get_announcements', methods=['GET'])
def get_announcements():
    announcements = list(db.annonces.find({}, {'_id': 0}).sort("date", -1))
    for a in announcements: a['date_str'] = datetime.fromtimestamp(a['date']).strftime('%d/%m/%Y')
    return jsonify(announcements)

@app.route('/api/get_schedules', methods=['GET'])
def get_schedules():
    query = {}
    if session.get('role') == 'student':
        s = db.students.find_one({"_id": ObjectId(session['user_id'])})
        query = {"major": s.get('major'), "year": str(s.get('year'))}
    scheds = list(db.schedules.find(query).sort("upload_date", -1))
    return jsonify([{"title": f"EDT {s['major']}{s['year']} ({s['date_range']})", "link": s['file_path']} for s in scheds])

@app.route('/api/student/request_document', methods=['POST'])
def request_document():
    if session.get('role') != 'student': return jsonify({"success": False}), 403
    db.document_requests.insert_one({
        "student_id": session.get('user_id'), "student_name": session.get('name'),
        "doc_type": request.json.get('type'), "details": request.json.get('details'),
        "status": "pending", "request_date": time.time()
    })
    return jsonify({"success": True})

@app.route('/api/student/my_requests', methods=['GET'])
def get_my_requests():
    reqs = list(db.document_requests.find({"student_id": session.get('user_id')}).sort("request_date", -1))
    return jsonify([{"id": str(r['_id']), "type": r['doc_type'], "status": r['status'], "date": datetime.fromtimestamp(r['request_date']).strftime("%d/%m"), "file": r.get('file_path')} for r in reqs])

@app.route('/api/student/info', methods=['GET'])
def get_student_info():
    if session.get('role') != 'student': return jsonify({})
    s = db.students.find_one({"_id": ObjectId(session.get('user_id'))})
    return jsonify({"year": s.get('year'), "has_scholarship": s.get('has_scholarship'), "is_graduated": s.get('is_graduated')})

# ==============================================================================
#                                AI & CHAT APIs
# ==============================================================================

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        from chatbot_core import get_ai_response, generate_chat_title
        d = request.json
        sid, msg, uid = d.get('session_id'), d.get('message'), session.get('user_id')
        if not sid: return jsonify({"error": "No Session ID"}), 400
        resp = get_ai_response(msg, sid, uid)
        db.conversations.update_one({"session_id": sid}, {
            "$push": {"messages": {"user": msg, "ai": resp, "time": time.time()}},
            "$set": {"updated_at": time.time(), "user_id": uid},
            "$setOnInsert": {"created_at": time.time(), "title": generate_chat_title(msg, resp)}
        }, upsert=True)
        convo = db.conversations.find_one({"session_id": sid})
        return jsonify({"response": resp, "title": convo.get('title')})
    except: return jsonify({"response": "AI Unavailable"})

@app.route('/api/upload', methods=['POST'])
def upload_chat_file():
    try:
        from rag_utils import index_document
        if index_document(request.files.get('file'), request.files.get('file').filename, request.form.get('session_id')):
            return jsonify({"success": True})
    except: pass
    return jsonify({"success": False})

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    convos = list(db.conversations.find({"user_id": session.get('user_id')}).sort("updated_at", -1))
    return jsonify([{"session_id": c["session_id"], "title": c.get("title")} for c in convos])

@app.route('/api/load_session/<session_id>', methods=['GET'])
def load_session(session_id):
    c = db.conversations.find_one({"session_id": session_id, "user_id": session.get('user_id')})
    return jsonify({"messages": c.get('messages', []), "title": c.get('title')}) if c else jsonify({})

@app.route('/api/reset', methods=['POST'])
def reset_chat(): return jsonify({"success": True})

@app.route('/api/quiz/generate', methods=['POST'])
def generate_quiz():
    try:
        from quiz_core import generate_quiz_ai
        d = request.json
        content = generate_quiz_ai(d.get('subject'), d.get('difficulty'), d.get('language'))
        qid = str(uuid.uuid4())
        db.quizzes.insert_one({"quiz_id": qid, "user_id": session.get('user_id'), "content": content})
        return jsonify({"success": True, "quiz_id": qid})
    except: return jsonify({"success": False})

# --- UPDATED: ROBUST QUIZ LOADING ---
@app.route('/api/quiz/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    q = db.quizzes.find_one({"quiz_id": quiz_id})
    if not q: return jsonify({"error": "Quiz introuvable"}), 404
    
    content = q.get('content', {})

    # 1. Parse if string (Fix "Expecting ',' delimiter" issue aftermath)
    if isinstance(content, str):
        try: content = json.loads(content)
        except: content = {}

    # 2. Normalize Dict vs List
    if isinstance(content, dict):
        questions = content.get('questions', [])
        subject = content.get('subject', 'Quiz')
    elif isinstance(content, list):
        questions = content
        subject = "Quiz"
    else:
        questions = []
        subject = "Erreur de format"

    # 3. Sanitize
    safe_questions = []
    for i in questions:
        if isinstance(i, dict):
            safe_q = {k: v for k, v in i.items() if k != 'correct_answer'}
            safe_questions.append(safe_q)

    return jsonify({"questions": safe_questions, "subject": subject})

# --- UPDATED: ROBUST QUIZ HINT ---
@app.route('/api/quiz/hint', methods=['POST'])
def get_quiz_hint():
    try:
        data = request.json
        quiz = db.quizzes.find_one({"quiz_id": data.get('quiz_id')})
        if not quiz: return jsonify({"hint": "Quiz introuvable."})
        
        # Robust content extraction (same as get_quiz)
        content = quiz.get('content', {})
        if isinstance(content, str):
            try: content = json.loads(content)
            except: content = {}
            
        questions = content.get('questions', []) if isinstance(content, dict) else (content if isinstance(content, list) else [])
        
        idx = int(data.get('index', 0))
        if 0 <= idx < len(questions):
            q = questions[idx]
            hint = q.get('hint')
            if not hint:
                ans = q.get('correct_answer', '')
                hint = f"La réponse commence par '{ans[0].upper()}'..." if ans else "Aucun indice."
            return jsonify({"hint": hint})
        return jsonify({"hint": "Question invalide."})
    except: return jsonify({"hint": "Erreur."})

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    try:
        from quiz_core import grade_quiz_ai
        q = db.quizzes.find_one({"quiz_id": request.form.get('quiz_id')})
        return jsonify(grade_quiz_ai(q['content'], json.loads(request.form.get('answers'))))
    except: return jsonify({})

@app.route('/api/summarize', methods=['POST'])
def generate_summary_route():
    try:
        from summary_core import summarize_content
        from rag_utils import extract_text_from_pdf
        txt = extract_text_from_pdf(request.files['file']) if 'file' in request.files else request.form.get('text','')
        return jsonify({"success": True, "summary": summarize_content(txt[:30000], request.form.get('type'))})
    except: return jsonify({"success": False})

@app.route('/api/plan/generate', methods=['POST'])
def create_study_plan_route():
    try:
        from planner_core import generate_study_plan
        mats = [m.get('title') for m in db.materials.find({"uploaded_by": session.get('user_id')})]
        return jsonify({"success": True, "plan": generate_study_plan(request.json.get('days'), request.json.get('subjects'), request.json.get('goal'), mats)})
    except: return jsonify({"success": False})

if __name__ == '__main__':
    print("🚀 University System Online: http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)