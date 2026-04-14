import cv2
import numpy as np
import sys
import os

def refine_mask(mask, blur_radius=5):
    """
    对遮罩进行平滑处理（羽化），消除锯齿。
    """
    # 使用高斯模糊平滑遮罩边缘
    refined = cv2.GaussianBlur(mask, (blur_radius, blur_radius), 0)
    return refined

def segment_multi_entities(img, output_prefix, save_individual=False, blur_radius=5):
    """
    识别多个实体，抠图并处理边缘。
    """
    # 1. 预处理：转灰度 -> 高斯模糊 -> 边缘检测
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # 使用 Canny 或 Threshold 找到大致轮廓
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 2. 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 过滤掉过小的噪声轮廓
    min_area = img.shape[0] * img.shape[1] * 0.005 # 至少占 0.5% 面积
    valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    print(f"检测到 {len(valid_contours)} 个主要实体。")
    
    # 3. 创建整体 Alpha 通道
    full_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    entities_data = []
    for i, cnt in enumerate(valid_contours):
        # 为每个实体生成掩码
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        
        # 整体遮罩累加
        full_mask = cv2.bitwise_or(full_mask, mask)
        
        # 如果需要保存个体
        if save_individual:
            x, y, w, h = cv2.boundingRect(cnt)
            # 提取 ROI 并处理
            entity_roi = img[y:y+h, x:x+w]
            entity_mask = mask[y:y+h, x:x+w]
            
            # 羽化个体边缘
            refined_mask = refine_mask(entity_mask, blur_radius)
            b, g, r = cv2.split(entity_roi)
            entity_rgba = cv2.merge([b, g, r, refined_mask])
            
            out_name = f"{output_prefix}_entity_{i}.png"
            cv2.imwrite(out_name, entity_rgba)
            print(f"已保存独立实体: {out_name}")

    # 4. 整体输出处理
    refined_full_mask = refine_mask(full_mask, blur_radius)
    b, g, r = cv2.split(img)
    full_rgba = cv2.merge([b, g, r, refined_full_mask])
    
    # 裁剪到内容边界
    coords = cv2.findNonZero(full_mask)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        full_rgba = full_rgba[y:y+h, x:x+w]
        
    return full_rgba

def main():
    if len(sys.argv) < 3:
        print("用法: python matting_pro.py <input> <output_prefix> [--split]")
        return

    input_path = sys.argv[1]
    output_prefix = sys.argv[2]
    save_individual = "--split" in sys.argv
    
    img = cv2.imread(input_path)
    if img is None:
        print("错误: 无法读取图像")
        return

    # 执行高级分割
    result_rgba = segment_multi_entities(img, output_prefix, save_individual)
    
    # 保存整体抠图结果
    final_output = f"{output_prefix}_full.png"
    cv2.imwrite(final_output, result_rgba)
    print(f"已完成！整体抠图结果保存至: {final_output}")

if __name__ == "__main__":
    main()
