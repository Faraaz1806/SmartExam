from flask import Flask 
from flask import render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/Product')
def product():
    return "I am trying"

if __name__ == "__main__":
    app.run(debug=True)
