import json
import os
from PIL import Image

# Paths
json_file = "ground_truths.json"
image_folder = r"test_images"
label_folder = r"test_labels"

os.makedirs(label_folder, exist_ok=True)

# Load ground truth JSON
with open(json_file, "r") as f:
    data = json.load(f)

def convert_to_yolo(img_w, img_h, x1, y1, x2, y2):
    x_center = (x1 + x2) / 2 / img_w
    y_center = (y1 + y2) / 2 / img_h
    width = (x2 - x1) / img_w
    height = (y2 - y1) / img_h
    return x_center, y_center, width, height

for img_name, box in data.items():

    img_path = os.path.join(image_folder, img_name)
    if not os.path.exists(img_path):
        print(f"❌ Image not found: {img_name}")
        continue

    # Load image to get dimensions
    img = Image.open(img_path)
    w, h = img.size

    x1, y1, x2, y2 = box
    x_c, y_c, w_norm, h_norm = convert_to_yolo(w, h, x1, y1, x2, y2)

    # Write YOLO label
    label_path = os.path.join(label_folder, img_name.replace(".jpg", ".txt"))
    with open(label_path, "w") as f:
        f.write(f"0 {x_c} {y_c} {w_norm} {h_norm}\n")

    print(f"✅ Created label for {img_name}")

print("\nAll labels generated!")

