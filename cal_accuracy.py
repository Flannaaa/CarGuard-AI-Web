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
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    return intersection_area / float(box1_area + box2_area - intersection_area)

# ------------------------
# Hardcoded Ground Truth
# Format: [xmin, ymin, xmax, ymax, class_id]
# ------------------------
ground_truths = {
    "JPJ-Malaysia-Cool-NUmber-Plates-2.jpg": [
        [100, 200, 400, 300, 0]
    ]
}

# ------------------------
# Hardcoded Predictions
# Format: [xmin, ymin, xmax, ymax, score, class_id]
# ------------------------
predictions = {
    "JPJ-Malaysia-Cool-NUmber-Plates-2.jpg": [
        [105, 205, 395, 295, 0.9, 0],  # Good prediction
        [50, 50, 150, 100, 0.4, 0]      # Wrong prediction
    ]
}

# ------------------------
# Accuracy Calculation
# ------------------------
def calculate_accuracy(gt_boxes, pred_boxes, iou_threshold=0.5):
    matched_gt = []
    correct = 0

    for pred in pred_boxes:
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

        if best_iou >= iou_threshold:
            correct += 1
            matched_gt.append(best_gt_idx)

    total_preds = len(pred_boxes)
    total_gt = len(gt_boxes)

    accuracy_pred = correct / total_preds if total_preds > 0 else 0
    accuracy_gt = correct / total_gt if total_gt > 0 else 0

    return accuracy_pred, accuracy_gt

# ------------------------
# Run accuracy for each image
# ------------------------
print("===== ACCURACY RESULT =====")

for img_name in predictions:
    pred_boxes = predictions[img_name]
    gt_boxes = ground_truths[img_name]

    acc_pred, acc_gt = calculate_accuracy(gt_boxes, pred_boxes)

    print(f"\nImage: {img_name}")
    print(f"Accuracy based on predicted boxes: {acc_pred:.4f}")
    print(f"Accuracy based on ground truth:    {acc_gt:.4f}")
