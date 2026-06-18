"""
Batch image undistortion.

Select one or more images, undistort them with the saved camera calibration,
and write the corrected images out.
"""

import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os
import datetime
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_CSV = os.path.join(BASE_DIR, "camera_calibration", "camera_calibration_params.csv")


def parse_calibration_value(value):
    try:
        return float(value)
    except ValueError:
        return value


def read_calibration_csv(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing calibration file: {csv_path}")

    grouped_values = {}
    with open(csv_path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            parameter = row["parameter"]
            indexes = [
                int(row[index_name])
                for index_name in ("index_0", "index_1", "index_2")
                if row[index_name] != ""
            ]
            value = parse_calibration_value(row["value"])
            grouped_values.setdefault(parameter, []).append((tuple(indexes), value))

    calibration = {}
    for parameter, values in grouped_values.items():
        if values[0][0] == ():
            calibration[parameter] = values[0][1]
            continue

        shape = tuple(max(index[axis] for index, _value in values) + 1 for axis in range(len(values[0][0])))
        array = np.zeros(shape, dtype=np.float64)
        for index, value in values:
            array[index] = value
        calibration[parameter] = array

    return calibration


def undistort_image(img, camera_matrix, distortion_coefficients):
    h, w = img.shape[:2]
    # Match measurementbasics.py: alpha=0 keeps this calibration centered.
    # alpha=1 pushes the corrected view off to the right for these images.
    new_camera_matrix, _roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, distortion_coefficients, (w, h), 0, (w, h)
    )
    return cv2.undistort(img, camera_matrix, distortion_coefficients, None, new_camera_matrix)


def main():
    root = tk.Tk()
    root.withdraw()

    # --- Load calibration ---
    try:
        calibration = read_calibration_csv(CALIBRATION_CSV)
        camera_matrix = calibration["camera_matrix"]
        distortion_coefficients = calibration["distortion_coefficients"]
    except Exception as error:
        messagebox.showerror("Calibration", f"Could not read calibration:\n{error}")
        return

    # Calibration is only valid for the resolution it was computed at.
    cal_size = calibration.get("frame_size")
    cal_wh = (int(cal_size[0]), int(cal_size[1])) if cal_size is not None else None

    # --- Pick images ---
    image_paths = filedialog.askopenfilenames(
        title="Select images to undistort",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")],
    )
    if not image_paths:
        print("No files selected.")
        return

    # --- Pick output folder (cancel = save next to each original) ---
    output_dir = filedialog.askdirectory(title="Select output folder (Cancel = save next to originals)")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    saved, skipped = [], []

    for image_path in image_paths:
        name = os.path.basename(image_path)
        img = cv2.imread(image_path)
        if img is None:
            print(f"SKIP (unreadable): {name}")
            skipped.append(f"{name} - could not read")
            continue

        h, w = img.shape[:2]
        if cal_wh is not None and (w, h) != cal_wh:
            print(f"SKIP (size {w}x{h} != calibration {cal_wh[0]}x{cal_wh[1]}): {name}")
            skipped.append(f"{name} - resolution {w}x{h} doesn't match calibration {cal_wh[0]}x{cal_wh[1]}")
            continue

        undistorted = undistort_image(img, camera_matrix, distortion_coefficients)

        base_name, ext = os.path.splitext(name)
        if ext.lower() not in (".jpg", ".jpeg", ".png", ".bmp", ".tiff"):
            ext = ".png"
        target_dir = output_dir if output_dir else os.path.dirname(image_path)
        os.makedirs(target_dir, exist_ok=True)
        out_path = os.path.join(target_dir, f"undistorted_{base_name}_{timestamp}{ext}")

        if cv2.imwrite(out_path, undistorted):
            print(f"Saved: {out_path}")
            saved.append(out_path)
        else:
            print(f"SKIP (write failed): {out_path}")
            skipped.append(f"{name} - write failed")

    # --- Summary ---
    summary = f"Undistorted {len(saved)} image(s)."
    if saved:
        summary += f"\nSaved to:\n{os.path.dirname(saved[0])}"
    if skipped:
        summary += "\n\nSkipped:\n" + "\n".join(skipped)
    print(summary)
    messagebox.showinfo("Undistort complete", summary)
    root.destroy()


if __name__ == "__main__":
    main()
