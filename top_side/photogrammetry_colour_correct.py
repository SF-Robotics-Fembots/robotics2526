import base64
import os
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
import numpy as np

try:
    from .undistort_batch import (
        CALIBRATION_CSV,
        read_calibration_csv,
        undistort_image,
    )
except ImportError:
    from undistort_batch import (
        CALIBRATION_CSV,
        read_calibration_csv,
        undistort_image,
    )


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
DEFAULT_MIN_BRIGHTNESS = 0
DEFAULT_MAX_BRIGHTNESS = 70
DEFAULT_FILL_TOLERANCE = 12
RED_BGR = (0, 0, 255)
OUTPUT_FOLDER_NAME = "red_black_parts"
PREVIEW_MAX_WIDTH = 850
PREVIEW_MAX_HEIGHT = 360


def choose_source_folder():
    root = tk.Tk()
    root.withdraw()
    root.update()
    folder_path = filedialog.askdirectory(
        title="Select folder containing images to process"
    )
    root.destroy()
    return folder_path


def choose_images(source_folder):
    root = tk.Tk()
    root.withdraw()
    root.update()
    image_paths = filedialog.askopenfilenames(
        title="Select image(s) to turn dark areas red",
        initialdir=source_folder,
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return list(image_paths)


def make_output_folder(input_folder):
    output_folder = os.path.join(input_folder, OUTPUT_FOLDER_NAME)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder


def flood_fill_mask(image, normalized_seeds, tolerance):
    """Return connected regions with brightness similar to each clicked seed."""
    brightness = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:, :, 2]
    height, width = brightness.shape
    combined_mask = np.zeros((height, width), dtype=bool)

    for normalized_x, normalized_y in normalized_seeds:
        seed_x = min(width - 1, max(0, round(normalized_x * (width - 1))))
        seed_y = min(height - 1, max(0, round(normalized_y * (height - 1))))
        flood_mask = np.zeros((height + 2, width + 2), dtype=np.uint8)
        flags = (
            4
            | cv2.FLOODFILL_MASK_ONLY
            | cv2.FLOODFILL_FIXED_RANGE
            | (255 << 8)
        )
        cv2.floodFill(
            brightness.copy(),
            flood_mask,
            (seed_x, seed_y),
            0,
            loDiff=tolerance,
            upDiff=tolerance,
            flags=flags,
        )
        combined_mask |= flood_mask[1:-1, 1:-1] != 0

    return combined_mask


def brightness_range_mask(image, min_brightness, max_brightness):
    brightness = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:, :, 2]
    return (brightness >= min_brightness) & (brightness <= max_brightness)


def make_selected_parts_red(
    image,
    min_brightness,
    max_brightness,
    normalized_seeds,
    tolerance,
):
    corrected = image.copy()
    selected_mask = brightness_range_mask(
        image,
        min_brightness,
        max_brightness,
    )
    selected_mask |= flood_fill_mask(image, normalized_seeds, tolerance)
    corrected[selected_mask] = RED_BGR
    return corrected


def image_to_tk(image):
    success, encoded = cv2.imencode(".png", image)
    if not success:
        raise ValueError("Could not create fill preview.")
    data = base64.b64encode(encoded.tobytes()).decode("ascii")
    return tk.PhotoImage(data=data, format="png")


