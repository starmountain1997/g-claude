import cv2
import numpy as np
import sys
import os

def remove_background(img, iterations=5):
    """
    Removes background using GrabCut algorithm.
    """
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    
    height, width = img.shape[:2]
    # Assume the subject is mostly in the center, leave a 5px margin
    rect = (5, 5, width - 10, height - 10)
    
    # GrabCut with a rectangular mask
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, iterations, cv2.GC_INIT_WITH_RECT)
    
    # mask = 0 (definite bg), 2 (probable bg) -> 0 (bg)
    # mask = 1 (definite fg), 3 (probable fg) -> 1 (fg)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    
    # Create an alpha channel based on the GrabCut mask
    alpha = mask2 * 255
    
    # Split the original image and merge with alpha channel
    b, g, r = cv2.split(img)
    rgba = cv2.merge([b, g, r, alpha.astype(np.uint8)])
    
    return rgba

def crop_to_content(rgba):
    """
    Crops the image to its non-transparent boundaries.
    """
    alpha = rgba[:, :, 3]
    coords = cv2.findNonZero(alpha)
    if coords is None:
        return rgba
    
    # Find bounding box of non-zero alpha values
    x, y, w, h = cv2.boundingRect(coords)
    return rgba[y:y+h, x:x+w]

def process_image(input_path, output_path):
    # Read the image
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Could not read image at {input_path}")
        return

    print(f"Processing {input_path}...")
    
    # 1. Remove background (Matting)
    rgba = remove_background(img)
    
    # 2. Crop edges (Bounding Box)
    final_img = crop_to_content(rgba)
    
    # Save the result as PNG to support transparency
    cv2.imwrite(output_path, final_img)
    print(f"Saved result to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python matting.py <input_path> <output_path>")
    else:
        process_image(sys.argv[1], sys.argv[2])
