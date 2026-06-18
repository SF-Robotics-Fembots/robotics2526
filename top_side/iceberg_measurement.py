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
    title="Select the First Photo",
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

FIRST_REFERENCE_MM = 21.336
ZOOM_STEP      = 1.2
ZOOM_MIN       = 1.0
ZOOM_MAX       = 20.0

# CLAHE (on LAB L channel) tuning: raise clip limit if edges stay flat,
# lower it if noise gets amplified.
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID  = (8, 8)

# Homography rectification: real-world size of the measurement block whose four
# corners get clicked (clicked order: top-left, top-right, bottom-right, bottom-left).
BLOCK_WIDTH_MM   = 125.0
BLOCK_HEIGHT_MM  = 27.0
RECTIFY_PX_PER_MM = 4.0    # fixed output resolution of the rectified image
RECTIFY_MARGIN_MM = 150.0  # real-world area kept around the block on every side
RECTIFY_MAX_DIM   = 5000   # cap the canvas (px) so a huge margin can't blow up memory

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
click_ticker_counts = []   # parallel to clicks: ticker lines each click appended (for undo)
pixels_per_mm = [None]
photo_number = [1]
second_photo_reference_mm = [None]
undistort_button_rect = [None]
undo_button_rect = [None]
save_button_rect = [None]
white_balance_button_rect = [None]
clahe_button_rect = [None]
rectify_button_rect = [None]
has_undistorted = [False]   # image may only be undistorted once
undistorted_img = [None]    # holds the undistorted image awaiting a manual save
base_img = [img.copy()]     # image without WB/CLAHE/rectify toggles applied
wb_enabled = [False]        # gray-world white balance toggle
clahe_enabled = [False]     # CLAHE contrast toggle

# Homography rectification state
rectify_enabled   = [False]   # show rectified (warped) view
rectify_pick_mode = [False]   # currently clicking the 4 block corners
rectify_corners   = []        # up to 4 (x, y) corner points in base-image coords
rectify_H         = [None]    # 3x3 homography (base coords -> rectified canvas)
rectify_size      = [None]    # (out_w, out_h) of the rectified canvas
rectify_scale     = [None]    # px per mm in the rectified image (auto from block)

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
    global img, h, w, filename, file_datetime, zoom_level, view_x, view_y
    img = new_img
    h, w = img.shape[:2]
    if new_filename is not None:
        filename = new_filename
    if image_path and os.path.exists(image_path):
        mtime = os.path.getmtime(image_path)
        file_datetime = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d  %H:%M:%S")

    clicks.clear()
    ticker.clear()
    click_ticker_counts.clear()
    pixels_per_mm[0] = None
    zoom_level = 1.0
    view_x = 0.0
    view_y = 0.0

    # new underlying image becomes the unadjusted base; toggles start off
    base_img[0] = new_img.copy()
    wb_enabled[0] = False
    clahe_enabled[0] = False

def load_second_photo():
    global image_path
    if second_photo_reference_mm[0] is None:
        messagebox.showinfo(
            "Second Photo",
            "Measure the reference object in the first photo before loading the second photo.",
        )
        return

    next_path = filedialog.askopenfilename(
        title=f"Select the Second Photo (reference: {second_photo_reference_mm[0]:.3f} mm)",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")],
    )
    if not next_path:
        ticker.append(("Second photo not selected; press N to try again", (0, 200, 255)))
        cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
        return

    next_img = cv2.imread(next_path)
    if next_img is None:
        messagebox.showerror("Second Photo", f"Could not load {next_path}")
        return

    image_path = next_path
    photo_number[0] = 2
    has_undistorted[0] = False
    undistorted_img[0] = None
    rectify_enabled[0] = False
    rectify_pick_mode[0] = False
    rectify_corners.clear()
    rectify_H[0] = None
    rectify_size[0] = None
    rectify_scale[0] = None
    reset_image_state(next_img, os.path.basename(next_path))
    ticker.append((f"Photo 2 reference: {second_photo_reference_mm[0]:.3f} mm", (0, 255, 255)))
    cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
    print(f"Showing second photo: {image_path}  ({w}x{h})")

def undo_last_click():
    if not clicks:
        return
    clicks.pop()
    removed_lines = click_ticker_counts.pop() if click_ticker_counts else 1
    for _ in range(removed_lines):
        if ticker:
            ticker.pop()
    # calibration (yellow pair) is only valid once its 2 points exist
    if len(clicks) < 2:
        pixels_per_mm[0] = None
    if photo_number[0] == 1 and len(clicks) < 4:
        second_photo_reference_mm[0] = None
    cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))

