import keyboard

def event(event):
    print(f"key:{event.name},Event:{event.event_type}")


keyboard.hook(event)
print("Listening to key events... Press 'esc' to stop.")
keyboard.wait("esc") 