def choose_fill_settings(first_image_path):
    image = cv2.imread(first_image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not load preview image: {first_image_path}")

    result = {"settings": None}
    normalized_seeds = []

    window = tk.Tk()
    window.title("Choose areas to change to red")
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(
        f"{min(900, screen_width - 80)}x{min(720, screen_height - 100)}"
    )
    window.minsize(520, 500)

    tk.Label(
        window,
        text=(
            "First adjust the brightness range applied to every image.\n"
            "Then click the red preview to fill additional connected areas."
        ),
        justify="center",
    ).pack(padx=12, pady=(10, 5))

    available_width = max(300, min(PREVIEW_MAX_WIDTH, screen_width - 140))
    available_height = max(180, min(PREVIEW_MAX_HEIGHT, screen_height - 450))
    height, width = image.shape[:2]
    scale = min(available_width / width, available_height / height, 1.0)
    preview_size = max(1, round(width * scale)), max(1, round(height * scale))
    preview_image = cv2.resize(image, preview_size, interpolation=cv2.INTER_AREA)

    preview_label = tk.Label(window, cursor="crosshair")
    min_value = tk.IntVar(value=DEFAULT_MIN_BRIGHTNESS)
    max_value = tk.IntVar(value=DEFAULT_MAX_BRIGHTNESS)
    tolerance_value = tk.IntVar(value=DEFAULT_FILL_TOLERANCE)
    selection_label = tk.Label(window)

    def update_preview(_value=None):
        minimum = min_value.get()
        maximum = max_value.get()
        if minimum > maximum:
            selection_label.config(
                text="Minimum brightness must not exceed maximum brightness.",
                fg="red",
            )
            return

        range_mask = brightness_range_mask(
            preview_image,
            minimum,
            maximum,
        )
        fill_mask = flood_fill_mask(
            preview_image,
            normalized_seeds,
            tolerance_value.get(),
        )
        selected_mask = range_mask | fill_mask
        corrected = preview_image.copy()
        corrected[selected_mask] = RED_BGR
        tk_image = image_to_tk(corrected)
        preview_label.configure(image=tk_image)
        preview_label.image = tk_image
        changed_percent = np.count_nonzero(selected_mask) / selected_mask.size * 100
        selection_label.config(
            text=(
                f"Brightness {minimum}-{maximum} | "
                f"{len(normalized_seeds)} extra fill point(s) | "
                f"{changed_percent:.1f}% selected"
            ),
            fg="black",
        )

    def add_fill_point(event):
        preview_width, preview_height = preview_size
        if 0 <= event.x < preview_width and 0 <= event.y < preview_height:
            normalized_seeds.append(
                (
                    event.x / max(1, preview_width - 1),
                    event.y / max(1, preview_height - 1),
                )
            )
            update_preview()

    def undo_fill_point():
        if normalized_seeds:
            normalized_seeds.pop()
            update_preview()

    def clear_fill_points():
        normalized_seeds.clear()
        update_preview()

    def confirm():
        if min_value.get() > max_value.get():
            messagebox.showerror(
                "Invalid range",
                "Minimum brightness must not exceed maximum brightness.",
                parent=window,
            )
            return
        result["settings"] = (
            min_value.get(),
            max_value.get(),
            list(normalized_seeds),
            tolerance_value.get(),
        )
        window.destroy()

    def cancel():
        window.destroy()

    controls = tk.Frame(window)
    controls.pack(fill="x", padx=12)
    tk.Label(controls, text="Minimum brightness").pack(anchor="w")
    tk.Scale(
        controls,
        from_=0,
        to=255,
        orient="horizontal",
        variable=min_value,
        command=update_preview,
    ).pack(fill="x")
    tk.Label(controls, text="Maximum brightness").pack(anchor="w")
    tk.Scale(
        controls,
        from_=0,
        to=255,
        orient="horizontal",
        variable=max_value,
        command=update_preview,
    ).pack(fill="x")
    tk.Label(
        controls,
        text="Fill similarity tolerance",
    ).pack(anchor="w")
    tk.Scale(
        controls,
        from_=0,
        to=80,
        orient="horizontal",
        variable=tolerance_value,
        command=update_preview,
    ).pack(fill="x")
    selection_label.pack(pady=3)

    buttons = tk.Frame(window)
    buttons.pack(pady=(2, 8))
    tk.Button(
        buttons,
        text="Confirm and Process All Images",
        command=confirm,
        padx=10,
        pady=4,
    ).pack(side="left", padx=4)
    tk.Button(buttons, text="Undo Click", command=undo_fill_point).pack(
        side="left", padx=4
    )
    tk.Button(buttons, text="Clear", command=clear_fill_points).pack(
        side="left", padx=4
    )
    tk.Button(buttons, text="Cancel", command=cancel).pack(side="left", padx=4)

    preview_label.pack(padx=12, pady=5)
    preview_label.bind("<Button-1>", add_fill_point)
    window.protocol("WM_DELETE_WINDOW", cancel)
    window.bind("<Return>", lambda _event: confirm())
    window.bind("<Escape>", lambda _event: cancel())
    update_preview()
    window.mainloop()
    return result["settings"]


def output_path_for(image_path, output_folder):
    base_name, extension = os.path.splitext(os.path.basename(image_path))
    if extension.lower() not in IMAGE_EXTENSIONS:
        extension = ".png"
    return os.path.join(output_folder, f"{base_name}_fill_to_red{extension}")


def process_image(
    image_path,
    output_folder,
    min_brightness,
    max_brightness,
    normalized_seeds,
    tolerance,
    camera_matrix,
    distortion_coefficients,
    calibration_size,
):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    height, width = image.shape[:2]
    if calibration_size is not None and (width, height) != calibration_size:
        raise ValueError(
            f"resolution {width}x{height} does not match calibration "
            f"{calibration_size[0]}x{calibration_size[1]}"
        )

    corrected = make_selected_parts_red(
        image,
        min_brightness,
        max_brightness,
        normalized_seeds,
        tolerance,
    )
    corrected = undistort_image(
        corrected,
        camera_matrix,
        distortion_coefficients,
    )
    save_path = output_path_for(image_path, output_folder)
    if not cv2.imwrite(save_path, corrected):
        raise ValueError(f"Could not save image: {save_path}")
    return save_path


def main():
    source_folder = choose_source_folder()
    if not source_folder:
        print("No folder selected.")
        return

    image_paths = choose_images(source_folder)
    if not image_paths:
        print("No images selected.")
        return

    fill_settings = choose_fill_settings(image_paths[0])
    if fill_settings is None:
        print("Fill selection cancelled.")
        return
    min_brightness, max_brightness, normalized_seeds, tolerance = fill_settings

    try:
        calibration = read_calibration_csv(CALIBRATION_CSV)
        camera_matrix = calibration["camera_matrix"]
        distortion_coefficients = calibration["distortion_coefficients"]
        frame_size = calibration.get("frame_size")
        calibration_size = (
            (int(frame_size[0]), int(frame_size[1]))
            if frame_size is not None
            else None
        )
    except Exception as error:
        messagebox.showerror(
            "Calibration",
            f"Could not read camera calibration:\n{error}",
        )
        return

    output_folder = make_output_folder(source_folder)
    saved_paths = []
    failed_paths = []

    for image_path in image_paths:
        try:
            saved_paths.append(
                process_image(
                    image_path,
                    output_folder,
                    min_brightness,
                    max_brightness,
                    normalized_seeds,
                    tolerance,
                    camera_matrix,
                    distortion_coefficients,
                    calibration_size,
                )
            )
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

    message = (
        f"Applied brightness range {min_brightness}-{max_brightness} and "
        f"{len(normalized_seeds)} extra fill point(s).\n"
        "Undistorted each image using the saved camera calibration.\n\n"
        f"Saved {len(saved_paths)} corrected image(s) to:\n"
        f"{output_folder}"
    )
    if failed_paths:
        message += (
            f"\n\nCould not process {len(failed_paths)} image(s). "
            "Check the terminal for details."
        )
        messagebox.showwarning("Colour correction finished", message)
    else:
        messagebox.showinfo("Colour correction finished", message)


if __name__ == "__main__":
    main()
