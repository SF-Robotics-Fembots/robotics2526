import os

import cv2
from ultralytics import YOLO


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_species.pt")

CONFIDENCE_THRESHOLD = 0.25

CLASS_COLORS = {
    "green_crab": (0, 255, 0),
    "jonah_crab": (0, 255, 255),
    "rock_crab": (255, 0, 255),
}


def pretty_label(class_name):
    return class_name.replace("_", " ").title()


def find_test_image():
    return next(
        (
            os.path.join(BASE_DIR, filename)
            for filename in os.listdir(BASE_DIR)
            if filename.lower().startswith("test.")
            and filename.lower().endswith((".jpg", ".jpeg", ".png"))
        ),
        None,
    )


def detect_and_identify_crabs(image_path, output_path="output.jpg"):
    """
    Detect crab species with the trained YOLO model, draw boxes, save output_path,
    and return detections as (x, y, w, h, confidence, class_name) tuples.
    """
    if image_path is None:
        raise FileNotFoundError("No test image found. Add test.jpg, test.jpeg, or test.png to image_rec.")

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Missing YOLO model: {MODEL_PATH}")

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    print(f"\nProcessing image: {image_path}")
    yolo_model = YOLO(MODEL_PATH)
    results = yolo_model(image_path)[0]

    detections = []
    green_count = 0

    for box in results.boxes:
        confidence = float(box.conf[0])
        if confidence < CONFIDENCE_THRESHOLD:
            continue

        class_id = int(box.cls[0])
        class_name = yolo_model.names[class_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        w = x2 - x1
        h = y2 - y1

        if class_name == "green_crab":
            green_count += 1

        detections.append((x1, y1, w, h, confidence, class_name))

        color = CLASS_COLORS.get(class_name, (255, 255, 255))
        label = f"{pretty_label(class_name)} ({confidence:.2f})"
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

        text_y = y1 - 10 if y1 > 30 else y2 + 20
        cv2.putText(
            img,
            label,
            (x1, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

        print(f"  {label} at box ({x1}, {y1}, {w}x{h})")

    cv2.putText(
        img,
        f"Green Crabs: {green_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        3,
    )

    cv2.imwrite(output_path, img)
    print(f"\nSaved annotated image to: {output_path}")
    print(f"Green crab count: {green_count}")

    return detections


if __name__ == "__main__":
    test_image = find_test_image()
    output_image = os.path.join(BASE_DIR, "output.jpg")

    results = detect_and_identify_crabs(test_image, output_path=output_image)
    if not results:
        print("No crabs identified in image.")
    else:
        print(f"\nSummary: {len(results)} crab(s) detected:")
        for i, (x, y, w, h, confidence, class_name) in enumerate(results, 1):
            print(f"  Crab {i}: {pretty_label(class_name)} ({confidence:.2f}) at box ({x}, {y}, {w}x{h})")
