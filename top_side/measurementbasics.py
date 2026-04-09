import cv2
import tkinter as tk
from tkinter import filedialog
import os
import datetime

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

KNOWN_DISTANCE = 4.0
ZOOM_STEP      = 1.2
ZOOM_MIN       = 1.0
ZOOM_MAX       = 20.0

font      = cv2.FONT_HERSHEY_SIMPLEX
scale     = 0.55
thickness = 1
padding   = 6

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
pixels_per_inch = [None]

# Zoom / pan state
zoom_level     = 1.0
view_x         = 0.0   # top-left of visible region in original image coords
view_y         = 0.0
pan_start      = [None]
pan_view_start = [None]

def pair_color(i):
    return PAIR_COLORS[(i // 2) % len(PAIR_COLORS)]

def px_distance(p1, p2):
    return ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5

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

    # --- Lower-right info label ---
    info_lines = [filename, f"{w} x {h}", file_datetime, f"zoom  {zoom_level:.1f}x"]
    for i, line in enumerate(reversed(info_lines)):
        (tw, th), _ = cv2.getTextSize(line, font, scale, thickness)
        lx = dw - tw - padding
        ly = dh - padding - i * (th + padding * 2)
        cv2.rectangle(out, (lx-padding, ly-th-padding), (lx+tw+padding, ly+padding), (0,0,0), -1)
        cv2.putText(out, line, (lx, ly), font, scale, (255,255,255), thickness)

    # --- Upper-right ticker ---
    for i, (line, color) in enumerate(ticker):
        (tw, th), _ = cv2.getTextSize(line, font, scale, thickness)
        lx = dw - tw - padding
        ly = padding + (i + 1) * (th + padding)
        cv2.rectangle(out, (lx-padding, ly-th-padding), (lx+tw+padding, ly+padding), (0,0,0), -1)
        cv2.putText(out, line, (lx, ly), font, scale, color, thickness)

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
                pixels_per_inch[0] = dist_px / KNOWN_DISTANCE
                line = f"  {dist_px:.1f}px = {KNOWN_DISTANCE}in  →  {pixels_per_inch[0]:.2f}px/in"
            elif pixels_per_inch[0]:
                inches = dist_px / pixels_per_inch[0]
                line = f"  {dist_px:.1f}px  →  {inches:.3f} in"
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
