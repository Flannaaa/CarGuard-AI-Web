import cv2
import os

# ------------------------
# YOLO model setup
# ------------------------
MODEL_PATH = r"C:/Users/Flanna/Downloads/license_plate_recogniton_system-main/yolo/best.pt"
USE_YOLO = False
try:
    from ultralytics import YOLO
    if os.path.exists(MODEL_PATH):
        model = YOLO(MODEL_PATH)
        USE_YOLO = True
        print(f"✅ YOLO model loaded from {MODEL_PATH}")
    else:
        print(f"❌ YOLO model not found at {MODEL_PATH}. Using dummy predictions.")
except ImportError:
    print("❌ ultralytics YOLO not installed. Using dummy predictions.")

# ------------------------
# Test images
# ------------------------
images = [
    r"C:\Users\Flanna\Downloads\JPJ-Malaysia-Cool-NUmber-Plates-2.jpg"
]

ground_truths = {}
predictions = {}

# ------------------------
# IoU function
# ------------------------
def iou(box1, box2):
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (box1[2]-box1[0]) * (box1[3]-box1[1])
    box2_area = (box2[2]-box2[0]) * (box2[3]-box2[1])
    return intersection_area / float(box1_area + box2_area - intersection_area)

# ------------------------
# Annotation + Prediction
# ------------------------
for img_path in images:
    image = cv2.imread(img_path)
    if image is None:
        print(f"❌ Cannot read image: {img_path}")
        continue

    clone = image.copy()
    coords = []

    # Mouse callback
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            coords.append((x, y))
            cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
            cv2.imshow("Image", image)

    cv2.imshow("Image", image)
    cv2.setMouseCallback("Image", click_event)
    print(f"Click top-left and bottom-right corners for {img_path}")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(coords) != 2:
        print("❌ You must click exactly TWO points!")
        continue

    (xmin, ymin), (xmax, ymax) = coords
    img_name = img_path.split("\\")[-1]
    ground_truths[img_name] = [[xmin, ymin, xmax, ymax, 0]]  # class 0

    # YOLO prediction or dummy
    if USE_YOLO:
        results = model(img_path)[0]
        pred_list = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            score = float(box.conf[0])
            cls = int(box.cls[0])
            pred_list.append([x1, y1, x2, y2, score, cls])
        predictions[img_name] = pred_list
    else:
        # Dummy prediction: slightly offset from GT
        pred_list = [[xmin+5, ymin+5, xmax-5, ymax-5, 0.9, 0]]
        predictions[img_name] = pred_list

# ------------------------
# AP calculation
# ------------------------
IOU_THRESHOLD = 0.5

def calculate_ap(gt_boxes, pred_boxes):
    if len(pred_boxes) == 0:
        return 0.0
    pred_boxes = sorted(pred_boxes, key=lambda x: x[4], reverse=True)
    TP = [0] * len(pred_boxes)
    FP = [0] * len(pred_boxes)
    matched_gt = []
    for i, pred in enumerate(pred_boxes):
        pred_box = pred[:4]
        best_iou = 0
        best_gt_idx = -1
        for j, gt in enumerate(gt_boxes):
            if j in matched_gt:
                continue
            gt_box = gt[:4]
            iou_score = iou(pred_box, gt_box)
            if iou_score > best_iou:
                best_iou = iou_score
                best_gt_idx = j
        if best_iou >= IOU_THRESHOLD:
            TP[i] = 1
            matched_gt.append(best_gt_idx)
        else:
            FP[i] = 1
    cum_TP = 0
    cum_FP = 0
    precisions = []
    recalls = []
    for t, f in zip(TP, FP):
        cum_TP += t
        cum_FP += f
        precision = cum_TP / (cum_TP + cum_FP)
        recall = cum_TP / max(len(gt_boxes), 1)
        precisions.append(precision)
        recalls.append(recall)
    ap = 0
    for i in range(len(precisions)):
        delta_recall = recalls[i] - recalls[i-1] if i > 0 else recalls[i]
        ap += precisions[i] * delta_recall
    return ap

# ------------------------
# Compute mAP
# ------------------------
all_ap = []
for img_name in predictions:
    pred_boxes = predictions[img_name]
    gt_boxes = ground_truths.get(img_name, [])
    ap = calculate_ap(gt_boxes, pred_boxes)
    all_ap.append(ap)
    print(f"{img_name} AP: {ap:.4f}")

mAP = sum(all_ap) / len(all_ap) if all_ap else 0
print(f"\n===== mAP @ IoU {IOU_THRESHOLD} =====")
print(f"mAP: {mAP:.4f}")
