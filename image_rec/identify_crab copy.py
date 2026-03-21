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
def extract_features(image_path):
    img = Image.open(image_path).convert("RGB")
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
# Match test image
# -------------------------------
test_features = extract_features("test.jpg")

best_match = None
best_score = -1

for name, feat in known_features.items():
    score = cosine_similarity([test_features], [feat])[0][0]
    if score > best_score:
        best_score = score
        best_match = name

print(f"Matched crab: {best_match}")
print(f"Similarity score: {best_score:.3f}")

# -------------------------------
# Threshold logic
# -------------------------------
IDENTITY_THRESHOLD = 0.75
GREEN_CRAB_THRESHOLD = 0.80

if best_score < IDENTITY_THRESHOLD:
    print("Unknown crab species")
    draw_box = False
elif best_match == "european_green_crab.jpg" and best_score >= GREEN_CRAB_THRESHOLD:
    print("European green crab detected — drawing bounding box")
    draw_box = True
else:
    print("Other crab species — no bounding box")
    draw_box = False

# -------------------------------
# Bounding box (OpenCV)
# -------------------------------
def draw_crab_bbox(image_path, label):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image {image_path}")

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

    if not contours:
        return img

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(
        img, label,
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8, (0, 255, 0), 2
    )

    return img

# -------------------------------
# Draw bounding box ONLY if green crab
# -------------------------------
if draw_box:
    output = draw_crab_bbox("test.jpg", "European Green Crab")
    cv2.imwrite("output.jpg", output)
    print("Saved output.jpg with bounding box")
else:
    print("No bounding box drawn")