def undistort_loaded_image():
    if has_undistorted[0]:
        return
    try:
        calibration = read_calibration_csv(CALIBRATION_CSV)
        camera_matrix = calibration["camera_matrix"]
        distortion_coefficients = calibration["distortion_coefficients"]

        # alpha=0 keeps the principal point centered and fills the frame. (alpha=1
        # pushes the corrected principal point off the right edge with this
        # calibration, squishing all content to one side.)
        new_camera_matrix, _roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix,
            distortion_coefficients,
            (w, h),
            0,
            (w, h),
        )
        undistorted = cv2.undistort(img, camera_matrix, distortion_coefficients, None, new_camera_matrix)

        undistorted_img[0] = undistorted   # stash for manual save via the Save button
        reset_image_state(undistorted, f"undistorted_{filename}")
        has_undistorted[0] = True
        ticker.append(("Image undistorted using saved calibration", (0, 255, 0)))
        ticker.append(("Press Save Image to write it to disk", (0, 255, 0)))
        cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
        print("Image undistorted using:", CALIBRATION_CSV)
    except Exception as error:
        message = f"Could not undistort image: {error}"
        print(message)
        messagebox.showerror("Undistort Image", message)

def save_undistorted_image():
    if undistorted_img[0] is None:
        return
    try:
        # Save to the same folder the original image came from.
        source_dir = os.path.dirname(image_path)
        base_name, ext = os.path.splitext(os.path.basename(image_path))
        if ext.lower() not in (".jpg", ".jpeg", ".png", ".bmp", ".tiff"):
            ext = ".png"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(source_dir, f"undistorted_{base_name}_{timestamp}{ext}")
        cv2.imwrite(save_path, undistorted_img[0])
        ticker.append((f"Saved: {os.path.basename(save_path)}", (0, 255, 0)))
        cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
        print("Saved undistorted image to:", save_path)
    except Exception as error:
        message = f"Could not save image: {error}"
        print(message)
        messagebox.showerror("Save Image", message)

def gray_world(image):
    # Gray-world white balance: scale each channel so its mean matches the
    # overall gray mean, removing the blue-green underwater color cast.
    balanced = image.astype(np.float32)
    means = [balanced[:, :, c].mean() for c in range(3)]
    gray_mean = sum(means) / 3.0
    for c in range(3):
        if means[c] > 1e-6:
            balanced[:, :, c] *= gray_mean / means[c]
    return np.clip(balanced, 0, 255).astype(np.uint8)

def clahe_l_channel(image):
    # CLAHE on the L (lightness) channel in LAB space — boosts local contrast
    # without shifting colors, since a and b are left untouched.
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID)
    l_channel = clahe.apply(l_channel)
    return cv2.cvtColor(cv2.merge((l_channel, a_channel, b_channel)), cv2.COLOR_LAB2BGR)

def recompute_image():
    # Rebuild the displayed image from the unadjusted base, applying whichever
    # toggles are on: rectify (geometry) first, then white balance, then CLAHE.
    global img, w, h, zoom_level, view_x, view_y
    if base_img[0] is None:
        return

    if rectify_enabled[0] and rectify_H[0] is not None:
        result = cv2.warpPerspective(base_img[0], rectify_H[0], rectify_size[0])
    else:
        result = base_img[0].copy()
    if wb_enabled[0]:
        result = gray_world(result)
    if clahe_enabled[0]:
        result = clahe_l_channel(result)

    # Rectify changes the image dimensions/coordinate system, so when geometry
    # changes we reset the view and drop measurements taken in the old frame.
    new_h, new_w = result.shape[:2]
    if (new_w, new_h) != (w, h):
        w, h = new_w, new_h
        zoom_level = 1.0
        view_x = 0.0
        view_y = 0.0
        clicks.clear()
        click_ticker_counts.clear()
        pixels_per_mm[0] = None

    img = result
    # rectified view has a uniform, known scale derived from the block
    if rectify_enabled[0] and rectify_scale[0] is not None:
        pixels_per_mm[0] = rectify_scale[0]
    # keep the stashed copy in sync so a later save reflects the toggles
    if undistorted_img[0] is not None:
        undistorted_img[0] = result
    cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))

