from flask import Flask, request, jsonify, render_template, redirect, url_for, session,flash
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_session import Session
#HEREE FARAAZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ

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
#-------------------------------------------------------------------------------------
@app.route('/')
def home():
    return render_template('mainLanding.html')
# ✅ Route to render Create Test Page (GET) and save test to DB (POST)
import random

@app.route('/create_test', methods=['GET', 'POST']) 
def t_createtest():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for('login'))  # Restrict access to teachers only
    
    if request.method == 'POST':
        data = request.json
        test_id = random.randint(1000, 9999)  # Generate a random 4-digit test ID
        
        test_data = {
            "test_id": test_id,
            "teacher": session["username"],  
            "test_title": data.get("test_title"),
            "questions": data.get("questions")  # List of questions
        }
        
        # Store in MongoDB
        mongo.tests.insert_one(test_data)
        
        return jsonify({"message": f"Test created successfully! Test ID: {test_id}", "test_id": test_id})

    return render_template("t_createtest.html", username=session["username"])

#------------------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data["username"].strip().lower()
        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            flash("❌ User already exists. Choose a different username.", "danger")
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = {
            "username": username,
            "password": hashed_password,
            "role": data["role"].lower()
        }

        try:
            mongo.db.users.insert_one(user)
            print("User inserted successfully")
            flash("✅ Registration successful! Please log in.", "success") #added flash message
            return redirect(url_for('login')) #Added redirect.
        except Exception as mongo_error:
            print(f"MongoDB insert error: {mongo_error}")
            flash(f"Database error: {mongo_error}", "danger") #Added flash message.
            return redirect(url_for('register')) #Added redirect.

    return render_template("register.html") #Moved outside the POST block

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get("identifier")
        password = request.form.get("password")

        if not identifier or not password:
            flash("❌ Please enter both username and password!", "danger")
            return redirect(url_for('login'))

        user = mongo.db.users.find_one({"username": identifier})

        if user and bcrypt.check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["role"] = user["role"]

            # flash("✅ Login successful!", "success")

            if user["role"] == "student":
                return redirect(url_for('s_dashboard'))
            elif user["role"] == "teacher":
                return redirect(url_for('t_dashboard'))
            elif user["role"] == "admin":
                return redirect(url_for('a_dashboard'))

        flash("❌ Invalid username or password!", "danger")
        return redirect(url_for('login'))

    return render_template("login.html")



@app.route('/logout')
def logout():
    session.clear()  # ✅ Clear session
    return redirect(url_for('login'))

@app.route('/s_dashboard')
def s_dashboard():
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for('login'))

    # Retrieve and clear the login message
    login_message = session.pop('login_message', None)

    # Pass the login_message to the template
    return render_template('s_dashboard.html', username=session["username"], login_message=login_message)

@app.route('/t_dashboard')
def t_dashboard():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for('login'))

    login_message = session.pop('login_message', None)

    return render_template("t_dashboard.html", username=session["username"], login_message=login_message)
@app.route('/s_profile')
def s_profile():
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.json
        data["username"] = session["username"]  # Link data to logged-in user
        mongo.profiles.update_one({"username": session["username"]}, {"$set": data}, upsert=True)
        return jsonify({"message": "Profile saved successfully!"})

    return render_template("s_profile.html", username=session["username"])

@app.route('/save_profile', methods=['POST'])
def save_profile():
    if "username" not in session or session.get("role") not in ["student", "teacher"]:
        return jsonify({"message": "Unauthorized"}), 401  # Only logged-in users can save profiles

    data = request.json
    data["username"] = session["username"]
    data["role"] = session["role"]  # Store the role (student/teacher)

    # Differentiate between student and teacher profiles
    if session["role"] == "student":
        mongo.profiles.update_one(
            {"username": session["username"], "role": "student"},
            {"$set": data},
            upsert=True
        )
    elif session["role"] == "teacher":
        mongo.profiles.update_one(
            {"username": session["username"], "role": "teacher"},
            {"$set": data},
            upsert=True
        )

    return jsonify({"message": f"{session['role'].capitalize()} profile saved successfully!"})


@app.route('/get_s_profile', methods=['GET'])
def get_s_profile():
    if "username" not in session or session.get("role") != "student":
        return jsonify({"message": "Unauthorized"}), 401
    
    student_profile = mongo.profiles.find_one({"username": session["username"], "role": "student"}, {"_id": 0})
    return jsonify(student_profile if student_profile else {"message": "Profile not found!"})


#Teacher


@app.route('/create-exam')
def create_exam():
    return render_template('create_exam.html')

@app.route('/view_tests')
def view_tests():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for('login'))  # Restrict access to teachers only
    
    tests = list(mongo.db.tests.find({}, {"_id": 0}))  # Fetch all tests, excluding ObjectId
    return render_template('view_tests.html', tests=tests)


    
@app.route('/view-results')
def view_result():
   return render_template('view_result.html')

@app.route('/profile')
def profile():
    return render_template('t_profile.html')

teacher_collection = mongo.db.teachers_Profile


@app.route('/get_teacher_profile', methods=['GET'])
def get_teacher_profile():
    if "username" not in session or session.get("role") != "teacher":
        return jsonify({"message": "Unauthorized"}), 401  # Restrict access to teachers only

    teacher = teacher_collection.find_one({"username": session["username"]}, {"_id": 0})
    if teacher:
        return jsonify(teacher)
    
    return jsonify({"message": "No teacher profile found"})


@app.route('/save_teacher_profile', methods=['POST'])
def save_teacher_profile():
    if "username" not in session or session.get("role") != "teacher":
        return jsonify({"message": "Unauthorized"}), 401  # Restrict access to teachers only

    data = request.json
    data["username"] = session["username"]  # Ensure profile is linked to the logged-in teacher

    teacher_collection.update_one(
        {"username": session["username"]},
        {"$set": data},
        upsert=True
    )
    return jsonify({"message": "Teacher profile saved successfully!"})

@app.route('/s_test', methods=['GET', 'POST'])
def s_test():
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        test_id = request.form.get("test_id")
        print(f"Student entered test_id: {test_id}")  # Debugging: Print the entered test ID
        try:
            test_id_int = int(test_id)
            test = mongo.tests.find_one({"test_id": test_id_int})
            print(f"Database query result: {test}") #debugging print of the result of the search.

            if test:
                return render_template('take_test.html', test=test)
            else:
                return render_template('s_test.html', message="Test not found.")
        except ValueError:
            return render_template('s_test.html', message="Invalid test ID format.")

    return render_template('s_test.html')

@app.route('/get_test/<int:test_id>', methods=['GET'])
def get_test(test_id):
    test = mongo.db.tests.find_one({"test_id": test_id})
    if test:
        return jsonify(test)  # Return the test details as JSON
    return jsonify({"message": "Test not found"}), 404


@app.route('/submit_test/<int:test_id>', methods=['POST'])
def submit_test(test_id):
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for('login'))

    print(f"Received test_id: {test_id}")  # Debugging line

    test = mongo.db.tests.find_one({"test_id": test_id})
    if not test:
        return jsonify({"message": "Test not found"}), 404

    answers = {}
    for question_num, question in enumerate(test["questions"], start=1):
        student_answer = request.form.get(f"question_{question_num}")
        answers[question_num] = {
            "correct_answer": question["correct_option"],
            "student_answer": student_answer,
            "is_correct": student_answer == question["correct_option"]
        }

    return render_template('test_results.html', answers=answers)  # Render test results page

if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Fixed indentation