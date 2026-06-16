from pathlib import Path
from shutil import copy2
from tempfile import gettempdir
from zipfile import ZipFile
import argparse

from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent
IMAGE_REC_DIR = BASE_DIR / "image_rec"

DATASET_ZIP = IMAGE_REC_DIR / "Crab Detection Species.v3i.yolov11.zip"
DATASET_DIR = Path(gettempdir()) / "robotics2526_yolo_datasets" / "Crab Detection Species.v3i.yolov11"
DATA_YAML = DATASET_DIR / "data.yaml"
STARTING_MODEL = "yolo11n.pt"
TRAINED_MODEL_PATH = IMAGE_REC_DIR / "crab_detection_species_v3_yolo11.pt"


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
    print(f"Starting from model: {STARTING_MODEL}")
    print(f"Training dataset: {DATA_YAML}")

    model = YOLO(STARTING_MODEL)
    results = model.train(
        data=str(DATA_YAML),
        epochs=100,
        imgsz=640,
        project=str(BASE_DIR / "runs" / "detect"),
        name="crab_detection_species_v3_yolo11",
    )

    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    if not best_weights.exists():
        raise FileNotFoundError(f"Training finished, but best weights were not found: {best_weights}")

    copy2(best_weights, TRAINED_MODEL_PATH)
    print(f"Copied trained model to: {TRAINED_MODEL_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Unzip and train YOLO on the v3 crab detection species dataset.")
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