def toggle_white_balance():
    wb_enabled[0] = not wb_enabled[0]
    ticker.append((f"White balance {'ON' if wb_enabled[0] else 'OFF'}", (0, 255, 0)))
    recompute_image()
    print(f"White balance {'ON' if wb_enabled[0] else 'OFF'}")

def toggle_clahe():
    clahe_enabled[0] = not clahe_enabled[0]
    ticker.append((f"CLAHE {'ON' if clahe_enabled[0] else 'OFF'}", (0, 255, 0)))
    recompute_image()
    print(f"CLAHE {'ON' if clahe_enabled[0] else 'OFF'}")

def compute_rectification():
    # Map the four clicked block corners to a fronto-parallel rectangle of the
    # block's true proportions, placed inside a fixed-size canvas defined in
    # real-world space (block + margin). Sizing the output in mm-space — rather
    # than from the warped image extent — keeps it robust at grazing angles,
    # where the far plane would otherwise blow up and collapse the scale.
    src = np.array(rectify_corners, dtype=np.float32)   # TL, TR, BR, BL

    span_w_mm = BLOCK_WIDTH_MM + 2 * RECTIFY_MARGIN_MM
    span_h_mm = BLOCK_HEIGHT_MM + 2 * RECTIFY_MARGIN_MM
    # fixed resolution, clamped so a large margin can't exceed the canvas cap
    scale = min(RECTIFY_PX_PER_MM, RECTIFY_MAX_DIM / max(span_w_mm, span_h_mm))

    offset = RECTIFY_MARGIN_MM * scale
    block_w_px = BLOCK_WIDTH_MM * scale
    block_h_px = BLOCK_HEIGHT_MM * scale
    dst = np.array([
        [offset,              offset],
        [offset + block_w_px, offset],
        [offset + block_w_px, offset + block_h_px],
        [offset,              offset + block_h_px],
    ], dtype=np.float32)

    rectify_H[0]     = cv2.getPerspectiveTransform(src, dst)
    rectify_size[0]  = (int(round(span_w_mm * scale)), int(round(span_h_mm * scale)))
    rectify_scale[0] = scale

def start_rectify_pick():
    # pick corners on the un-rectified geometry
    if rectify_enabled[0]:
        rectify_enabled[0] = False
        recompute_image()
    rectify_pick_mode[0] = True
    rectify_corners.clear()
    ticker.append(("Click block corners: TL, TR, BR, BL", (0, 200, 255)))
    cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))

def toggle_rectify():
    if rectify_H[0] is None:
        return
    rectify_enabled[0] = not rectify_enabled[0]
    ticker.append((f"Rectify {'ON' if rectify_enabled[0] else 'OFF'}", (0, 255, 0)))
    recompute_image()
    print(f"Rectify {'ON' if rectify_enabled[0] else 'OFF'}")

def rectify_button_action():
    if rectify_pick_mode[0]:
        # cancel an in-progress pick
        rectify_pick_mode[0] = False
        rectify_corners.clear()
        ticker.append(("Rectify pick cancelled", (0, 200, 255)))
        cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
    elif rectify_H[0] is None:
        start_rectify_pick()
    else:
        toggle_rectify()

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

def get_undo_button_rect():
    label = "Undo Click"
    (tw, th), _ = cv2.getTextSize(label, font, button_scale, thickness)
    # sit directly below the undistort button, sharing the same left edge
    _, (ux1, _uy1, _ux2, uy2) = get_undistort_button_rect()
    x1 = ux1
    y1 = uy2 + padding
    x2 = x1 + tw + padding * 5
    y2 = y1 + th + padding * 4
    return label, (x1, y1, x2, y2)

def get_save_button_rect():
    label = "Save Image"
    (tw, th), _ = cv2.getTextSize(label, font, button_scale, thickness)
    # sit directly below the undo button, sharing the same left edge
    _, (sx1, _sy1, _sx2, sy2) = get_undo_button_rect()
    x1 = sx1
    y1 = sy2 + padding
    x2 = x1 + tw + padding * 5
    y2 = y1 + th + padding * 4
    return label, (x1, y1, x2, y2)

