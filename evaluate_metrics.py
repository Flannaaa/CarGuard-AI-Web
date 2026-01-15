import json
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score

# Load GT and prediction data
gt = json.load(open("ground_truths.json"))
pred = json.load(open("predictions.json"))

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / (boxAArea + boxBArea - interArea + 1e-6)

IOUs = []
TP = 0
FP = 0
FN = 0

y_true = []
y_pred = []

IOU_THRESHOLD = 0.5

for image in gt:
    boxes = gt[image]

    # Ensure GT is always a list of lists
    if isinstance(boxes[0], int):
        # Convert single box [x1,y1,x2,y2] → [[x1,y1,x2,y2]]
        gt_boxes = [boxes]
    else:
        gt_boxes = boxes

    pred_boxes = pred.get(image, [])

    matched = []

    for g in gt_boxes:
        gx1, gy1, gx2, gy2 = g
        best_iou = 0
        best_pred = None

        for p in pred_boxes:
            px1, py1, px2, py2, conf, cls = p
            iou = compute_iou([gx1, gy1, gx2, gy2], [px1, py1, px2, py2])

            if iou > best_iou:
                best_iou = iou
                best_pred = p

        if best_iou >= IOU_THRESHOLD:
            TP += 1
            IOUs.append(best_iou)
            y_true.append(1)
            y_pred.append(1)
            matched.append(best_pred)
        else:
            FN += 1
            y_true.append(1)
            y_pred.append(0)

    for p in pred_boxes:
        if p not in matched:
            FP += 1
            y_true.append(0)
            y_pred.append(1)

        best_iou = 0
        best_pred = None

        for p in pred_boxes:
            px1, py1, px2, py2, conf, cls = p
            iou = compute_iou([gx1, gy1, gx2, gy2], [px1, py1, px2, py2])

            if iou > best_iou:
                best_iou = iou
                best_pred = p

        if best_iou >= IOU_THRESHOLD:
            TP += 1
            IOUs.append(best_iou)
            y_true.append(1)
            y_pred.append(1)
            matched.append(best_pred)
        else:
            FN += 1
            y_true.append(1)
            y_pred.append(0)

    for p in pred_boxes:
        if p not in matched:
            FP += 1
            y_true.append(0)
            y_pred.append(1)

avg_iou = np.mean(IOUs)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)
acc = accuracy_score(y_true, y_pred)
cm = confusion_matrix(y_true, y_pred)

print("Average IoU:", avg_iou)
print("Precision:", precision)
print("Recall:", recall)
print("Accuracy:", acc)
print("F1 Score:", f1)
print("Confusion Matrix:\n", cm)
