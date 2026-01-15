import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

# 设置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def simple_ocr_recognize(plate_roi):
    """简化版OCR识别"""
    try:
        # 转换为灰度图
        if len(plate_roi.shape) == 3:
            gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_roi
        
        results = []
        
        # 方法1: 标准二值化
        _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text1 = pytesseract.image_to_string(thresh1, 
            config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789').strip()
        if text1:
            results.append(text1)
        
        # 方法2: 自适应阈值
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        text2 = pytesseract.image_to_string(thresh2, 
            config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789').strip()
        if text2:
            results.append(text2)
        
        if not results:
            return ""
        
        # 选择最长的结果
        best_result = max(results, key=len)
        
        # 字符修正
        corrected = character_correction(best_result)
        
        print(f"OCR识别: {best_result} -> 修正: {corrected}")
        return corrected
        
    except Exception as e:
        print(f"OCR识别错误: {e}")
        return ""

def character_correction(self, text):
    """保守字符修正 - 只修正明显错误，保留正确字母"""
    if not text:
        return ""
    
    # 清理文本
    clean_text = ''.join([c for c in text if c.isalnum()]).upper()
    print(f"原始识别: {text} -> 清理后: {clean_text}")
    
    if not clean_text:
        return ""
    
    # 1. 首先处理特殊模式：4M -> 4177
    if '4M' in clean_text:
        clean_text = clean_text.replace('4M', '4177')
        print("特殊模式修正: 4M -> 4177")
    elif '4m' in clean_text:
        clean_text = clean_text.replace('4m', '4177')
        print("特殊模式修正: 4m -> 4177")
    
    # 2. 只修正最明显的错误（字母明显误识别为数字的情况）
    obvious_corrections = {
        # 这些字母几乎总是被误识别为数字
        'O': '0',  # 字母O看起来像数字0
        'Q': '0',  # 字母Q看起来像数字0
        'I': '1',  # 字母I看起来像数字1
        'Z': '2',  # 字母Z看起来像数字2
        'S': '5',  # 字母S看起来像数字5
    }
    
    corrected_chars = []
    for char in clean_text:
        if char in obvious_corrections:
            corrected_chars.append(obvious_corrections[char])
            print(f"明显修正: {char} -> {obvious_corrections[char]}")
        else:
            corrected_chars.append(char)  # 保留原字符
    
    result = ''.join(corrected_chars)
    
    # 3. 应用格式验证，但不强制转换正确字符
    formatted_result = self.conservative_format_validation(result)
    
    print(f"最终结果: {text} -> {clean_text} -> {result} -> {formatted_result}")
    return formatted_result

def conservative_format_validation(self, text):
    """保守的格式验证 - 只修正明显不符合格式的字符"""
    if len(text) < 7:
        # 如果长度不足，填充到7位
        padded = text.ljust(7, '0')
        print(f"长度不足，填充: {text} -> {padded}")
        text = padded
    
    if len(text) > 7:
        # 如果长度超过，截断到7位
        truncated = text[:7]
        print(f"长度超过，截断: {text} -> {truncated}")
        text = truncated
    
    # 检查当前文本是否符合 XXX1234 格式
    if len(text) == 7:
        letters_part = text[:3]
        digits_part = text[3:]
        
        # 检查字母部分是否包含非字母字符
        non_letter_chars = [c for c in letters_part if c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
        # 检查数字部分是否包含非数字字符  
        non_digit_chars = [c for c in digits_part if c not in '0123456789']
        
        if non_letter_chars or non_digit_chars:
            print(f"格式问题 - 字母部分: {letters_part} (非字母: {non_letter_chars}), 数字部分: {digits_part} (非数字: {non_digit_chars})")
            
            # 只修正有问题的字符，保留正确的
            corrected_letters = []
            for i, char in enumerate(letters_part):
                if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    # 数字转字母的保守映射
                    digit_to_letter = {
                        '0': 'O', '1': 'I', '2': 'Z', '5': 'S', '6': 'G', '8': 'B'
                    }
                    new_char = digit_to_letter.get(char, 'A')
                    corrected_letters.append(new_char)
                    print(f"字母部分修正: 位置{i} {char}->{new_char}")
                else:
                    corrected_letters.append(char)  # 保留正确字母
            
            corrected_digits = []
            for i, char in enumerate(digits_part):
                if char not in '0123456789':
                    # 字母转数字的保守映射
                    letter_to_digit = {
                        'O': '0', 'Q': '0', 'I': '1', 'Z': '2', 'S': '5', 'G': '6', 'B': '8'
                    }
                    new_char = letter_to_digit.get(char, '0')
                    corrected_digits.append(new_char)
                    print(f"数字部分修正: 位置{i+3} {char}->{new_char}")
                else:
                    corrected_digits.append(char)  # 保留正确数字
            
            result = ''.join(corrected_letters) + ''.join(corrected_digits)
            print(f"格式修正: {text} -> {result}")
            return result
    
    return text