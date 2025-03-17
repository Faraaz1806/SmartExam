from flask import Flask, render_template
from flask_socketio import SocketIO
import keyboard
import threading

app = Flask(__name__)
s = SocketIO(app, cors_allowed_origins="*")

def detect_keys():          
    with app.app_context():  
        while True:
            event = keyboard.read_event()
            s.emit("keyevent", {"key": event.name, "event": event.event_type})

key_thread = threading.Thread(target=detect_keys, daemon=True)
key_thread.start()

@app.route("/")
def home():

    return render_template("tod.html")

if __name__ == "__main__":
    s.run(app, debug=True)
