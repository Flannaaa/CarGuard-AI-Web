import cv2
from ultralytics import YOLO

# ----------------------------------------
# 🔥 UPDATE THIS PATH TO YOUR trained model
# ----------------------------------------
model = YOLO(r"C:\Users\Flanna\Downloads\license_plate_recogniton_system-main\models\yolo\best.pt")


# List your test images
import glob

images = glob.glob(r"C:\Users\Flanna\Downloads\license_plate_recogniton_system-main\test_images\*.jpg")


ground_truths = {}
predictions = {}

for img_path in images:
    image = cv2.imread(img_path)

    if image is None:
        print(f"❌ ERROR: Cannot read image: {img_path}")
        continue

    clone = image.copy()
    coords = []

    # Mouse callback to select GT
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            coords.append((x, y))
            cv2.circle(image, (x, y), 3, (0, 255, 0), -1)
            cv2.imshow("Image", image)

    img_name = img_path.split("\\")[-1]

    cv2.imshow("Image", image)
    cv2.setMouseCallback("Image", click_event)
    print(f"Click top-left and bottom-right corners for {img_path}")
    cv2.waitKey(0)

    if len(coords) != 2:
        print("❌ You must click exactly TWO points!")
        cv2.destroyAllWindows()
        continue

    (xmin, ymin), (xmax, ymax) = coords
    ground_truths[img_name] = [xmin, ymin, xmax, ymax]

    # Show GT bounding box
    cv2.rectangle(clone, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
    cv2.imshow("GT Box", clone)
    cv2.waitKey(500)
    cv2.destroyAllWindows()

    # ----------------------------------------
    # 🔥 NOW GET YOLO PREDICTED BOXES
    # ----------------------------------------

    results = model(img_path)[0]
    pred_list = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        score = float(box.conf[0])
        cls = int(box.cls[0])
        pred_list.append([x1, y1, x2, y2, score, cls])

    predictions[img_name] = pred_list

    import json

# Save predictions
with open("predictions.json", "w") as f:
    json.dump(predictions, f)

# Save ground truths
with open("ground_truths.json", "w") as f:
    json.dump(ground_truths, f)

print("✅ Saved predictions.json and ground_truths.json")


print("\n=========== FINAL OUTPUTS ===========")
print("\nGROUND TRUTH:")
print(ground_truths)

print("\nPREDICTIONS:")
print(predictions)
