def compute_iou(boxA, boxB):
    # box format = (x1, y1, x2, y2)

    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # overlap area
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH

    # areas of both boxes
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    # union
    unionArea = boxAArea + boxBArea - interArea

    # IoU
    iou = interArea / unionArea if unionArea != 0 else 0
    return iou


# TEST
if __name__ == "__main__":
    box_gt = (100, 100, 200, 200)      # ground truth
    box_pred = (120, 110, 210, 220)    # predicted

    print("IoU =", compute_iou(box_gt, box_pred))
