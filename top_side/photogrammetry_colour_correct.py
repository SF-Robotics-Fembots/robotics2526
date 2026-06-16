import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import cv2
import numpy as np


BLACK_THRESHOLD = 70
DARK_RED_MAX_BRIGHTNESS = 190
DARK_RED_MIN_SATURATION = 25
DARK_RED_HUE_RANGE = 18
RED_DOMINANCE_MARGIN = 8
RED_BGR = (0, 0, 255)
OUTPUT_FOLDER_NAME = "red_black_parts"


def choose_images():
    root = tk.Tk()
    root.withdraw()
    root.update()

    image_paths = filedialog.askopenfilenames(
        title="Select image(s) to colour correct",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()
    return list(image_paths)


def make_black_parts_red(image):
    # A pixel is treated as black when all three colour channels are dark.
    black_mask = np.all(image <= BLACK_THRESHOLD, axis=2)

    # Also catch dark red pixels that are too red to pass the all-channel black
    # check, but still need to be normalized to bright red.
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    saturation = hsv[:, :, 1]
    brightness = hsv[:, :, 2]
    red_hue_mask = (hue <= DARK_RED_HUE_RANGE) | (hue >= 180 - DARK_RED_HUE_RANGE)
    dark_red_mask = (
        red_hue_mask
        & (saturation >= DARK_RED_MIN_SATURATION)
        & (brightness <= DARK_RED_MAX_BRIGHTNESS)
    )
    blue = image[:, :, 0]
    green = image[:, :, 1]
    red = image[:, :, 2]
    red_dominant_dark_mask = (
        (brightness <= DARK_RED_MAX_BRIGHTNESS)
        & (red >= green + RED_DOMINANCE_MARGIN)
        & (red >= blue + RED_DOMINANCE_MARGIN)
    )

    corrected = image.copy()
    corrected[black_mask | dark_red_mask | red_dominant_dark_mask] = RED_BGR
    return corrected


def output_path_for(image_path):
    source_folder = os.path.dirname(image_path)
    output_folder = os.path.join(source_folder, OUTPUT_FOLDER_NAME)
    os.makedirs(output_folder, exist_ok=True)

    base_name, extension = os.path.splitext(os.path.basename(image_path))
    if extension.lower() not in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"):
        extension = ".png"

    return os.path.join(output_folder, f"{base_name}_black_to_red{extension}")


def process_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    corrected = make_black_parts_red(image)
    save_path = output_path_for(image_path)

    if not cv2.imwrite(save_path, corrected):
        raise ValueError(f"Could not save image: {save_path}")

    return save_path


def main():
    image_paths = choose_images()
    if not image_paths:
        print("No images selected.")
        return

    saved_paths = []
    failed_paths = []

    for image_path in image_paths:
        try:
            saved_paths.append(process_image(image_path))
        except Exception as error:
            failed_paths.append(f"{image_path}\n  {error}")

    if saved_paths:
        print("Saved corrected images:")
        for save_path in saved_paths:
            print(save_path)

    if failed_paths:
        print("\nImages that could not be processed:")
        for failed_path in failed_paths:
            print(failed_path)

    message = f"Saved {len(saved_paths)} corrected image(s)."
    if failed_paths:
        message += f"\n\nCould not process {len(failed_paths)} image(s). Check the terminal for details."
        messagebox.showwarning("Colour correction finished", message)
    else:
        messagebox.showinfo("Colour correction finished", message)


if __name__ == "__main__":
    main()
