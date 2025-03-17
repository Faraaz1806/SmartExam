from flask import Flask , render_template
 
app=Flask(__name__)

@app.route('/')
def tab():
    return render_template('reload.html')

if __name__=="__main__":
    app.run(debug=True)