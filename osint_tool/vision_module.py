import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import imagehash
from rich.console import Console
from pathlib import Path
import urllib.request
import argparse
import sys

console = Console()


def analyze_hashes(img):
    """Compute image hashes"""
    ahash = imagehash.average_hash(img)
    phash = imagehash.phash(img)
    dhash = imagehash.dhash(img)
    whash = imagehash.whash(img)

    console.print("\n[bold cyan]=== Image Hashes ===[/bold cyan]")
    console.print(f"aHash: {ahash}")
    console.print(f"pHash: {phash}")
    console.print(f"dHash: {dhash}")
    console.print(f"wHash: {whash}")


def analyze_ocr(img):
    """Extract text with OCR"""
    console.print("\n[bold cyan]=== Extracted Text (OCR) ===[/bold cyan]")
    text = pytesseract.image_to_string(img)
    if text.strip():
        console.print(text.strip())
        with open("text.txt", "w", encoding="utf-8") as f:
            f.write(text)
        console.print("[green]Saved extracted text to text.txt[/green]")
    else:
        console.print("[red]No text detected[/red]")


def perform_ela(img, scale=10):
    """Perform Error Level Analysis (ELA)"""
    resaved = "temp_resaved.jpg"
    img.save(resaved, "JPEG", quality=90)
    resaved_img = Image.open(resaved)

    diff = ImageChops.difference(img, resaved_img)
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1

    diff = ImageEnhance.Brightness(diff).enhance(scale)
    return diff


def analyze_ela(img):
    """Run ELA and save"""
    ela_path = "ela.png"
    ela_img = perform_ela(img, scale=20)
    ela_img.save(ela_path)
    console.print("\n[bold cyan]=== ELA Output ===[/bold cyan]")
    console.print(f"Saved to: {ela_path}")


def detect_faces(image_path):
    """Detect faces using OpenCV Haar cascade"""
    console.print("\n[bold cyan]=== Face Detection ===[/bold cyan]")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        console.print("[red]No faces detected[/red]")
    else:
        console.print(f"[green]Detected {len(faces)} face(s)[/green]")
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        out_path = "faces_detected.jpg"
        cv2.imwrite(out_path, img)
        console.print(f"[green]Saved output with faces highlighted: {out_path}[/green]")


def ensure_models():
    """Ensure MobileNet SSD model files are available; download if missing."""
    model_dir = Path.home() / ".local" / "share" / "cv2" / "dnn"
    model_dir.mkdir(parents=True, exist_ok=True)

    proto = model_dir / "MobileNetSSD_deploy.prototxt"
    model = model_dir / "MobileNetSSD_deploy.caffemodel"

    urls = {
        proto: "https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt",
        model: "https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel"
    }

    for path, url in urls.items():
        if not path.exists():
            console.print(f"[yellow]Downloading {path.name}...[/yellow]")
            urllib.request.urlretrieve(url, str(path))
            console.print(f"[green]Downloaded {path.name}[/green]")

    return str(proto), str(model)


def detect_objects(image_path):
    """Detect objects using MobileNet SSD"""
    console.print("\n[bold cyan]=== Object Detection ===[/bold cyan]")

    proto, model = ensure_models()
    net = cv2.dnn.readNetFromCaffe(proto, model)

    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant",
               "sheep", "sofa", "train", "tvmonitor"]

    img = cv2.imread(image_path)
    (h, w) = img.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    count = 0
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.4:  # confidence threshold
            idx = int(detections[0, 0, i, 1])
            label = CLASSES[idx]
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            cv2.rectangle(img, (startX, startY), (endX, endY), (255, 0, 0), 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(img, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            count += 1

    if count == 0:
        console.print("[red]No objects detected[/red]")
    else:
        out_path = "objects_detected.jpg"
        cv2.imwrite(out_path, img)
        console.print(f"[green]Detected {count} object(s). Saved to {out_path}[/green]")


def main():
    parser = argparse.ArgumentParser(description="Vision-based OSINT Analyzer")
    parser.add_argument("-i", "--image", required=True, help="Path to image file")
    parser.add_argument("--hashes", action="store_true", help="Run image hashing")
    parser.add_argument("--ocr", action="store_true", help="Run OCR")
    parser.add_argument("--ela", action="store_true", help="Run Error Level Analysis")
    parser.add_argument("--faces", action="store_true", help="Run face detection")
    parser.add_argument("--objects", action="store_true", help="Run object detection")
    parser.add_argument("--all", action="store_true", help="Run all analyses")

    args = parser.parse_args()

    img = Image.open(args.image).convert("RGB")

    if args.all or args.hashes:
        analyze_hashes(img)
    if args.all or args.ocr:
        analyze_ocr(img)
    if args.all or args.ela:
        analyze_ela(img)
    if args.all or args.faces:
        detect_faces(args.image)
    if args.all or args.objects:
        detect_objects(args.image)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python vision_module.py -i <image> [--all | --ocr --faces --objects --ela --hashes]")
        sys.exit(1)
    main()
