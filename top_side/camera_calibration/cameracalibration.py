import numpy as np
import cv2 as cv
import glob
import os

# Change to the script's directory so relative paths work
os.chdir(os.path.dirname(os.path.abspath(__file__)))

########### FIND CHESSBOARD CORNERS - objPoints AND imgPoints ############
chessboardSize = (8,6)
frameSize = (1190,841)

# # termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ......,(6,5,0)
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1,2)

# # Arrays to store object points and image points from all the images.
objPoints = [] # 3d point in real world space
imgPoints = [] # 2d points in image plane.

images = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'C*.jpg'))
print(len(images))

for image in images:
    print(image)
    img = cv.imread(image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)
    print("return = ", ret)

    # # If found, add object points, image points (after refining them)
    if ret == True:
        
        objPoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgPoints.append(corners2)

        #Draw and display corners
        cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(1000)


cv.destroyAllWindows()

print("Object Points: ", objPoints)
print("Image Points: ", imgPoints)




#####CALIBRATION###############

if len(objPoints) == 0:
    raise RuntimeError("No corners found — check chessboardSize matches your board")
ret, cameraMatrix, dist, rvecs, tvecs = cv.calibrateCamera(objPoints, imgPoints, frameSize, None, None)

print("Camera Calibrated: ", ret)
print("\nCamera Matix:\n", cameraMatrix)
print("\nDistortion Parameters:\n", dist)
print("\nRotation Vectors:\n", rvecs)
print("\nTranslation Vectors:\n", tvecs)


########UNDISTORTION##################



img = cv.imread('measurement.jpg')
h, w = img.shape[:2]
newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

# Undistort
dst = cv.undistort(img, cameraMatrix, dist, None, newCameraMatrix)
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]


cv.imwrite('caliResult1.jpg', dst)
cv.imshow('Undistorted Result 1', dst)
cv.waitKey(0)



# Undistort with remapping
mapx, mapy = cv.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (img.shape[1], img.shape[0]), cv.CV_16SC2)
dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
#crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('caliResult2.jpg', dst)
cv.imshow('Undistorted Result 2', dst)
cv.waitKey(0)

cv.destroyAllWindows()
# Reprojection Error
mean_error = 0
for i in range(len(objPoints)):
    imgPoints2, _ = cv.projectPoints(objPoints[i], rvecs[i], tvecs[i], cameraMatrix, dist)
    error = cv.norm(imgPoints[i], imgPoints2, cv.NORM_L2) / len(imgPoints2)
    mean_error += error

print("Total reprojection error: ", mean_error / len(objPoints))