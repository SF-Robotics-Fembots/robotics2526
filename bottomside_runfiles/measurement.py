import cv2
import numpy as np

# --- CONFIGURATION ---
# The physical distance between your two laser pointers (e.g., 10 cm)
KNOWN_DISTANCE = 10.0 

# Global state
points = []

def mouse_click(event, x, y, flags, param):
    """Handles mouse clicks for measuring objects."""
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            points.append((x, y))
        else:
            points = [(x, y)] # Reset and start a new measurement

# 1. Initialize Camera (0 is usually the default RPi or USB cam)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 2. Create the GUI Window
window_name = "VS Code Laser Measure"
cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, mouse_click)

print("Starting... Point lasers at target. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 3. Detect Laser Dots (Looking for Bright Red)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Red color range - might need adjustment based on your specific laser
    lower_red = np.array([150, 50, 200])
    upper_red = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    # Find the laser centers
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    for c in contours:
        if cv2.contourArea(c) > 2:
            M = cv2.moments(c)
            if M["m00"] != 0:
                centers.append((int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])))

    # 4. Calibration Logic (Distance Triangulation)
    pixels_per_unit = None
    if len(centers) >= 2:
        # Get the two dots
        centers = sorted(centers, key=lambda x: x[0])
        p1, p2 = centers[0], centers[1]
        
        # Calculate pixel distance between lasers
        px_dist = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        pixels_per_unit = px_dist / KNOWN_DISTANCE
        
        # Visual Feedback: Blue line for the "Ruler"
        cv2.line(frame, p1, p2, (255, 0, 0), 2)
        cv2.putText(frame, "CALIBRATED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # 5. Measurement Logic
    for p in points:
        cv2.circle(frame, p, 5, (0, 0, 255), -1)

    if len(points) == 2 and pixels_per_unit:
        # Distance between your clicks
        obj_px = np.sqrt((points[0][0]-points[1][0])**2 + (points[0][1]-points[1][1])**2)
        actual_size = obj_px / pixels_per_unit
        
        # Display Yellow Measurement Line
        cv2.line(frame, points[0], points[1], (0, 255, 255), 2)
        cv2.putText(frame, f"{actual_size:.2f} units", (points[0][0], points[0][1]-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # 6. Refresh the GUI
    cv2.imshow(window_name, frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()