import cv2
from ultralytics import YOLO
from utils.readLicensePlate import readLicensePlate
from utils.utils import visualize
from datetime import datetime
import os
from utils.enhancer import enhance_plate

# Load YOLO model
license_plate_detector = YOLO('models/yolo/best.pt')

# ----------------- Existing photo detection -----------------
def yoloDetectPhoto(path):
    img = cv2.imread(path)
    license_plates = license_plate_detector(img)[0]

    os.makedirs("resources/image/output/yolo", exist_ok=True)

    for license_plate in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, license_plateScore, license_plateClass_id = license_plate

        imgcpy = img.copy()
        license_plate_text = readLicensePlate(imgcpy, x1, y1, x2, y2)
        plate_number = license_plate_text[0] if license_plate_text else "Unknown"

        visualize(img, license_plateScore, plate_number, x1, y1, x2, y2)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"resources/image/output/yolo/detection_{timestamp}.jpg"
        cv2.imwrite(output_path, img)

        # Log detection
        os.makedirs("resources", exist_ok=True)
        with open("resources/entered_record.txt", "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"Detected Plate: {plate_number}\n"
                    f"Image: {output_path}\n"
                    f"{'-'*60}\n")

        return [plate_number, output_path]

# ----------------- New frame detection for live camera -----------------
def yoloDetectFrame(frame):
    """
    Detect plates in a single frame (from webcam/live stream)
    Returns:
        plate_number (str)
        annotated_frame (np.array)
    """
    license_plates = license_plate_detector(frame)[0]
    annotated_frame = frame.copy()
    plate_number = "Unknown"

    for lp in license_plates.boxes.data.tolist():
        x1, y1, x2, y2, score, cls = lp

        # Crop & enhance plate
        cropped_plate = annotated_frame[int(y1):int(y2), int(x1):int(x2)]
        enhanced_plate = enhance_plate(cropped_plate)

        # OCR
        plate_text = readLicensePlate(enhanced_plate, x1, y1, x2, y2)
        plate_number = plate_text[0] if plate_text else "Unknown"

        # Visualize
        visualize(annotated_frame, score, plate_number, x1, y1, x2, y2)

        # We just take the first plate detected
        break

    return plate_number, annotated_frame
