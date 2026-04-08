import cv2
import numpy as np

# --- CONFIGURATION ---
KNOWN_DISTANCE = 4.0  # The lasers are exactly 4 inches apart
IMAGE_PATH = "your_photo.jpg"  # Put your image filename here

# Global variables to store your measurement clicks
measurement_points = []
pixels_per_inch = None

def mouse_callback(event, x, y, flags, param):
    global measurement_points, pixels_per_inch
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Save the point where you clicked
        measurement_points.append((x, y))
        
        # We need 2 points to make a measurement
        if len(measurement_points) == 2:
            p1, p2 = measurement_points[0], measurement_points[1]
            
            # Calculate pixel distance of your clicks
            dist_px = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            
            if pixels_per_inch:
                final_inches = dist_px / pixels_per_inch
                print(f"Measurement: {final_inches:.2f} inches")
                
                # Draw the measurement on the screen
                cv2.line(display_img, p1, p2, (0, 255, 255), 2)
                cv2.putText(display_img, f"{final_inches:.2f} in", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.imshow("Measure Tool", display_img)
            else:
                print("Error: Lasers not detected. Cannot calibrate scale.")
            
            # Reset points for the next measurement
            measurement_points = []

# 1. Load the Image
raw_img = cv2.imread(IMAGE_PATH)
if raw_img is None:
    print(f"Error: Could not find {IMAGE_PATH}")
    exit()

display_img = raw_img.copy()

# 2. Detect Lasers (Automatic Calibration)
hsv = cv2.cvtColor(raw_img, cv2.COLOR_BGR2HSV)
# Looking for bright green laser dots
mask = cv2.inRange(hsv, np.array([150, 100, 200]), np.array([180, 255, 255]))
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

laser_centers = []
for c in contours:
    if cv2.contourArea(c) > 2:
        M = cv2.moments(c)
        if M["m00"] != 0:
            laser_centers.append((int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])))

# 3. Setup the "Ruler"
if len(laser_centers) >= 2:
    laser_centers = sorted(laser_centers, key=lambda x: x[0])
    l1, l2 = laser_centers[0], laser_centers[1]
    
    # How many pixels represent 4 inches?
    laser_dist_px = np.sqrt((l1[0]-l2[0])**2 + (l1[1]-l2[1])**2)
    pixels_per_inch = laser_dist_px / KNOWN_DISTANCE
    
    # Draw blue line between lasers to show it worked
    cv2.line(display_img, l1, l2, (255, 0, 0), 2)
    cv2.putText(display_img, "CALIBRATED (4in)", (l1[0], l1[1]-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    print(f"Calibration successful: {pixels_per_inch:.2f} pixels per inch.")
else:
    print("Warning: Could not find 2 laser dots. Scale is unknown.")

# 4. Interaction Loop
cv2.imshow("Measure Tool", display_img)
cv2.setMouseCallback("Measure Tool", mouse_callback)

print("INSTRUCTIONS:")
print("1. The blue line shows the 4-inch laser reference.")
print("2. Click two points on the object you want to measure.")
print("3. Results will print here and show on the image.")
print("4. Press any key to close.")

cv2.waitKey(0)
cv2.destroyAllWindows()