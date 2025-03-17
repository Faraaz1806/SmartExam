from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request
# Initialize the Flask application
app = Flask(__name__)

# Configure the SQLAlchemy database URI and disable modification tracking
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(300), nullable=False)
    

    def __repr__(self) -> str:
        return f"{self.sno} -- {self.title} -- {self.desc}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method("POST"):
        print("POST")

    todo=Todo(title="Day one", desc="excercise")
    db.session.add(todo)
    db.session.commit()
    alltodo = Todo.query.all()  
    return render_template('tod.html' , alltodo=alltodo) 

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)