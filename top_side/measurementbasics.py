import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import csv
import os
import datetime
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_CSV = os.path.join(BASE_DIR, "camera_calibration", "camera_calibration_params.csv")

# Open file chooser dialog
root = tk.Tk()
root.withdraw()
image_path = filedialog.askopenfilename(
    title="Select an Image",
    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
)

if not image_path:
    print("No file selected.")
    exit()

img = cv2.imread(image_path)
if img is None:
    print(f"Error: Could not load {image_path}")
    exit()

h, w = img.shape[:2]
filename = image_path.split("/")[-1].split("\\")[-1]
mtime = os.path.getmtime(image_path)
file_datetime = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d  %H:%M:%S")

KNOWN_DISTANCE_MM = 125.0
ZOOM_STEP      = 1.2
ZOOM_MIN       = 1.0
ZOOM_MAX       = 20.0

font      = cv2.FONT_HERSHEY_SIMPLEX
scale     = 0.62
small_scale = 0.52
button_scale = 0.68
thickness = 1
padding   = 8
line_type = cv2.LINE_AA

PAIR_COLORS = [
    (0,   255, 255),   # yellow  — calibration
    (255, 255,   0),   # cyan    — measurement
    (255,   0, 255),   # magenta
    (0,   165, 255),   # orange
    (0,   255,   0),   # green
]

WINDOW_NAME    = "Image Viewer"
clicks         = []
ticker         = []
pixels_per_mm = [None]
undistort_button_rect = [None]

# Zoom / pan state
zoom_level     = 1.0
view_x         = 0.0   # top-left of visible region in original image coords
view_y         = 0.0
pan_start      = [None]
pan_view_start = [None]

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

def reset_image_state(new_img, new_filename=None):
    global img, h, w, filename, zoom_level, view_x, view_y
    img = new_img
    h, w = img.shape[:2]
    if new_filename is not None:
        filename = new_filename

    clicks.clear()
    ticker.clear()
    pixels_per_mm[0] = None
    zoom_level = 1.0
    view_x = 0.0
    view_y = 0.0

def undistort_loaded_image():
    try:
        calibration = read_calibration_csv(CALIBRATION_CSV)
        camera_matrix = calibration["camera_matrix"]
        distortion_coefficients = calibration["distortion_coefficients"]

        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix,
            distortion_coefficients,
            (w, h),
            1,
            (w, h),
        )
        undistorted = cv2.undistort(img, camera_matrix, distortion_coefficients, None, new_camera_matrix)

        x, y, roi_w, roi_h = roi
        if roi_w > 0 and roi_h > 0:
            undistorted = undistorted[y:y + roi_h, x:x + roi_w]

        reset_image_state(undistorted, f"undistorted_{filename}")
        ticker.append(("Image undistorted using saved calibration", (0, 255, 0)))
        cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
        print("Image undistorted using:", CALIBRATION_CSV)
    except Exception as error:
        message = f"Could not undistort image: {error}"
        print(message)
        messagebox.showerror("Undistort Image", message)

