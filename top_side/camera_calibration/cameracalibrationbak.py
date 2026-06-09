import glob
import os

import cv2 as cv
import numpy as np


# Change to the script's directory so relative paths work.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)


########################
# ChArUco Board Settings
########################

# These settings must match the physical ChArUco board you print/use.
# squares_x and squares_y are the number of chessboard squares, not corners.
SQUARES_X = 7
SQUARES_Y = 5

# Use your real printed board measurements here. Units can be inches, cm, or mm,
# but square_length and marker_length must use the same unit.
SQUARE_LENGTH = 1.0
MARKER_LENGTH = 0.75

# Use the same dictionary that was used to create/print the ChArUco board.
ARUCO_DICTIONARY = cv.aruco.DICT_6X6_250

# Minimum detected ChArUco corners needed before using a photo for calibration.
MIN_CHARUCO_CORNERS = 6

# Turn this on if you want preview windows while the script runs.
SHOW_DETECTIONS = False


def get_aruco_dictionary(dictionary_id):
    if hasattr(cv.aruco, "getPredefinedDictionary"):
        return cv.aruco.getPredefinedDictionary(dictionary_id)
    return cv.aruco.Dictionary_get(dictionary_id)


def create_charuco_board(dictionary):
    if hasattr(cv.aruco, "CharucoBoard"):
        size = (SQUARES_X, SQUARES_Y)
        return cv.aruco.CharucoBoard(size, SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    return cv.aruco.CharucoBoard_create(
        SQUARES_X,
        SQUARES_Y,
        SQUARE_LENGTH,
        MARKER_LENGTH,
        dictionary,
    )


def create_detector_parameters():
    if hasattr(cv.aruco, "DetectorParameters"):
        return cv.aruco.DetectorParameters()
    return cv.aruco.DetectorParameters_create()


def detect_markers(gray, dictionary, detector_params):
    if hasattr(cv.aruco, "ArucoDetector"):
        detector = cv.aruco.ArucoDetector(dictionary, detector_params)
        return detector.detectMarkers(gray)

    return cv.aruco.detectMarkers(
        gray,
        dictionary,
        parameters=detector_params,
    )


def detect_charuco_corners(gray, board, dictionary, detector_params):
    if hasattr(cv.aruco, "CharucoDetector"):
        detector = cv.aruco.CharucoDetector(board)
        charuco_corners, charuco_ids, marker_corners, marker_ids = detector.detectBoard(gray)
    else:
        marker_corners, marker_ids, _ = detect_markers(gray, dictionary, detector_params)

        if marker_ids is None or len(marker_ids) == 0:
            return False, marker_corners, marker_ids, None, None

        _, charuco_corners, charuco_ids = cv.aruco.interpolateCornersCharuco(
            marker_corners,
            marker_ids,
            gray,
            board,
        )

    if marker_ids is None or len(marker_ids) == 0:
        return False, marker_corners, marker_ids, None, None

    found = (
        charuco_corners is not None
        and charuco_ids is not None
        and len(charuco_corners) >= MIN_CHARUCO_CORNERS
    )
    return found, marker_corners, marker_ids, charuco_corners, charuco_ids


def get_board_object_points(board, charuco_ids):
    if hasattr(board, "getChessboardCorners"):
        all_object_points = board.getChessboardCorners()
    else:
        all_object_points = board.chessboardCorners

    return np.array([all_object_points[int(point_id[0])] for point_id in charuco_ids], dtype=np.float32)


def main():
    if not hasattr(cv, "aruco"):
        raise RuntimeError("OpenCV ArUco module not found. Install opencv-contrib-python.")

    dictionary = get_aruco_dictionary(ARUCO_DICTIONARY)
    board = create_charuco_board(dictionary)
    detector_params = create_detector_parameters()

    all_charuco_corners = []
    all_charuco_ids = []
    object_points = []
    image_points = []
    frame_size = None

    images = sorted(glob.glob(os.path.join(BASE_DIR, "WIN*.jpg")))
    if not images:
        images = sorted(glob.glob(os.path.join(BASE_DIR, "W*.jpg")))
    images = [
        image_path
        for image_path in images
        if not image_path.lower().endswith("_charuco_detected.jpg")
    ]

    print(f"Calibration images found: {len(images)}")

    for image_path in images:
        print(image_path)
        img = cv.imread(image_path)
        if img is None:
            print("  skipped: could not read image")
            continue

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        frame_size = gray.shape[::-1]

        found, marker_corners, marker_ids, charuco_corners, charuco_ids = detect_charuco_corners(
            gray,
            board,
            dictionary,
            detector_params,
        )

        marker_count = 0 if marker_ids is None else len(marker_ids)
        corner_count = 0 if charuco_corners is None else len(charuco_corners)
        print(f"  markers: {marker_count}, charuco corners: {corner_count}, usable: {found}")

        if not found:
            continue

        all_charuco_corners.append(charuco_corners)
        all_charuco_ids.append(charuco_ids)
        object_points.append(get_board_object_points(board, charuco_ids))
        image_points.append(charuco_corners)

        cv.aruco.drawDetectedMarkers(img, marker_corners, marker_ids)
        cv.aruco.drawDetectedCornersCharuco(img, charuco_corners, charuco_ids)
        preview_path = os.path.splitext(image_path)[0] + "_charuco_detected.jpg"
        cv.imwrite(preview_path, img)

        if SHOW_DETECTIONS:
            cv.imshow("ChArUco detection", img)
            cv.waitKey(500)

    cv.destroyAllWindows()

    if len(all_charuco_corners) == 0:
        raise RuntimeError(
            "No ChArUco corners found. Check that your photos show a real ChArUco board "
            "and that SQUARES_X, SQUARES_Y, SQUARE_LENGTH, MARKER_LENGTH, and "
            "ARUCO_DICTIONARY match the printed board."
        )

    if hasattr(cv.aruco, "calibrateCameraCharuco"):
        ret, camera_matrix, dist, rvecs, tvecs = cv.aruco.calibrateCameraCharuco(
            all_charuco_corners,
            all_charuco_ids,
            board,
            frame_size,
            None,
            None,
        )
    else:
        ret, camera_matrix, dist, rvecs, tvecs = cv.calibrateCamera(
            object_points,
            image_points,
            frame_size,
            None,
            None,
        )

    print("Camera Calibrated:", ret)
    print("\nCamera Matrix:\n", camera_matrix)
    print("\nDistortion Parameters:\n", dist)
    print("\nRotation Vectors:\n", rvecs)
    print("\nTranslation Vectors:\n", tvecs)

    measurement = cv.imread("measurement.png")
    if measurement is None:
        raise FileNotFoundError("Missing measurement.png")

    h, w = measurement.shape[:2]
    new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist, (w, h), 1, (w, h))

    dst = cv.undistort(measurement, camera_matrix, dist, None, new_camera_matrix)
    x, y, w, h = roi
    dst = dst[y : y + h, x : x + w]
    cv.imwrite("caliResult1.jpg", dst)

    mapx, mapy = cv.initUndistortRectifyMap(
        camera_matrix,
        dist,
        None,
        new_camera_matrix,
        (measurement.shape[1], measurement.shape[0]),
        cv.CV_16SC2,
    )
    dst = cv.remap(measurement, mapx, mapy, cv.INTER_LINEAR)
    x, y, w, h = roi
    dst = dst[y : y + h, x : x + w]
    cv.imwrite("caliResult2.jpg", dst)

    mean_error = 0
    for i in range(len(object_points)):
        projected_points, _ = cv.projectPoints(
            object_points[i],
            rvecs[i],
            tvecs[i],
            camera_matrix,
            dist,
        )
        error = cv.norm(image_points[i], projected_points, cv.NORM_L2) / len(projected_points)
        mean_error += error

    print("Total reprojection error:", mean_error / len(object_points))


if __name__ == "__main__":
    main()
