from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_session import Session

app = Flask(__name__)

# MongoDB Connection
app.config["MONGO_URI"] = "mongodb+srv://Admin:Halal1806@cluster0.l4o5d.mongodb.net/mydatabase?retryWrites=true&w=majority"

# Session Configuration
app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["SESSION_TYPE"] = "filesystem"  # Store sessions on the server
app.config["SESSION_PERMANENT"] = False
Session(app)

client = MongoClient(app.config["MONGO_URI"])
mongo = client.get_database()
bcrypt = Bcrypt(app)

try:
    mongo.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# Collections
users_collection = mongo["users"]
teachers_collection = mongo["teachers_Profile"]
tests_collection = mongo["tests"]
profiles_collection = mongo["profiles"]

# ---------------------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('mainLanding.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = {
            "username": data["username"],
            "email": data["email"],
            "password": hashed_password,
            "role": data["role"].lower()
        }
        users_collection.insert_one(user)
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = users_collection.find_one({"username": data["identifier"]})

        if user and bcrypt.check_password_hash(user["password"], data["password"]):
            session["username"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "student":
                return redirect(url_for('s_dashboard'))
            elif user["role"] == "teacher":
                return redirect(url_for('t_dashboard'))
            else:
                return redirect(url_for('login'))

        return jsonify({"message": "Invalid credentials!"}), 401

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/s_dashboard')
def s_dashboard():
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for('login'))
    return render_template('s_dashboard.html', username=session["username"])

@app.route('/s_profile')
def s_profile():
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.json
        data["username"] = session["username"]
        profiles_collection.update_one({"username": session["username"]}, {"$set": data}, upsert=True)
        return jsonify({"message": "Profile saved successfully!"})

    return render_template("s_profile.html", username=session["username"])

@app.route('/save_profile', methods=['POST'])
def save_profile():
    if "username" not in session or session.get("role") not in ["student", "teacher"]:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    data["username"] = session["username"]
    data["role"] = session["role"]

    if session["role"] == "student":
        profiles_collection.update_one({"username": session["username"], "role": "student"}, {"$set": data}, upsert=True)
    elif session["role"] == "teacher":
        profiles_collection.update_one({"username": session["username"], "role": "teacher"}, {"$set": data}, upsert=True)

    return jsonify({"message": f"{session['role'].capitalize()} profile saved successfully!"})

@app.route('/get_s_profile', methods=['GET'])
def get_s_profile():
    if "username" not in session or session.get("role") != "student":
        return jsonify({"message": "Unauthorized"}), 401
    
    student_profile = profiles_collection.find_one({"username": session["username"], "role": "student"}, {"_id": 0})
    return jsonify(student_profile if student_profile else {"message": "Profile not found!"})

# ---------------------------------------------------------------------------------
# Teacher Dashboard
@app.route('/t_dashboard')
def t_dashboard():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for('login'))

    teacher = teachers_collection.find_one({"username": session["username"]}, {"_id": 0})

    return render_template('t_dashboard.html', teacher=teacher)

@app.route('/create_test', methods=['GET', 'POST'])
def t_createtest():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.json
        test_data = {
            "teacher": session["username"],
            "test_title": data.get("test_title"),
            "questions": data.get("questions")
        }
        tests_collection.insert_one(test_data)
        return jsonify({"message": "Test created successfully!"})

    return render_template("t_createtest.html", username=session["username"])

@app.route('/create-exam')
def create_exam():
    return render_template('create_exam.html')

@app.route('/view-results')
def view_results():
   return render_template('view_result.html')

@app.route('/profile')
def profile():
    return render_template('t_profile.html')

@app.route('/get_teacher_profile', methods=['GET'])
def get_teacher_profile():
    if "username" not in session or session.get("role") != "teacher":
        return jsonify({"message": "Unauthorized"}), 401

    teacher = teachers_collection.find_one({"username": session["username"]}, {"_id": 0})
    if teacher:
        return jsonify(teacher)
    
    return jsonify({"message": "No teacher profile found"})

@app.route('/save_teacher_profile', methods=['POST'])
def save_teacher_profile():
    if "username" not in session or session.get("role") != "teacher":
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json
    data["username"] = session["username"]

    teachers_collection.update_one({"username": session["username"]}, {"$set": data}, upsert=True)
    return jsonify({"message": "Teacher profile saved successfully!"})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
