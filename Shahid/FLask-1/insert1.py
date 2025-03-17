from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    users = User.query.all()  
    return render_template('index1.html', users=users)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    print(f"Received name: {name}")  
    new_user = User(name=name)
    db.session.add(new_user)
    db.session.commit()
    print(f"User {name} added to database.") 
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
