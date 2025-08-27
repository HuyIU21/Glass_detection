#pdf_convert.py
import os
from pdf2image import convert_from_path
def pdf_to_images(pdf_path, output_folder="pdf_images", dpi=300):
    os.makedirs(output_folder, exist_ok=True)
    images = convert_from_path(pdf_path, dpi=dpi)
    img_paths = []
    
    for i, page in enumerate(images):
        img_path = os.path.join(output_folder, f"page_{i+1}.jpg")
        page.save(img_path, "JPEG")
        img_paths.append(img_path)
    return img_paths
    