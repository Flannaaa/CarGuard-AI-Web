import numpy as np
import cv2
from tensorflow.lite.python.interpreter import Interpreter
from utils.readLicensePlate import readLicensePlate
from utils.utils import visualize

def ssdDetectPhoto(path):
    # setup
    modelpath = 'models/sdd_MobileNetV2_FpnLite/detect.tflite'
    min_conf = 0.22
    img = cv2.imread(path)
    interpreter = Interpreter(model_path=modelpath)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    float_input = (input_details[0]['dtype'] == np.float32)
    input_mean = 127.5
    input_std = 127.5
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imH, imW, _ = img.shape
    img_resized = cv2.resize(img_rgb, (width, height))
    input_data = np.expand_dims(img_resized, axis=0)
     # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if float_input:
        input_data = (np.float32(input_data) - input_mean) / input_std

    #Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[1]['index'])[0]  # Bounding box coordinates of detected objects
    scores = interpreter.get_tensor(output_details[0]['index'])[0]  # Confidence of detected objects


    for i in range(len(scores)):
        if ((scores[i] > min_conf) and (scores[i] <= 1.0)):
            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            license_plateScore = scores[i]
            ymin = int(max(1, (boxes[i][0] * imH)))
            xmin = int(max(1, (boxes[i][1] * imW)))
            ymax = int(min(imH, (boxes[i][2] * imH)))
            xmax = int(min(imW, (boxes[i][3] * imW)))

            imgcpy=img.copy()
            license_plate = readLicensePlate(imgcpy, xmin, ymin, xmax, ymax)
            # Draw label
            visualize(img, license_plateScore, license_plate[0], xmin, ymin, xmax, ymax)

            cv2.imwrite('resources/image/output/sdd_MobileNetV2_FpnLite/detection.jpg', img)
            return [license_plate[0], "resources/image/output/sdd_MobileNetV2_FpnLite/detection.jpg"]