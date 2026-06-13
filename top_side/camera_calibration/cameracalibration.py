#checkerboard img needs to be taken underwater and needs to be taken straight on
import numpy as np
import cv2 as cv
import csv
import glob
import os
import shutil
from datetime import datetime

# Change to the script's directory so relative paths work
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

CALIBRATION_FILE = os.path.join(BASE_DIR, "camera_calibration_params.csv")
CALIBRATION_ARCHIVE_DIR = os.path.join(BASE_DIR, "archived_calibrations")


def archive_existing_calibration():
    if not os.path.exists(CALIBRATION_FILE):
        return None

    os.makedirs(CALIBRATION_ARCHIVE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = os.path.join(
        CALIBRATION_ARCHIVE_DIR,
        f"camera_calibration_params_{timestamp}.csv",
    )

    counter = 1
    while os.path.exists(archive_path):
        archive_path = os.path.join(
            CALIBRATION_ARCHIVE_DIR,
            f"camera_calibration_params_{timestamp}_{counter}.csv",
        )
        counter += 1

    shutil.move(CALIBRATION_FILE, archive_path)
    return archive_path


def save_calibration_parameters(
    camera_matrix,
    distortion_coefficients,
    rotation_vectors,
    translation_vectors,
    new_camera_matrix,
    roi,
    reprojection_error,
):
    archived_path = archive_existing_calibration()
    if archived_path is not None:
        print("Archived previous calibration settings:", archived_path)

    rows = []
    rows.extend(array_to_csv_rows("camera_matrix", camera_matrix))
    rows.extend(array_to_csv_rows("distortion_coefficients", distortion_coefficients))
    rows.extend(array_to_csv_rows("rotation_vectors", rotation_vectors))
    rows.extend(array_to_csv_rows("translation_vectors", translation_vectors))
    rows.extend(array_to_csv_rows("frame_size", frameSize))
    rows.extend(array_to_csv_rows("chessboard_size", chessboardSize))
    rows.extend(array_to_csv_rows("new_camera_matrix", new_camera_matrix))
    rows.extend(array_to_csv_rows("roi", roi))
    rows.extend(array_to_csv_rows("reprojection_error", reprojection_error))
    rows.extend(array_to_csv_rows("saved_at", datetime.now().isoformat(timespec="seconds")))

    with open(CALIBRATION_FILE, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["parameter", "index_0", "index_1", "index_2", "value"])
        writer.writerows(rows)

    print("Saved calibration settings:", CALIBRATION_FILE)


def array_to_csv_rows(parameter_name, value):
    value_array = np.asarray(value)

    if value_array.ndim == 0:
        return [[parameter_name, "", "", "", value_array.item()]]

    rows = []
    for index in np.ndindex(value_array.shape):
        padded_index = list(index) + [""] * (3 - len(index))
        rows.append([parameter_name, padded_index[0], padded_index[1], padded_index[2], value_array[index]])
    return rows

########### FIND CHESSBOARD CORNERS - objPoints AND imgPoints ############
chessboardSize = (8,6)
frameSize = (3840,2160)

# # termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ......,(6,5,0)
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1,2)

# # Arrays to store object points and image points from all the images.
objPoints = [] # 3d point in real world space
imgPoints = [] # 2d points in image plane.

images = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c*.png'))
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
    raise RuntimeError("No corners found â€” check chessboardSize matches your board")
ret, cameraMatrix, dist, rvecs, tvecs = cv.calibrateCamera(objPoints, imgPoints, frameSize, None, None)

print("Camera Calibrated: ", ret)
print("\nCamera Matix:\n", cameraMatrix)
print("\nDistortion Parameters:\n", dist)
print("\nRotation Vectors:\n", rvecs)
print("\nTranslation Vectors:\n", tvecs)

# Reprojection Error
mean_error = 0
for i in range(len(objPoints)):
    imgPoints2, _ = cv.projectPoints(objPoints[i], rvecs[i], tvecs[i], cameraMatrix, dist)
    error = cv.norm(imgPoints[i], imgPoints2, cv.NORM_L2) / len(imgPoints2)
    mean_error += error

reprojection_error = mean_error / len(objPoints)
print("Total reprojection error: ", reprojection_error)

calibration_new_camera_matrix, calibration_roi = cv.getOptimalNewCameraMatrix(
    cameraMatrix,
    dist,
    frameSize,
    1,
    frameSize,
)
save_calibration_parameters(
    cameraMatrix,
    dist,
    rvecs,
    tvecs,
    calibration_new_camera_matrix,
    calibration_roi,
    reprojection_error,
)


########UNDISTORTION##################



img = cv.imread('measurement.png')
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