def get_white_balance_button_rect():
    label = "White Balance"
    (tw, th), _ = cv2.getTextSize(label, font, button_scale, thickness)
    # sit directly below the save button, sharing the same left edge
    _, (wx1, _wy1, _wx2, wy2) = get_save_button_rect()
    x1 = wx1
    y1 = wy2 + padding
    x2 = x1 + tw + padding * 5
    y2 = y1 + th + padding * 4
    return label, (x1, y1, x2, y2)

def get_clahe_button_rect():
    label = "CLAHE Contrast"
    (tw, th), _ = cv2.getTextSize(label, font, button_scale, thickness)
    # sit directly below the white balance button, sharing the same left edge
    _, (cx1, _cy1, _cx2, cy2) = get_white_balance_button_rect()
    x1 = cx1
    y1 = cy2 + padding
    x2 = x1 + tw + padding * 5
    y2 = y1 + th + padding * 4
    return label, (x1, y1, x2, y2)

def get_rectify_button_label():
    if rectify_pick_mode[0]:
        return f"Picking corner {len(rectify_corners) + 1}/4"
    if rectify_H[0] is None:
        return "Rectify Block"
    return "Rectify: ON" if rectify_enabled[0] else "Rectify: OFF"

def get_rectify_button_rect():
    # width sized to the longest possible label so the box doesn't jump around
    (tw, th), _ = cv2.getTextSize("Picking corner 4/4", font, button_scale, thickness)
    # sit directly below the CLAHE button, sharing the same left edge
    _, (rx1, _ry1, _rx2, ry2) = get_clahe_button_rect()
    x1 = rx1
    y1 = ry2 + padding
    x2 = x1 + tw + padding * 5
    y2 = y1 + th + padding * 4
    return get_rectify_button_label(), (x1, y1, x2, y2)

def is_inside_rect(x, y, rect):
    if rect is None:
        return False
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2

def confirm_point_on_distorted_image():
    if has_undistorted[0]:
        return True
    return messagebox.askyesno(
        "Image Not Undistorted",
        "Are you sure you want to place this point?\n\n"
        "The image has not been undistorted.",
        icon="warning",
    )

def get_display_size():
    rect = cv2.getWindowImageRect(WINDOW_NAME)
    dw, dh = rect[2], rect[3]
    return (dw, dh) if dw > 0 and dh > 0 else (w, h)

def clamp_view():
    global view_x, view_y
    view_x = max(0.0, min(view_x, w - w / zoom_level))
    view_y = max(0.0, min(view_y, h - h / zoom_level))

def get_crop_bounds():
    # the source-image region currently visible (depends on zoom / pan).
    x1 = max(0, int(view_x))
    y1 = max(0, int(view_y))
    x2 = min(w, int(view_x + w / zoom_level) + 1)
    y2 = min(h, int(view_y + h / zoom_level) + 1)
    return x1, y1, x2, y2

def get_view_layout(dw, dh):
    # Fit the visible crop into the display preserving aspect ratio (letterbox).
    # Returns the crop bounds plus the uniform scale f and the black-bar offset
    # (off_x, off_y). All display<->original mapping uses this so clicks line up.
    x1, y1, x2, y2 = get_crop_bounds()
    crop_w = max(1, x2 - x1)
    crop_h = max(1, y2 - y1)
    f = min(dw / crop_w, dh / crop_h)
    content_w = crop_w * f
    content_h = crop_h * f
    off_x = (dw - content_w) / 2.0
    off_y = (dh - content_h) / 2.0
    return x1, y1, x2, y2, f, off_x, off_y

def display_to_orig(dx, dy, dw, dh):
    # invert the letterboxed fit; keep sub-pixel precision so the stored point
    # matches the click, rounding only happens when drawing back
    x1, y1, _x2, _y2, f, off_x, off_y = get_view_layout(dw, dh)
    return (
        x1 + (dx - off_x) / f,
        y1 + (dy - off_y) / f,
    )

def orig_to_display(ox, oy, dw, dh):
    x1, y1, _x2, _y2, f, off_x, off_y = get_view_layout(dw, dh)
    return (
        round((ox - x1) * f + off_x),
        round((oy - y1) * f + off_y),
    )

