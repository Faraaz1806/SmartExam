from flask import Flask, request, jsonify, render_template, redirect, url_for, session
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

# ✅ Route to render Create Test Page (GET) and save test to DB (POST)
@app.route('/create_test', methods=['GET', 'POST'])
def t_createtest():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for('login'))  # Restrict access to teachers only
    
    if request.method == 'POST':
        data = request.json
        test_data = {
            "teacher": session["username"],  
            "test_title": data.get("test_title"),
            "questions": data.get("questions")  # List of questions
        }
        
        # Store in MongoDB
        mongo.tests.insert_one(test_data)
        
        return jsonify({"message": "Test created successfully!"})

    return render_template("t_createtest.html", username=session["username"])


#------------------------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = {
            "username": data["username"],
            "password": hashed_password,
            "role": data["role"].lower()
        }
        mongo.users.insert_one(user)
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = mongo["users"].find_one({"username": data["identifier"]})

        if user and bcrypt.check_password_hash(user["password"], data["password"]):
            # ✅ Store user info in session
            session["username"] = user["username"]
            session["role"] = user["role"]

            # ✅ Redirect to the respective dashboard
            if user["role"] == "student":
                return redirect(url_for('s_dashboard'))
            elif user["role"] == "teacher":
                return redirect(url_for('t_dashboard'))
            else:
                return redirect(url_for('login'))  # Default fallback

        return jsonify({"message": "Invalid credentials!"}), 401

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()  # ✅ Clear session
    return redirect(url_for('login'))

@app.route('/s_dashboard')
def s_dashboard():
    if "username" not in session or session.get("role") != "student":
        return redirect(url_for('login'))
    return render_template('s_dashboard.html', username=session["username"])

@app.route('/t_dashboard')
def t_dashboard():
    if "username" not in session or session.get("role") != "teacher":
        return redirect(url_for('login'))
    return render_template("t_dashboard.html", username=session["username"])

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

if __name__ == '__main__':
    app.run(debug=True, port=8000)  # Example: Run on port 8000
