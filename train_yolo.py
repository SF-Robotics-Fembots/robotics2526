from pathlib import Path
from zipfile import ZipFile
import argparse

from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent
IMAGE_REC_DIR = BASE_DIR / "image_rec"

DATASET_ZIP = IMAGE_REC_DIR / "Crab Species Detection.v2i.yolov11.zip"
DATASET_DIR = IMAGE_REC_DIR / "Crab Species Detection.v2i.yolov11"
DATA_YAML = DATASET_DIR / "data.yaml"
LOCAL_STARTING_MODEL = IMAGE_REC_DIR / "best_species.pt"


def unzip_dataset_if_needed():
    if DATA_YAML.exists():
        print(f"Using existing dataset: {DATASET_DIR}")
        return

    if not DATASET_ZIP.exists():
        raise FileNotFoundError(f"Missing dataset zip: {DATASET_ZIP}")

    print(f"Unzipping dataset: {DATASET_ZIP}")
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(DATASET_ZIP, "r") as zip_file:
        zip_file.extractall(DATASET_DIR)

    if not DATA_YAML.exists():
        raise FileNotFoundError(f"Could not find data.yaml after unzipping: {DATA_YAML}")


def train():
    starting_model = LOCAL_STARTING_MODEL if LOCAL_STARTING_MODEL.exists() else "yolo11n.pt"
    print(f"Starting from model: {starting_model}")

    model = YOLO(str(starting_model))
    model.train(
        data=str(DATA_YAML),
        epochs=100,
        imgsz=640,
    )


def main():
    parser = argparse.ArgumentParser(description="Unzip and train YOLO on the v2 crab species dataset.")
    parser.add_argument(
        "--unzip-only",
        action="store_true",
        help="Unzip the dataset and stop before training.",
    )
    args = parser.parse_args()

    unzip_dataset_if_needed()
    if not args.unzip_only:
        train()


if __name__ == "__main__":
    main()
