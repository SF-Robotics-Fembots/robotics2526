#completed to do list but needs tuning to work properly

import torch
import numpy as np
from torchvision import models, transforms
from PIL import Image
import os
from sklearn.metrics.pairwise import cosine_similarity
import cv2
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_CRABS_DIR = os.path.join(BASE_DIR, "known_crabs")

# Model setup (CPU, offline)
device = torch.device("cpu")

#model = models.resnet18(pretrained=True)
from torchvision.models import resnet18, ResNet18_Weights

model = resnet18(weights=ResNet18_Weights.DEFAULT)
model.fc = torch.nn.Identity()
model = model.to(device)
model.eval()

# Load YOLO model for crab detection
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
yolo_model = YOLO(MODEL_PATH)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def enhance_underwater(img):
    img = np.array(img)

    # 1. White balance
    result = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(result)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    result = cv2.merge((l, a, b))
    result = cv2.cvtColor(result, cv2.COLOR_LAB2RGB)

    # 2. Reduce green/blue dominance
    r, g, b = cv2.split(result)
    r = cv2.add(r, 20)
    result = cv2.merge((r, g, b))

    # 3. Dehaze (simple dark channel prior)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dark = cv2.min(cv2.min(r, g), b)
    dark = cv2.erode(dark, kernel)
    haze = cv2.normalize(dark, None, 0, 255, cv2.NORM_MINMAX)
    haze = cv2.cvtColor(haze, cv2.COLOR_GRAY2RGB)
    result = cv2.addWeighted(result, 0.85, haze, -0.85, 0)

    return Image.fromarray(result)

# Feature extraction
def extract_features(image_input):
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGB")
    else:
        img = image_input.convert("RGB")
    
    #fix underwater color distortion before feature extraction
    img = enhance_underwater(img)

    #RGB version
    rgb_tensor = transform(img).unsqueeze(0).to(device)

    #grayscale version (reduces color dependence)
    gray = img.convert("L").convert("RGB")
    gray_tensor = transform(gray).unsqueeze(0).to(device)

    with torch.no_grad():
        rgb_feat = model(rgb_tensor)
        gray_feat = model(gray_tensor)

    #combine features
    features = torch.cat([rgb_feat, gray_feat], dim=1)

    return features.cpu().numpy().flatten()

# Load known crab samples
known_features = {}

#for file in os.listdir("known_crabs"):
for file in os.listdir(KNOWN_CRABS_DIR):
    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    path = os.path.join(KNOWN_CRABS_DIR, file)
    known_features[file] = extract_features(path)

# Thresholds
# IDENTITY_THRESHOLD = 0.75
# GREEN_CRAB_THRESHOLD = 0.80
IDENTITY_THRESHOLD = 0.45
GREEN_CRAB_THRESHOLD = 0.55

# Detection tuning parameters
MIN_CONTOUR_AREA = 500       # Skip contours smaller than this (filters noise)
MAX_CONTOUR_AREA_RATIO = 0.8  # Skip contours larger than 80% of image (filters background)

# Region detection
def find_candidate_regions(image_path):
    results = yolo_model(image_path)[0]

    candidates = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        w = x2 - x1
        h = y2 - y1
        conf = float(box.conf[0])
        candidates.append((int(x1), int(y1), int(w), int(h), conf))


    img_cv = cv2.imread(image_path)
    return img_cv, candidates

# Non-maximum suppression
def compute_iou(box_a, box_b):
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b

    ax2, ay2 = ax + aw, ay + ah
    bx2, by2 = bx + bw, by + bh

    inter_x1 = max(ax, bx)
    inter_y1 = max(ay, by)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    union_area = aw * ah + bw * bh - inter_area
    if union_area == 0:
        return 0.0
    return inter_area / union_area


def apply_nms(detections, iou_threshold=0.4):
    """
    detections: list of (x, y, w, h, score, label)
    Returns filtered list keeping highest-scoring box when boxes overlap.
    """
    if not detections:
        return []

    detections = sorted(detections, key=lambda d: d[4], reverse=True)
    kept = []

    while detections:
        best = detections.pop(0)
        kept.append(best)
        detections = [
            d for d in detections
            if compute_iou(best[:4], d[:4]) < iou_threshold
        ]

    return kept


