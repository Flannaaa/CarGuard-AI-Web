from ultralytics import YOLO
import os

# ----------------- CONFIG -----------------
model_path = "yolov8n.pt"  # or your trained model
image_folder = r"C:\Users\Flanna\Downloads\fyp\images"  # folder with test images

# Ground truth boxes for each image
# Format: {"image_name.jpg": [xmin, ymin, xmax, ymax], ...}
ground_truths = {

    "JPJ-Malaysia-Cool-NUmber-Plates-2.jpg": [75, , 496, 308]


    # Add all your test images here
}
# ------------------------------------------

# Function to calculate IoU
def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter_area = max(0, xB - xA) * max(0, yB - yA)
    union_area = ((boxA[2]-boxA[0])*(boxA[3]-boxA[1]) +
                  (boxB[2]-boxB[0])*(boxB[3]-boxB[1]) -
                  inter_area)
    return inter_area / union_area if union_area != 0 else 0

# Load YOLO model
model = YOLO(model_path)

# Track overall IoU
iou_sum = 0
image_count = 0

for image_name, gt_box in ground_truths.items():
    image_path = os.path.join(image_folder, image_name)
    results = model.predict(image_path)

    # Take the predicted box with the **highest IoU** for each image
    best_iou = 0
    for result in results:
        boxes = result.boxes.xyxy
        for box in boxes:
            x1, y1, x2, y2 = box
            iou_score = iou([x1, y1, x2, y2], gt_box)
            if iou_score > best_iou:
                best_iou = iou_score

    iou_sum += best_iou
    image_count += 1
    print(f"{image_name}: Best IoU = {best_iou:.4f}")

# Compute overall system IoU
overall_iou = iou_sum / image_count if image_count > 0 else 0
print(f"\nOverall system IoU: {overall_iou:.4f}")
