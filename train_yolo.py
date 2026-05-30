from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data=r"image_rec/Crab Species Detection.v1i.yolov11/data.yaml",
    epochs=100,
    imgsz=640
)