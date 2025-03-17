import time
import pygetwindow as gw

while True:
    active_window=gw.getActiveWindow()
    if active_window:
        print("Active Window:", active_window.title)
    time.sleep(1)
