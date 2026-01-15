import cv2
import numpy as np

# Simple image enhancement (you can upgrade this later)
def enhance_plate(img):
    if img is None:
        return img

    # Improve contrast
    enhanced = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)

    # Optional sharpening
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return sharpened
