# models/yolo/yoloRealTimeDetection.py
import os
import time
from datetime import datetime
from collections import deque, Counter

import cv2
import numpy as np
from ultralytics import YOLO

# utilities from your repo (expected to exist)
from utils.utils import get_car, visualize
from utils.readLicensePlate import readLicensePlate  # expected (plate_text, score) return

# tracker
from sort.sort import Sort

# Files used by your main app
LIVE_RESULTS_FILE = "resources/live_detection_results.txt"
REGISTERED_CAR_PLATE_FILE = "resources/registered_car_plate.txt"
DETECTION_RESULTS_DIR = "detection_results"

# ensure output dir
os.makedirs(DETECTION_RESULTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LIVE_RESULTS_FILE), exist_ok=True)

# Global capture handle (optional control from outside)
global_live_capture = None

# --- Load models (adjust paths if needed) ---
mot_tracker = Sort()
# COCO detector (vehicle detections)
coco_model = YOLO('models/yolov8n.pt')
# YOLO model trained for license plates (your path)
license_plate_detector = YOLO('models/yolo/best.pt')


def _append_live_result(plate, crop_path=None):
    """Append stable detection to the live results file for the GUI to pick up."""
    try:
        with open(LIVE_RESULTS_FILE, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            line = f"{ts} - Plate: {plate}"
            if crop_path:
                line += f" - Image: {crop_path}"
            line += "\n"
            f.write(line)
    except Exception as e:
        print("Failed to write live result:", e)


def yoloRealTimeModelDetect(
    camera_index=0,
    fps_display_pos=(7, 70),
    conf_threshold=0.7,
    stabilizer_size=8,
    stable_required=3,
    report_cooldown_seconds=8
):
    """
    Start real-time detection using YOLO + a license-plate model, but stabilize output
    so the GUI shows one best match per car instead of flickering.

    - camera_index: index for cv2.VideoCapture
    - conf_threshold: minimum OCR confidence to accept
    - stabilizer_size: how many recent readings to keep per car
    - stable_required: how many matching entries required to consider 'stable'
    - report_cooldown_seconds: cooldown per car before reporting again
    """

    global global_live_capture
    cap = cv2.VideoCapture(camera_index)
    # set resolution (optional)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    global_live_capture = cap

    vehicles = [2, 3, 5, 7]  # class ids considered vehicles (COCO)
    prev_frame_time = time.time()

    # stabilizer: car_id -> deque of (plate_text, score)
    stabilizer = {}
    # last reported plate per car: car_id -> (plate_text, timestamp)
    last_reported = {}

    # Keep a simple per-loop FPS limiter if needed
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame grab failed; retrying...")
                time.sleep(0.1)
                continue

            # --- FPS calculation (overlay) ---
            new_frame_time = time.time()
            fps = 1.0 / max((new_frame_time - prev_frame_time), 1e-6)
            prev_frame_time = new_frame_time
            fps_display = str(int(fps))
            cv2.putText(frame, fps_display, fps_display_pos, cv2.FONT_HERSHEY_SIMPLEX, 1.2, (100, 255, 0), 2, cv2.LINE_AA)

            # --- detect vehicles using COCO model ---
            detections = coco_model(frame)[0]  # ultralytics returns a result object
            detections_ = []
            try:
                for box in detections.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = box
                    if int(class_id) in vehicles and score > 0.3:
                        detections_.append([x1, y1, x2, y2, score])
            except Exception:
                detections_ = []

            # convert to numpy array for tracker (Sort expects 5 cols: x1,y1,x2,y2,score)
            if len(detections_) > 0:
                det_array = np.array(detections_, dtype=np.float32).reshape(-1, 5)
            else:
                det_array = np.empty((0, 5), dtype=np.float32)

            # Update tracker -> returns array of tracked boxes [x1,y1,x2,y2,track_id]
            track_array = mot_tracker.update(det_array)

            # Prepare track ids for get_car usage later
            # track_array shape Nx5 (x1,y1,x2,y2,track_id); convert to list
            track_ids_list = track_array.tolist() if hasattr(track_array, "tolist") else []

            # --- run license plate detector on full frame (lighter than running per-ROI) ---
            lp_results = license_plate_detector(frame)[0]
            try:
                lp_boxes = lp_results.boxes.data.tolist()
            except Exception:
                lp_boxes = []

            # For each plate detection, find which car it's associated with
            for lp_box in lp_boxes:
                # Some ulralytics variants produce [x1,y1,x2,y2,score,class]
                if len(lp_box) >= 6:
                    x1, y1, x2, y2, lp_score, class_id = lp_box[:6]
                else:
                    # fallback if fewer fields
                    x1, y1, x2, y2 = lp_box[:4]
                    lp_score = lp_box[4] if len(lp_box) > 4 else 0.0
                    class_id = lp_box[5] if len(lp_box) > 5 else 0

                # associate this plate box to a car using your helper (get_car)
                # get_car should accept (license_plate_box, track_ids_list) like before
                try:
                    xcar1, ycar1, xcar2, ycar2, car_id = get_car(lp_box, track_ids_list)
                except Exception:
                    car_id = -1

                # Run OCR on cropped plate area (readLicensePlate expected to return text,score)
                try:
                    plate_text, plate_score = readLicensePlate(frame, int(x1), int(y1), int(x2), int(y2))
                except Exception as e:
                    # If OCR fails, skip
                    continue

                if not plate_text:
                    # skip empty reads
                    continue

                # Normalize plate text to uppercase and strip spaces, common cleaning
                plate_text = plate_text.strip().upper()

                # Initialize buffer for this car
                if car_id not in stabilizer:
                    stabilizer[car_id] = deque(maxlen=stabilizer_size)

                stabilizer[car_id].append((plate_text, float(plate_score)))

                # Evaluate stabilization
                recent = list(stabilizer[car_id])
                plates_only = [p for p, s in recent if p]
                if not plates_only:
                    continue

                # Most common plate in buffer
                most_common_plate, occurrences = Counter(plates_only).most_common(1)[0]
                # Best score seen for that plate in the buffer
                best_score_for_plate = max((s for p, s in recent if p == most_common_plate), default=0.0)

                is_stable = (occurrences >= stable_required) and (best_score_for_plate >= conf_threshold)

                # Prepare display string: stable result or 'Detecting...'
                display_plate = most_common_plate if is_stable else plate_text

                # Annotate on frame using your visualize helper
                try:
                    visualize(frame, float(best_score_for_plate), display_plate, int(x1), int(y1), int(x2), int(y2))
                except Exception:
                    # fallback simple text if visualize isn't compatible
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                    cv2.putText(frame, f"{display_plate} ({best_score_for_plate:.2f})", (int(x1), int(y1)-8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # If stable and we haven't reported recently for this car, report it
                now_ts = time.time()
                last_info = last_reported.get(car_id, (None, 0.0))
                last_plate_reported, last_time = last_info

                # Only report when stable and not already reported recently or different
                if is_stable:
                    should_report = False
                    if last_plate_reported != most_common_plate:
                        should_report = True
                    elif (now_ts - last_time) > report_cooldown_seconds:
                        should_report = True

                    if should_report:
                        # save crop image for history
                        crop_x1, crop_y1 = max(0, int(x1)), max(0, int(y1))
                        crop_x2, crop_y2 = min(frame.shape[1]-1, int(x2)), min(frame.shape[0]-1, int(y2))
                        crop_img = frame[crop_y1:crop_y2, crop_x1:crop_x2].copy()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_plate = most_common_plate.replace(" ", "_").replace("/", "_")
                        crop_filename = f"{DETECTION_RESULTS_DIR}/{timestamp}_{safe_plate}_crop.jpg"
                        try:
                            if crop_img.size != 0:
                                cv2.imwrite(crop_filename, crop_img)
                        except Exception:
                            crop_filename = None

                        # append to live results file (GUI is watching this file)
                        _append_live_result(most_common_plate, crop_filename)

                        # update last_reported
                        last_reported[car_id] = (most_common_plate, now_ts)

                        # optional: print to console for debugging
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] STABLE -> {most_common_plate} (score={best_score_for_plate:.2f}) saved={crop_filename}")

            # Show frame
            cv2.imshow('RealTime License Plate System (Press q to quit)', frame)

            # stop on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting live detection loop.")
    except Exception as ex:
        print("Exception in live detection:", ex)
    finally:
        # cleanup
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        global_live_capture = None