def pair_color(i):
    return PAIR_COLORS[(i // 2) % len(PAIR_COLORS)]

def px_distance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5

def draw_filled_rect_alpha(out, top_left, bottom_right, color, alpha):
    overlay = out.copy()
    cv2.rectangle(overlay, top_left, bottom_right, color, -1)
    cv2.addWeighted(overlay, alpha, out, 1 - alpha, 0, out)

def draw_text_panel(out, lines, anchor, align="left", vertical_align="top", panel_color=(20, 20, 20), alpha=0.78):
    text_sizes = [cv2.getTextSize(line, font, small_scale, thickness)[0] for line in lines]
    max_width = max((size[0] for size in text_sizes), default=0)
    line_height = max((size[1] for size in text_sizes), default=14) + padding
    panel_width = max_width + padding * 3
    panel_height = line_height * len(lines) + padding

    ax, ay = anchor
    if align == "right":
        x1 = ax - panel_width
    else:
        x1 = ax
    if vertical_align == "bottom":
        y1 = ay - panel_height
    else:
        y1 = ay
    x2 = x1 + panel_width
    y2 = y1 + panel_height

    draw_filled_rect_alpha(out, (x1, y1), (x2, y2), panel_color, alpha)
    cv2.rectangle(out, (x1, y1), (x2, y2), (80, 80, 80), 1, line_type)

    for i, line in enumerate(lines):
        y = y1 + padding + (i + 1) * line_height - padding // 2
        cv2.putText(out, line, (x1 + padding * 2, y), font, small_scale, (245,245,245), thickness, line_type)

def get_undistort_button_rect():
    label = "Undistort Image"
    (tw, th), _ = cv2.getTextSize(label, font, button_scale, thickness)
    x1 = padding * 2
    y1 = padding * 2
    x2 = x1 + tw + padding * 5
    y2 = y1 + th + padding * 4
    return label, (x1, y1, x2, y2)

def is_inside_rect(x, y, rect):
    if rect is None:
        return False
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2

def get_display_size():
    rect = cv2.getWindowImageRect(WINDOW_NAME)
    dw, dh = rect[2], rect[3]
    return (dw, dh) if dw > 0 and dh > 0 else (w, h)

def clamp_view():
    global view_x, view_y
    view_x = max(0.0, min(view_x, w - w / zoom_level))
    view_y = max(0.0, min(view_y, h - h / zoom_level))

def display_to_orig(dx, dy, dw, dh):
    return (
        int(view_x + dx * (w / zoom_level) / dw),
        int(view_y + dy * (h / zoom_level) / dh),
    )

def orig_to_display(ox, oy, dw, dh):
    return (
        int((ox - view_x) * zoom_level * dw / w),
        int((oy - view_y) * zoom_level * dh / h),
    )

def draw_frame(dw, dh):
    x1 = max(0, int(view_x))
    y1 = max(0, int(view_y))
    x2 = min(w, int(view_x + w / zoom_level) + 1)
    y2 = min(h, int(view_y + h / zoom_level) + 1)
    out = cv2.resize(img[y1:y2, x1:x2], (dw, dh), interpolation=cv2.INTER_LINEAR)

    # --- Click dots ---
    for idx, (ox, oy) in enumerate(clicks):
        dx, dy = orig_to_display(ox, oy, dw, dh)
        if 0 <= dx < dw and 0 <= dy < dh:
            cv2.circle(out, (dx, dy), 5, pair_color(idx), -1)

    # --- Undistort button ---
    label, button_rect = get_undistort_button_rect()
    undistort_button_rect[0] = button_rect
    bx1, by1, bx2, by2 = button_rect
    draw_filled_rect_alpha(out, (bx1, by1), (bx2, by2), (32, 74, 104), 0.88)
    cv2.rectangle(out, (bx1, by1), (bx2, by2), (180, 225, 245), 1, line_type)
    cv2.putText(out, label, (bx1 + padding * 2, by2 - padding * 2), font, button_scale, (255,255,255), thickness, line_type)

    # --- Lower-right info label ---
    info_lines = [filename, f"{w} x {h}", file_datetime, f"Zoom {zoom_level:.1f}x"]
    text_sizes = [cv2.getTextSize(line, font, small_scale, thickness)[0] for line in info_lines]
    panel_height = (max(size[1] for size in text_sizes) + padding) * len(info_lines) + padding
    draw_text_panel(out, info_lines, (dw - padding * 2, dh - padding * 2), align="right", vertical_align="bottom")

    # --- Upper-right ticker ---
    if ticker:
        visible_ticker = ticker[-8:]
        ticker_lines = [line for line, _color in visible_ticker]
        text_sizes = [cv2.getTextSize(line, font, small_scale, thickness)[0] for line in ticker_lines]
        max_width = max(size[0] for size in text_sizes)
        line_height = max(size[1] for size in text_sizes) + padding
        panel_width = max_width + padding * 3
        panel_height = line_height * len(visible_ticker) + padding
        x1 = dw - panel_width - padding * 2
        y1 = padding * 2
        x2 = x1 + panel_width
        y2 = y1 + panel_height
        draw_filled_rect_alpha(out, (x1, y1), (x2, y2), (20, 20, 20), 0.78)
        cv2.rectangle(out, (x1, y1), (x2, y2), (80, 80, 80), 1, line_type)
        for i, (line, color) in enumerate(visible_ticker):
            ly = y1 + padding + (i + 1) * line_height - padding // 2
            cv2.putText(out, line, (x1 + padding * 2, ly), font, small_scale, color, thickness, line_type)

    return out

def mouse_callback(event, x, y, flags, _param):
    global zoom_level, view_x, view_y
    dw, dh = get_display_size()

    # --- Scroll wheel: zoom centered on cursor ---
    if event == cv2.EVENT_MOUSEWHEEL:
        old_zoom = zoom_level
        zoom_level = min(zoom_level * ZOOM_STEP, ZOOM_MAX) if flags > 0 \
                     else max(zoom_level / ZOOM_STEP, ZOOM_MIN)
        view_x += x * (w / dw) * (1/old_zoom - 1/zoom_level)
        view_y += y * (h / dh) * (1/old_zoom - 1/zoom_level)
        clamp_view()
        cv2.imshow(WINDOW_NAME, draw_frame(dw, dh))

    # --- Right-click drag: pan ---
    elif event == cv2.EVENT_RBUTTONDOWN:
        pan_start[0]      = (x, y)
        pan_view_start[0] = (view_x, view_y)

    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_RBUTTON):
        if pan_start[0]:
            view_x = pan_view_start[0][0] - (x - pan_start[0][0]) * (w / zoom_level) / dw
            view_y = pan_view_start[0][1] - (y - pan_start[0][1]) * (h / zoom_level) / dh
            clamp_view()
            cv2.imshow(WINDOW_NAME, draw_frame(dw, dh))

    elif event == cv2.EVENT_RBUTTONUP:
        pan_start[0] = None

    # --- Left-click: measurement point ---
    elif event == cv2.EVENT_LBUTTONDOWN:
        if is_inside_rect(x, y, undistort_button_rect[0]):
            undistort_loaded_image()
            return

        orig_x, orig_y = display_to_orig(x, y, dw, dh)
        idx        = len(clicks)
        pair       = idx // 2
        pt_in_pair = idx % 2 + 1
        color      = pair_color(idx)

        clicks.append((orig_x, orig_y))
        ticker.append((f"M{pair+1}.P{pt_in_pair}: ({orig_x}, {orig_y})", color))

        if pt_in_pair == 2:
            dist_px = px_distance(clicks[-2], clicks[-1])
            if pair == 0:
                pixels_per_mm[0] = dist_px / KNOWN_DISTANCE_MM
                line = f"  {dist_px:.1f}px = {KNOWN_DISTANCE_MM:.1f}mm  ->  {pixels_per_mm[0]:.2f}px/mm"
            elif pixels_per_mm[0]:
                millimeters = dist_px / pixels_per_mm[0]
                line = f"  {dist_px:.1f}px  ->  {millimeters:.2f} mm"
            else:
                line = f"  {dist_px:.1f}px  (calibrate yellow first)"
            ticker.append((line, color))
            print(line)

        cv2.imshow(WINDOW_NAME, draw_frame(dw, dh))

# --- Init ---
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
init_w = min(w, 1200)
init_h = int(h * init_w / w)
cv2.resizeWindow(WINDOW_NAME, init_w, init_h)
cv2.imshow(WINDOW_NAME, draw_frame(init_w, init_h))
cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

print(f"Showing: {image_path}  ({w}x{h})")
print("Scroll: zoom  |  Right-drag: pan  |  R: reset zoom  |  Left-click: measure")

prev_size = (init_w, init_h)
while True:
    key = cv2.waitKey(50)
    if key == ord('r'):          # reset zoom
        zoom_level, view_x, view_y = 1.0, 0.0, 0.0
        cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
    elif key != -1:
        break
    curr_size = get_display_size()
    if curr_size != prev_size:
        prev_size = curr_size
        cv2.imshow(WINDOW_NAME, draw_frame(*curr_size))

cv2.destroyAllWindows()
root.destroy()
