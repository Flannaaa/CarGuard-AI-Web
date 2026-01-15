import cv2
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.enhancer import improved_ocr

def debug_single_plate(image_path, x1, y1, x2, y2):
    """调试单个车牌区域"""
    print(f"调试图片: {image_path}")
    
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return
    
    # 提取车牌区域
    plate_roi = img[y1:y2, x1:x2]
    
    if plate_roi.size == 0:
        print("车牌区域为空")
        return
    
    print(f"车牌区域: {x1},{y1} to {x2},{y2}, 大小: {plate_roi.shape}")
    
    # 保存原始车牌区域
    debug_dir = 'resources/image/debug'
    os.makedirs(debug_dir, exist_ok=True)
    cv2.imwrite(os.path.join(debug_dir, 'original_plate.jpg'), plate_roi)
    print(f"车牌区域已保存到: {os.path.join(debug_dir, 'original_plate.jpg')}")
    
    # 显示车牌区域
    cv2.imshow('Plate ROI', plate_roi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 进行OCR识别
    print("\n开始OCR识别...")
    result = improved_ocr.recognize_plate(plate_roi)
    print(f"最终识别结果: {result}")

def auto_detect_and_debug(image_path):
    """自动检测车牌并调试"""
    from models.yolo.yoloPhoto import license_plate_detector
    
    print(f"自动检测图片: {image_path}")
    
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return
    
    # 检测车牌
    license_plates = license_plate_detector(img)[0]
    
    # 提取检测结果
    for i, license_plate in enumerate(license_plates.boxes.data.tolist()):
        x1, y1, x2, y2, license_plateScore, license_plateClass_id = license_plate
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        print(f"\n=== 检测到第 {i+1} 个车牌 ===")
        print(f"位置: ({x1}, {y1}) to ({x2}, {y2})")
        print(f"置信度: {license_plateScore:.3f}")
        
        # 调试这个车牌区域
        debug_single_plate(image_path, x1, y1, x2, y2)

if __name__ == "__main__":
    # 使用方法1: 手动指定坐标调试
    # test_image = "resources/image/your_test_image.jpg"
    # coordinates = (100, 200, 300, 250)  # 替换为实际坐标
    # debug_single_plate(test_image, *coordinates)
    
    # 使用方法2: 自动检测并调试（推荐）
    test_image = "resources/image/211104-JPJ-fancy-plate-750x375.jpg"  # 替换为你的图片路径
    auto_detect_and_debug(test_image)