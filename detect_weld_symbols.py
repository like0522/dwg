"""
Weld Symbol Detection Wrapper
Uses YOLO model from weldCalloutIdentifier to detect AWS/ISO weld symbols.

LAST MODIFIED: 2026-11-25 23:35:00
"""

import os
import sys
import argparse
from pathlib import Path
import cv2
import torch
from torchvision.ops import nms
from ultralytics import YOLO


def detect_welds(image_path: str, model_path: str = None, conf_threshold: float = 0.5):
    """Run weld callout detection on an input drawing image."""
    base_dir = Path(__file__).resolve().parent
    if model_path is None:
        model_path = str(base_dir / "tools" / "weldCalloutIdentifier" / "assets" / "weldIdentifier.pt")

    if not os.path.exists(model_path):
        print(f"[ERROR] Model file not found: {model_path}")
        return []

    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found: {image_path}")
        return []

    model = YOLO(model_path)
    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Failed to load image: {image_path}")
        return []

    results = model(image, verbose=False)
    detections = []

    for result in results:
        boxes = result.boxes
        cls_names = result.names

        box_data = []
        for box in boxes:
            conf = float(box.conf)
            if conf >= conf_threshold:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                box_data.append([x1, y1, x2, y2, conf, int(box.cls)])

        if box_data:
            box_tensor = torch.tensor([b[:4] for b in box_data], dtype=torch.float32)
            scores = torch.tensor([b[4] for b in box_data], dtype=torch.float32)
            indices = nms(box_tensor, scores, iou_threshold=0.5)

            for idx in indices:
                x1, y1, x2, y2, conf, cls_id = box_data[idx]
                detections.append({
                    "class_id": cls_id,
                    "class_name": cls_names[cls_id],
                    "confidence": round(conf, 3),
                    "box": [int(x1), int(y1), int(x2), int(y2)]
                })

    return detections


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect welding callouts from drawing image")
    parser.add_argument("image", help="Path to input drawing image (PNG, JPG)")
    parser.add_argument("--conf", type=float, default=0.5, help="Confidence threshold (default: 0.5)")
    args = parser.parse_args()

    results = detect_welds(args.image, conf_threshold=args.conf)
    print(f"=== DETECTED WELD SYMBOLS: {len(results)} items ===")
    for item in results:
        print(f" - {item['class_name']}: conf={item['confidence']} bbox={item['box']}")
