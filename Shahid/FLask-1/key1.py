from flask import Flask, jsonify
import keyboard
import threading

app = Flask(__name__)

key_events = [] 


def detect_keys():
    global key_events
    while True:
        event = keyboard.read_event()
        key_events.append({"key": event.name, "event": event.event_type})

key_thread = threading.Thread(target=detect_keys, daemon=True)
key_thread.start()

@app.route('/')
def get_keys():
    
    return jsonify('base.html')

if __name__ == '__main__':
    app.run(debug=True)
