from ultralytics import YOLO

# Load a pretrained YOLO model (smallest version)
model = YOLO("yolov8n.pt")

# Train on your dataset
model.train(
    data=r"image_rec/Crab Detection.v1-crabs.yolov11/data.yaml",
    epochs=100,
    imgsz=640
)