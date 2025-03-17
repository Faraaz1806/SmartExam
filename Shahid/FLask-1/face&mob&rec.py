from flask import Flask, render_template, Response
import cv2
import os
import datetime
from ultralytics import YOLO
import face_recognition
import numpy as np

app = Flask(__name__)
STUDENT_IMAGE = "sha.jpeg"

if not os.path.exists(STUDENT_IMAGE):
    raise FileNotFoundError(f"Error: {STUDENT_IMAGE} not found!")

#cv2.imwrite("sha.jpg", cv2.cvtColor(STUDENT_IMAGE, cv2.COLOR_RGB2BGR))

known_image = face_recognition.load_image_file(STUDENT_IMAGE)
known_encoding = face_recognition.face_encodings(known_image)[0]

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
camera = cv2.VideoCapture(0)
model = YOLO("yolov5su.pt")  

evidence_dir = "cheating_evidence"
os.makedirs(evidence_dir, exist_ok=True)

def capture():
    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        rgb= cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb)

        authorized_person = False
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([known_encoding], face_encoding)
            face_distance = face_recognition.face_distance([known_encoding], face_encoding)

            if matches[0] and face_distance[0] < 0.5:
                authorized_person = True

        box_color = (0, 255, 0) if authorized_person else (0, 0, 255)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

        if not authorized_person:
            cv2.putText(frame, "WARNING: Unauthorized Person!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if len(faces) > 1:
            cv2.putText(frame, "WARNING: Multiple people detected!", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = model.predict(rgb_frame)
        phone_detected = False
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]

                if "phone" in label or "cell" in label:
                    phone_detected = True
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "Mobile Detected!", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if phone_detected:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            evidence_path = os.path.join(evidence_dir, f"mobile_{timestamp}.jpg")
            cv2.imwrite(evidence_path, frame)
            print(f"Mobile detected! Evidence saved: {evidence_path}")

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def detect():
    return render_template('video.html')

@app.route('/video')
def video():
    return Response(capture(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, port=8000)
