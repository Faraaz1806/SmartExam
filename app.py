from flask import Flask,render_template
from pymongo import MongoClient

app = Flask(__name__)


from pymongo import MongoClient
# client = MongoClient("mongodb+srv://Admin:<db_password>@cluster0.l4o5d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

@app.route('/')
def inedex():
    return render_template('registerUI.html')


if __name__ == '__main__':
    app.run(debug=True)