# Multi-crab detection pipeline
def detect_and_identify_crabs(image_path, output_path="output.jpg"):
    """
    Detect all crabs in image_path, identify each with ResNet18 cosine similarity,
    draw labeled bounding boxes, and save to output_path.
    Returns list of (x, y, w, h, score, label) tuples.
    """
    print(f"\nProcessing image: {image_path}")

    img_cv, candidates = find_candidate_regions(image_path)

    if not candidates:
        print("No candidate regions found — no crabs detected.")
        cv2.imwrite(output_path, img_cv)
        return []

    print(f"Found {len(candidates)} candidate region(s). Running identification...")

    pil_image = Image.open(image_path).convert("RGB")
    img_width, img_height = pil_image.size

    detections = []

    for (x, y, w, h, det_conf) in candidates:
        if det_conf < 0.25:
            continue

        pad_x = int(w * 0.5)
        pad_y = int(h * 0.5)
        crop_x1 = max(0, x - pad_x)
        crop_y1 = max(0, y - pad_y)
        crop_x2 = min(img_width, x + w + pad_x)
        crop_y2 = min(img_height, y + h + pad_y)

        crop = pil_image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
        crop_features = extract_features(crop)

        best_match = None
        best_score = -1
        for name, ref_feat in known_features.items():
            score = cosine_similarity([crop_features], [ref_feat])[0][0]
            if score > best_score:
                best_score = score
                best_match = name

        if best_score < IDENTITY_THRESHOLD:
            label = None
        elif best_match == "european_green_crab.jpg" and best_score >= GREEN_CRAB_THRESHOLD:
            label = f"Green Crab ({best_score:.2f})"
        elif best_match == "native_jonah_crab.jpeg":
            label = f"Jonah Crab ({best_score:.2f})"
        elif best_match == "native_rock_crab.jpg":
            label = f"Rock Crab ({best_score:.2f})"
        else:
            label = f"Crab ({best_score:.2f})"

        if label is not None:
            detections.append((x, y, w, h, best_score, label))
            print(f"  Region ({x},{y},{w},{h}): {label}")
        else:
            print(f"  Region ({x},{y},{w},{h}): below threshold ({best_score:.3f}), skipping")

    # Keep ONLY green crabs
    green_detections = [
        d for d in detections
        if "Green Crab" in d[5]
    ]

    # Apply NMS only to green crabs
    green_detections = apply_nms(green_detections, iou_threshold=0.4)

    # Count green crabs
    green_count = len(green_detections)
    print(f"\nFinal green crab detections after NMS: {green_count}")

    # Draw only green crabs
    for (x, y, w, h, score, label) in green_detections:
        color = (0, 255, 0)
        cv2.rectangle(img_cv, (x, y), (x + w, y + h), color, 2)
        text_y = y - 10 if y > 30 else y + h + 20
        cv2.putText(
            img_cv, label,
            (x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, color, 2
        )

    # Add green crab count to screen
    cv2.putText(
        img_cv,
        f"Green Crabs: {green_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        3
    )

    cv2.imwrite(output_path, img_cv)
    return green_detections

# Entry point
if __name__ == "__main__":
    test_image = next(
    (os.path.join(BASE_DIR, f) for f in os.listdir(BASE_DIR)
     if f.lower().startswith("test.") and f.lower().endswith((".jpg", ".jpeg", ".png"))),
    None)
    output_image = os.path.join(BASE_DIR, "output.jpg")

    results = detect_and_identify_crabs(test_image, output_path=output_image)
    if not results:
        print("No crabs identified in image.")
    else:
        print(f"\nSummary: {len(results)} crab(s) detected:")
        for i, (x, y, w, h, score, label) in enumerate(results, 1):
            print(f"  Crab {i}: {label} at box ({x}, {y}, {w}x{h})")