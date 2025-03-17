from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import datetime


app = Flask(__name__)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
camera = cv2.VideoCapture(0)
model = YOLO("yolov5s.pt") 

def capture():
    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        box_color = (0, 255, 0) if len(faces) == 1 else (0, 0, 255)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)  

       
        if len(faces) > 1:
            cv2.putText(frame, "WARNING: Multiple people detected!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
        rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results=model.predict(rgb_frame)

        phone_detected=False
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]

                if label.lower()=="cell phone":
                    phone_detected=True

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "Mobile Detected!", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
        if phone_detected:
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            evidence_path = f"cheating_evidence/mobile_{timestamp}.jpg"
            cv2.imwrite(evidence_path, frame)
            print(f"🚨 Mobile detected! Evidence saved: {evidence_path}")

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
    app.run(debug=True, port=7000)
