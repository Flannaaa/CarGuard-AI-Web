from ultralytics import YOLO
import cv2

# Load your model
model = YOLO("yolov8n.pt")

# Image path
image_path = r"JPJ-Malaysia-Cool-NUmber-Plates-2.jpg"

# Run YOLO prediction
results = model(image_path)[0]

pred_boxes = []

# Extract boxes
for box in results.boxes:
    x1, y1, x2, y2 = box.xyxy[0].tolist()
    score = float(box.conf[0])
    cls = int(box.cls[0])
    pred_boxes.append([x1, y1, x2, y2, score, cls])

print("\nPredicted boxes:")
for b in pred_boxes:
    print(b)
