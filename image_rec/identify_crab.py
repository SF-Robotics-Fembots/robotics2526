import torch
import numpy as np
from torchvision import models, transforms
from PIL import Image
import os
from sklearn.metrics.pairwise import cosine_similarity
import cv2

# -------------------------------
# Model setup (CPU, offline)
# -------------------------------
device = torch.device("cpu")

model = models.resnet18(pretrained=True)
model.fc = torch.nn.Identity()
model = model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# -------------------------------
# Feature extraction
# -------------------------------
def extract_features(image_input):
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGB")
    else:
        img = image_input.convert("RGB")
    img = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        features = model(img)

    return features.cpu().numpy().flatten()

# -------------------------------
# Load known crab samples
# -------------------------------
known_features = {}

for file in os.listdir("known_crabs"):
    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    path = os.path.join("known_crabs", file)
    known_features[file] = extract_features(path)

# -------------------------------
# Thresholds
# -------------------------------
IDENTITY_THRESHOLD = 0.75
GREEN_CRAB_THRESHOLD = 0.80

# -------------------------------
# Detection tuning parameters
# -------------------------------
MIN_CONTOUR_AREA = 3000       # Skip contours smaller than this (filters noise)
MAX_CONTOUR_AREA_RATIO = 0.8  # Skip contours larger than 80% of image (filters background)

# -------------------------------
# Region detection
# -------------------------------
def find_candidate_regions(image_path):
    """
    Run contour detection and return all bounding boxes that pass area filtering.
    Returns (img_cv, [(x, y, w, h), ...])
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    img_area = img.shape[0] * img.shape[1]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_CONTOUR_AREA:
            continue
        if area > img_area * MAX_CONTOUR_AREA_RATIO:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        candidates.append((x, y, w, h))

    return img, candidates

# -------------------------------
# Non-maximum suppression
# -------------------------------
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

# -------------------------------
# Multi-crab detection pipeline
# -------------------------------
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

    for (x, y, w, h) in candidates:
        pad_x = int(w * 0.1)
        pad_y = int(h * 0.1)
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

    detections = apply_nms(detections, iou_threshold=0.4)
    print(f"\nFinal detections after NMS: {len(detections)}")

    for (x, y, w, h, score, label) in detections:
        color = (0, 255, 0) if "Green" in label else (0, 255, 255)
        cv2.rectangle(img_cv, (x, y), (x + w, y + h), color, 2)
        text_y = y - 10 if y > 30 else y + h + 20
        cv2.putText(
            img_cv, label,
            (x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, color, 2
        )

    cv2.imwrite(output_path, img_cv)
    print(f"Saved annotated image to: {output_path}")

    return detections

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    results = detect_and_identify_crabs("test.jpg", output_path="output.jpg")

    if not results:
        print("No crabs identified in image.")
    else:
        print(f"\nSummary: {len(results)} crab(s) detected:")
        for i, (x, y, w, h, score, label) in enumerate(results, 1):
            print(f"  Crab {i}: {label} at box ({x}, {y}, {w}x{h})")