def draw_frame(dw, dh):
    x1, y1, x2, y2, f, off_x, off_y = get_view_layout(dw, dh)
    content_w = max(1, int(round((x2 - x1) * f)))
    content_h = max(1, int(round((y2 - y1) * f)))
    resized = cv2.resize(img[y1:y2, x1:x2], (content_w, content_h), interpolation=cv2.INTER_LINEAR)

    # paste the fitted image onto a black canvas (the letterbox bars)
    out = np.zeros((dh, dw, 3), dtype=np.uint8)
    oxi = max(0, int(round(off_x)))
    oyi = max(0, int(round(off_y)))
    out[oyi:oyi + content_h, oxi:oxi + content_w] = resized[:dh - oyi, :dw - oxi]

    # --- Click dots ---
    for idx, (ox, oy) in enumerate(clicks):
        dx, dy = orig_to_display(ox, oy, dw, dh)
        if 0 <= dx < dw and 0 <= dy < dh:
            cv2.circle(out, (dx, dy), 5, pair_color(idx), -1)

    # --- Rectification corner markers (while picking) ---
    if rectify_pick_mode[0]:
        corner_names = ["TL", "TR", "BR", "BL"]
        pts = []
        for ci, (ox, oy) in enumerate(rectify_corners):
            dx, dy = orig_to_display(ox, oy, dw, dh)
            pts.append((dx, dy))
            cv2.drawMarker(out, (dx, dy), (0, 0, 255), cv2.MARKER_CROSS, 16, 2)
            cv2.putText(out, corner_names[ci], (dx + 6, dy - 6), font, small_scale, (0, 0, 255), thickness, line_type)
        # connect the corners placed so far to preview the quad
        if len(pts) >= 2:
            cv2.polylines(out, [np.array(pts, dtype=np.int32)], len(pts) == 4, (0, 0, 255), 1, line_type)

    # --- Undistort button ---
    label, button_rect = get_undistort_button_rect()
    undistort_button_rect[0] = button_rect
    bx1, by1, bx2, by2 = button_rect
    undistort_enabled = not has_undistorted[0]
    undistort_fill = (32, 74, 104) if undistort_enabled else (40, 40, 40)
    undistort_text_color = (255, 255, 255) if undistort_enabled else (130, 130, 130)
    draw_filled_rect_alpha(out, (bx1, by1), (bx2, by2), undistort_fill, 0.88)
    cv2.rectangle(out, (bx1, by1), (bx2, by2), (180, 225, 245), 1, line_type)
    cv2.putText(out, label, (bx1 + padding * 2, by2 - padding * 2), font, button_scale, undistort_text_color, thickness, line_type)

    # --- Undo button ---
    undo_label, undo_rect = get_undo_button_rect()
    undo_button_rect[0] = undo_rect
    ux1, uy1, ux2, uy2 = undo_rect
    undo_enabled = len(clicks) > 0
    undo_fill = (40, 60, 90) if undo_enabled else (40, 40, 40)
    undo_text_color = (255, 255, 255) if undo_enabled else (130, 130, 130)
    draw_filled_rect_alpha(out, (ux1, uy1), (ux2, uy2), undo_fill, 0.88)
    cv2.rectangle(out, (ux1, uy1), (ux2, uy2), (180, 225, 245), 1, line_type)
    cv2.putText(out, undo_label, (ux1 + padding * 2, uy2 - padding * 2), font, button_scale, undo_text_color, thickness, line_type)

    # --- Save button ---
    save_label, save_rect = get_save_button_rect()
    save_button_rect[0] = save_rect
    sx1, sy1, sx2, sy2 = save_rect
    save_enabled = undistorted_img[0] is not None
    save_fill = (40, 90, 60) if save_enabled else (40, 40, 40)
    save_text_color = (255, 255, 255) if save_enabled else (130, 130, 130)
    draw_filled_rect_alpha(out, (sx1, sy1), (sx2, sy2), save_fill, 0.88)
    cv2.rectangle(out, (sx1, sy1), (sx2, sy2), (180, 225, 245), 1, line_type)
    cv2.putText(out, save_label, (sx1 + padding * 2, sy2 - padding * 2), font, button_scale, save_text_color, thickness, line_type)

    # --- White balance button (toggle) ---
    wb_label, wb_rect = get_white_balance_button_rect()
    white_balance_button_rect[0] = wb_rect
    wx1, wy1, wx2, wy2 = wb_rect
    wb_fill = (40, 120, 40) if wb_enabled[0] else (90, 70, 40)
    wb_border = (120, 255, 120) if wb_enabled[0] else (180, 225, 245)
    draw_filled_rect_alpha(out, (wx1, wy1), (wx2, wy2), wb_fill, 0.88)
    cv2.rectangle(out, (wx1, wy1), (wx2, wy2), wb_border, 1, line_type)
    cv2.putText(out, wb_label, (wx1 + padding * 2, wy2 - padding * 2), font, button_scale, (255, 255, 255), thickness, line_type)

    # --- CLAHE button (toggle) ---
    clahe_label, clahe_rect = get_clahe_button_rect()
    clahe_button_rect[0] = clahe_rect
    cx1, cy1, cx2, cy2 = clahe_rect
    clahe_fill = (40, 120, 40) if clahe_enabled[0] else (70, 40, 90)
    clahe_border = (120, 255, 120) if clahe_enabled[0] else (180, 225, 245)
    draw_filled_rect_alpha(out, (cx1, cy1), (cx2, cy2), clahe_fill, 0.88)
    cv2.rectangle(out, (cx1, cy1), (cx2, cy2), clahe_border, 1, line_type)
    cv2.putText(out, clahe_label, (cx1 + padding * 2, cy2 - padding * 2), font, button_scale, (255, 255, 255), thickness, line_type)

    # --- Rectify button (pick corners / toggle) ---
    rect_label, rect_rect = get_rectify_button_rect()
    rectify_button_rect[0] = rect_rect
    rx1, ry1, rx2, ry2 = rect_rect
    if rectify_pick_mode[0]:
        rect_fill, rect_border = (40, 90, 160), (120, 200, 255)   # picking
    elif rectify_enabled[0]:
        rect_fill, rect_border = (40, 120, 40), (120, 255, 120)   # on
    else:
        rect_fill, rect_border = (90, 60, 40), (180, 225, 245)    # off / not set
    draw_filled_rect_alpha(out, (rx1, ry1), (rx2, ry2), rect_fill, 0.88)
    cv2.rectangle(out, (rx1, ry1), (rx2, ry2), rect_border, 1, line_type)
    cv2.putText(out, rect_label, (rx1 + padding * 2, ry2 - padding * 2), font, button_scale, (255, 255, 255), thickness, line_type)

    # --- Lower-right info label ---
    info_lines = [f"Photo {photo_number[0]}/2", filename, f"{w} x {h}", file_datetime, f"Zoom {zoom_level:.1f}x"]
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
        # keep the source point under the cursor fixed across the zoom
        src_before = display_to_orig(x, y, dw, dh)
        zoom_level = min(zoom_level * ZOOM_STEP, ZOOM_MAX) if flags > 0 \
                     else max(zoom_level / ZOOM_STEP, ZOOM_MIN)
        src_after = display_to_orig(x, y, dw, dh)
        view_x += src_before[0] - src_after[0]
        view_y += src_before[1] - src_after[1]
        clamp_view()
        cv2.imshow(WINDOW_NAME, draw_frame(dw, dh))

    # --- Right-click drag: pan ---
    elif event == cv2.EVENT_RBUTTONDOWN:
        pan_start[0]      = (x, y)
        pan_view_start[0] = (view_x, view_y)

    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_RBUTTON):
        if pan_start[0]:
            _x1, _y1, _x2, _y2, f, _ox, _oy = get_view_layout(dw, dh)
            view_x = pan_view_start[0][0] - (x - pan_start[0][0]) / f
            view_y = pan_view_start[0][1] - (y - pan_start[0][1]) / f
            clamp_view()
            cv2.imshow(WINDOW_NAME, draw_frame(dw, dh))

    elif event == cv2.EVENT_RBUTTONUP:
        pan_start[0] = None

    # --- Left-click: measurement point ---
    elif event == cv2.EVENT_LBUTTONDOWN:
        if is_inside_rect(x, y, undistort_button_rect[0]):
            undistort_loaded_image()
            return

        if is_inside_rect(x, y, undo_button_rect[0]):
            undo_last_click()
            return

        if is_inside_rect(x, y, save_button_rect[0]):
            save_undistorted_image()
            return

        if is_inside_rect(x, y, white_balance_button_rect[0]):
            toggle_white_balance()
            return

        if is_inside_rect(x, y, clahe_button_rect[0]):
            toggle_clahe()
            return

        if is_inside_rect(x, y, rectify_button_rect[0]):
            rectify_button_action()
            return

        if not confirm_point_on_distorted_image():
            return

        orig_x, orig_y = display_to_orig(x, y, dw, dh)

        # --- Picking block corners for rectification ---
        if rectify_pick_mode[0]:
            rectify_corners.append((orig_x, orig_y))
            ticker.append((f"Corner {len(rectify_corners)}/4 set", (0, 200, 255)))
            if len(rectify_corners) == 4:
                compute_rectification()
                rectify_pick_mode[0] = False
                rectify_enabled[0] = True
                clicks.clear()
                click_ticker_counts.clear()
                recompute_image()
                ticker.append((f"Rectified: {rectify_scale[0]:.2f} px/mm from block", (0, 255, 0)))
            cv2.imshow(WINDOW_NAME, draw_frame(dw, dh))
            return

        idx        = len(clicks)
        pair       = idx // 2
        pt_in_pair = idx % 2 + 1
        color      = pair_color(idx)

        # When rectified, scale is known from the block. Otherwise, the first
        # pair calibrates against this photo's reference distance.
        auto_scaled = rectify_enabled[0] and pixels_per_mm[0]

        clicks.append((orig_x, orig_y))
        ticker.append((f"M{pair+1}.P{pt_in_pair}: ({round(orig_x)}, {round(orig_y)})", color))
        ticker_lines_added = 1

        if pt_in_pair == 2:
            dist_px = px_distance(clicks[-2], clicks[-1])
            if pair == 0 and not auto_scaled:
                reference_mm = (
                    FIRST_REFERENCE_MM
                    if photo_number[0] == 1
                    else second_photo_reference_mm[0]
                )
                pixels_per_mm[0] = dist_px / reference_mm
                line = f"  {dist_px:.1f}px = {reference_mm:.3f}mm  ->  {pixels_per_mm[0]:.2f}px/mm"
            elif pixels_per_mm[0]:
                millimeters = dist_px / pixels_per_mm[0]
                line = f"  {dist_px:.1f}px  ->  {millimeters:.2f} mm"
                if photo_number[0] == 1 and pair == 1:
                    second_photo_reference_mm[0] = millimeters
                    line += "  (reference for photo 2)"
            else:
                line = f"  {dist_px:.1f}px  (calibrate yellow first)"
            ticker.append((line, color))
            ticker_lines_added += 1
            print(line)

        click_ticker_counts.append(ticker_lines_added)
        cv2.imshow(WINDOW_NAME, draw_frame(dw, dh))
        if (
            pt_in_pair == 2
            and photo_number[0] == 1
            and pair == 1
            and second_photo_reference_mm[0] is not None
        ):
            load_second_photo()

