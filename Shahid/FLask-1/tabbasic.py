from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import platform
import threading

if platform.system() == "Windows":
    import pygetwindow as gw
elif platform.system() == "Linux":
    import subprocess

app = Flask(__name__)
s = SocketIO(app, cors_allowed_origins="*")  # Fix for WebSocket CORS issues

def get_active_window():
    """Gets the currently active window title."""
    system = platform.system()
    
    if system == "Windows":
        window = gw.getActiveWindow()
        return window.title if window else None

    elif system == "Linux":
        try:
            result = subprocess.run(
                ["xdotool", "getwindowfocus", "getwindowname"],
                stdout=subprocess.PIPE, text=True
            )
            return result.stdout.strip()
        except Exception:
            return None
    return None

def monitor_screen_switch():
    """Continuously monitors if the user switches to another window."""
    previous_window = get_active_window()
    while True:
        current_window = get_active_window()
        if current_window and current_window != previous_window:
            print(f"Switched to: {current_window}")  # Debugging
            s.emit('screen_switch', {'window': current_window}, broadcast=True)
            previous_window = current_window
        s.sleep(1)  # Use s.sleep() instead of time.sleep()

@app.route('/')
def index():
    return render_template('tod.html')

@s.on('connect')
def handle_connect():
    print("Client connected")
    s.emit('server_message', {'message': 'WebSocket connected!'})

if __name__ == '__main__':
    threading.Thread(target=monitor_screen_switch, daemon=True).start()
    s.run(app, debug=True , port=3000)
