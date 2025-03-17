import cv2

# Load the image
image = cv2.imread("static/image/sha.jpeg")  # Replace with your image path

# Check if the image was loaded successfully
if image is None:
    raise FileNotFoundError("❌ Error: Image not found or could not be loaded!")

# Convert the image from BGR to RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Display the original and converted images (optional)
cv2.imshow("Original Image (BGR)", image)
cv2.imshow("Converted Image (RGB)", image_rgb)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the converted image (optional)
cv2.imwrite("sh.jpg", cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))