# --- Init ---
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
init_w = min(w, 1200)
init_h = int(h * init_w / w)
cv2.resizeWindow(WINDOW_NAME, init_w, init_h)
cv2.imshow(WINDOW_NAME, draw_frame(init_w, init_h))
cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

print(f"Showing first photo: {image_path}  ({w}x{h})")
print(f"Photo 1: pair 1 = {FIRST_REFERENCE_MM:.3f} mm; pair 2 becomes photo 2's reference.")
print("Scroll: zoom  |  Right-drag: pan  |  R: reset zoom  |  Z: undo click  |  N: load second photo  |  S: save undistorted  |  W: white balance  |  C: CLAHE  |  H: rectify  |  P: re-pick corners  |  Left-click: measure")

prev_size = (init_w, init_h)
while True:
    key = cv2.waitKey(50)
    if key == ord('r'):          # reset zoom
        zoom_level, view_x, view_y = 1.0, 0.0, 0.0
        cv2.imshow(WINDOW_NAME, draw_frame(*get_display_size()))
    elif key == ord('z'):        # undo last measurement click
        undo_last_click()
    elif key == ord('n'):        # load/retry the second photo
        load_second_photo()
    elif key == ord('s'):        # save undistorted image
        save_undistorted_image()
    elif key == ord('w'):        # toggle gray-world white balance
        toggle_white_balance()
    elif key == ord('c'):        # toggle CLAHE local contrast on L channel
        toggle_clahe()
    elif key == ord('h'):        # rectify: pick corners if unset, else toggle
        rectify_button_action()
    elif key == ord('p'):        # re-pick the block corners (reset homography)
        start_rectify_pick()
    elif key in (27, ord('q')): # Esc or Q exits
        break
    curr_size = get_display_size()
    if curr_size != prev_size:
        prev_size = curr_size
        cv2.imshow(WINDOW_NAME, draw_frame(*curr_size))

cv2.destroyAllWindows()
root.destroy()
