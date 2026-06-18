import os

import cv2
from ultralytics import YOLO


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "crab_detection_species_v3_yolo11.pt")

CONFIDENCE_THRESHOLD = 0.35
DRAWN_CLASSES = {"green_crab"}

CLASS_COLORS = {
    "green_crab": (0, 255, 0),
    "jonah_crab": (0, 255, 255),
    "rock_crab": (255, 0, 255),
}


def pretty_label(class_name):
    return class_name.replace("_", " ").title()


def find_test_image():
    image_extensions = (".jpg", ".jpeg", ".png")
    test_image = next(
        (
            os.path.join(BASE_DIR, filename)
            for filename in os.listdir(BASE_DIR)
            if filename.lower().startswith("test.")
            and filename.lower().endswith(image_extensions)
        ),
        None,
    )
    if test_image is not None:
        return test_image

    test_crabs_dir = os.path.join(BASE_DIR, "test_crabs")
    if not os.path.isdir(test_crabs_dir):
        return None

    return next(
        (
            os.path.join(test_crabs_dir, filename)
            for filename in os.listdir(test_crabs_dir)
            if filename.lower().endswith(image_extensions)
        ),
        None,
    )


def detect_and_identify_crabs(image_path, output_path="output.jpg"):
    """
    Detect crab species with the trained YOLO model, draw boxes, save output_path,
    and return detections as (x, y, w, h, confidence, class_name) tuples.
    """
    if image_path is None:
        raise FileNotFoundError("No test image found. Add test.jpg/test.jpeg/test.png to image_rec or an image to image_rec/test_crabs.")

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Missing YOLO model: {MODEL_PATH}. Run train_yolo.py first to train the v3 species model."
        )

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

        label = f"{pretty_label(class_name)} ({confidence:.2f})"
        if class_name in DRAWN_CLASSES:
            color = CLASS_COLORS.get(class_name, (255, 255, 255))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 4)

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
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        3.0,
        (0, 255, 0),
        5,
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
