import cv2

# Load the image
image = cv2.imread("static/image/sample.jpg")

# Draw a green line
cv2.line(image, (50, 50), (300, 50), (0, 255, 0), 5)

# Draw a blue rectangle
cv2.rectangle(image, (100, 100), (400, 300), (255, 0, 0), 3)

# Draw a red filled circle
cv2.circle(image, (250, 250), 50, (0, 0, 255), 10)

# Add text
cv2.putText(image, "Hello OpenCV!", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv2.putText(image,"Hello World",(50,600),cv2.FONT_HERSHEY_SCRIPT_COMPLEX,1,(0,255,255),2)

# Show the image
cv2.imshow("Shapes on Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
