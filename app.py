from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://Admin:Halal1806@cluster0.l4o5d.mongodb.net/mydatabase?retryWrites=true&w=majority"
app.config["JWT_SECRET_KEY"] = "bfe71a6d892b4f1ea7d0b1e3b6df8a7a3f6f5e3c9a2d8d7f"

client = MongoClient(app.config["MONGO_URI"])
mongo = client.get_database()

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

try:
    mongo.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = mongo.users.find_one({"username": data["identifier"]}) #change username to identifier.
        if user and bcrypt.check_password_hash(user["password"], data["password"]):
            access_token = create_access_token(identity={"username": user["username"], "role": user["role"]})
            return redirect(url_for('dashboard', token=access_token))
        return jsonify({"message": "Invalid credentials!"}), 401
    return render_template("login.html")

@app.route('/dashboard')
# @jwt_required() #add jwt_required decorator.
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)