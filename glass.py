import cv2
import re
from ultralytics import YOLO
from paddleocr import PaddleOCR
import json

# -------------------------
# 1. Load model
# -------------------------
detector = YOLO("best.pt")
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# -------------------------
# 2. Hàm chuẩn hóa OCR text
# -------------------------
def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[xX×*]", "x", text)
    return text

# -------------------------
# 3. Hàm parse từng loại thông tin
# -------------------------
def parse_glass(text: str) -> dict:
    text = normalize_text(text)
    match_order = re.search(r"(\d+\/[A-Za-z\s]+)", text)
    dong_hang = match_order.group(1).strip() if match_order else None
    # Lấy tất cả số > 0 trong Glass để so với Area
    numbers = [int(n) for n in re.findall(r"\d+", text)]
    return {"dong_hang": dong_hang, "numbers": numbers, "dai": None, "rong": None}

def parse_area(text: str) -> dict:
    text = normalize_text(text)
    numbers = [int(n) for n in re.findall(r"\d+", text)]
    if len(numbers) >= 2:
        return {"dai": numbers[0], "rong": numbers[1], "numbers": numbers}
    return {"dai": None, "rong": None, "numbers": numbers}

def parse_code(text: str) -> dict:
    text = normalize_text(text)
    # Mã
    code_match = re.search(r"Material Code\s*:\s*([A-Za-z0-9]+)", text, re.IGNORECASE)
    code = code_match.group(1) if code_match else None
    # Dày
    thick_match = re.search(r"(\d+)\s*mm", text)
    thick = int(thick_match.group(1)) if thick_match else None
    # Cân nặng
    weight_match = re.search(r"([\d\.]+)\s*Kg", text, re.IGNORECASE)
    weight = float(weight_match.group(1)) if weight_match else None
    return {"code": code, "thick": thick, "weight": weight}

def parse_para(text: str) -> dict:
    text = normalize_text(text)
    length_match = re.search(r"X\s*Dim\.?\s*(\d+)\s*mm", text, re.IGNORECASE)
    width_match = re.search(r"Y\s*Dim\.?\s*(\d+)\s*mm", text, re.IGNORECASE)
    length = int(length_match.group(1)) if length_match else None
    width = int(width_match.group(1)) if width_match else None
    # Hao phi
    waste_match = re.search(r"Total\s*Waste\s*([\d\.,]+)", text)
    waste = float(waste_match.group(1).replace(",", ".")) if waste_match else None
    return {"length": length, "width": width, "waste": waste}

def parse_numbers(text: str) -> dict:
    text = normalize_text(text)
    match = re.search(r"(\d+)\s*/\s*(\d+)", text)
    if match:
        current, total = int(match.group(1)), int(match.group(2))
        return {"current": current, "total": total}
    return {"current": 1, "total": 1}

# -------------------------
# 4. Hàm extract_text từ YOLO + OCR
# -------------------------
def extract_text(img_path):
    img = cv2.imread(img_path)
    results = detector(img_path, conf=0.3)
    data = {"Glass": [], "Area": [], "Code": [], "Para": [], "Numbers": []}

    for r in results[0].boxes:
        cls_id = int(r.cls[0])
        x1, y1, x2, y2 = map(int, r.xyxy[0])
        crop = img[y1:y2, x1:x2]
        ocr_result = ocr.ocr(crop, cls=True)
        text = " ".join([line[1][0] for line in ocr_result[0]]) if ocr_result[0] else ""

        if cls_id == 2:
            data["Glass"].append(parse_glass(text))
        elif cls_id == 4:
            data["Area"].append(parse_area(text))
        elif cls_id == 0:
            data["Code"].append(parse_code(text))
        elif cls_id == 1:
            data["Para"].append(parse_para(text))
        elif cls_id == 5:
            data["Numbers"].append(parse_numbers(text))

    # Gán giá trị Area vào Glass dựa trên matching số
    # Tìm Area có các số xuất hiện trong Glass tương ứng
    for glass in data["Glass"]:
        matched = False
        for area in data["Area"]:
            # Kiểm tra xem tất cả số trong Area có xuất hiện trong Glass không
            if all(num in glass["numbers"] for num in area["numbers"]):
                glass["dai"] = area["dai"]
                glass["rong"] = area["rong"]
                matched = True
                break
        
        if not matched:
            if glass["numbers"]:
                nums_sorted = sorted(glass["numbers"], reverse=True)
                glass["dai"] = nums_sorted[0]
                if len(nums_sorted) >= 2:
                    glass["rong"] = nums_sorted[1]

    return data

# -------------------------
# 5. Hiển thị kết quả JSON
# -------------------------
def show_result(data, img_path):
    numbers = data["Numbers"][0] if data["Numbers"] else {"current": 1, "total": 1}
    para = data["Para"][0] if data["Para"] else {"length": None, "width": None, "waste": None}
    code = data["Code"][0] if data["Code"] else {"code": None, "thick": None, "weight": None}
    result = {
        "Tổng số tấm kính": numbers["total"],  
        "Tấm kính hiện tại": f"{numbers['current']}/{numbers['total']}",
        "Hình ảnh": img_path,
        "Thứ tự": numbers['current'],  
        "Dài": para.get("length"), 
        "Rộng": para.get("width"),  
        "Dày": code.get("thick"),
        "Cân nặng": code.get("weight"),
        "Tấm kính con": [
            {
                "Dòng hàng": g["dong_hang"],
                "Dài": g["dai"],
                "Rộng": g["rong"]
            } for g in data["Glass"]
        ],
        # "Hao Phí": [
        #     {
        #         "Số m2": para.get("waste"),
        #     } 
        # ]
    }
    print(json.dumps(result, indent=4, ensure_ascii=False))

# -------------------------
# 6. Main
# -------------------------
if __name__ == "__main__":
    img_path = "smallpdf-convert-20250825-112418\\CTY REICH-images-11.jpg" # đưa đường link ảnh vào
    data = extract_text(img_path)
    show_result(data, img_path)

