import cv2

# Use 0 for the default camera, or 2 as in your previous script
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("Error: Could not open camera.")
else:
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('test_image.jpg', frame)
        print("Success! Image saved as test_image.jpg")
    else:
        print("Error: Could not read frame.")

cap.release()