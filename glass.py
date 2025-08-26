#------------------#
# import cv2
# import re
# from ultralytics import YOLO
# from paddleocr import PaddleOCR
# import json

# # -------------------------
# # 1. Load model
# # -------------------------
# detector = YOLO("runs/detect/train12/weights/best.pt")
# ocr = PaddleOCR(use_angle_cls=True, lang='en')

# # -------------------------
# # 2. Hàm chuẩn hóa OCR text
# # -------------------------
# def normalize_text(text: str) -> str:
#     text = text.strip()
#     text = re.sub(r"\s+", " ", text)
#     text = re.sub(r"[xX×*]", "x", text)  # chuẩn hóa dấu nhân
#     return text

# # -------------------------
# # 3. Hàm parse từng loại thông tin
# # -------------------------
# def parse_glass(text: str, area_text: str = None) -> dict:
#     text = normalize_text(text)
#     match_order = re.search(r"(\d+\/[A-Za-z\s]+)", text)
#     dong_hang = match_order.group(1).strip() if match_order else None

#     if area_text:
#         area_numbers = re.findall(r"\d+", normalize_text(area_text))
#         if len(area_numbers) >= 2:
#             glass_numbers = re.findall(r"\d+", text)
#             if any(num in glass_numbers for num in area_numbers):
#                 dai, rong = sorted([int(area_numbers[0]), int(area_numbers[1])], reverse=True)
#                 return {"dong_hang": dong_hang, "dai": dai, "rong": rong}

#     numbers = re.findall(r"\d+", text)
#     dai, rong = None, None
#     if len(numbers) >= 2:
#         dai, rong = int(numbers[0]), int(numbers[1])
#     return {"dong_hang": dong_hang, "dai": dai, "rong": rong}

# def parse_area(text: str) -> dict:
#     text = normalize_text(text)
#     numbers = re.findall(r"\d+", text)
#     dai, rong = None, None
#     if len(numbers) >= 2:
#         dai, rong = sorted([int(numbers[0]), int(numbers[1])], reverse=True)
#     return {"dai": dai, "rong": rong}

# def parse_code(text: str) -> dict:
#     text = normalize_text(text)
#     ma = re.search(r"Code\s*([A-Za-z0-9]+)", text)
#     ma = ma.group(1) if ma else None
#     day = re.search(r"(\d+)\s*mm", text)
#     day = int(day.group(1)) if day else None
#     can_nang = re.search(r"([\d\.]+)\s*Kg", text)
#     can_nang = float(can_nang.group(1)) if can_nang else None
#     return {"ma": ma, "day": day, "can_nang": can_nang}

# def parse_para(text: str) -> dict:
#     """
#     Ví dụ OCR: 'SHEETPARAMETERS X Dim. 3345 mm Y Dim. 2432 mm Total Waste 5,70'
#     Kết quả: {"dai": 3345, "rong": 2432, "hao_phi": 5.70}
#     """
#     text = normalize_text(text)
#     dai = re.search(r"X\s*Dim\.?\s*(\d+)", text)
#     dai = int(dai.group(1)) if dai else None
#     rong = re.search(r"Y\s*Dim\.?\s*(\d+)", text)
#     rong = int(rong.group(1)) if rong else None
#     hao_phi = re.search(r"Total\s*Waste\s*([\d\.,]+)", text)
#     hao_phi = float(hao_phi.group(1).replace(",", ".")) if hao_phi else None
#     return {"dai": dai, "rong": rong, "hao_phi": hao_phi}

# # -------------------------
# # 4. Hàm extract_text từ YOLO + OCR
# # -------------------------
# def extract_text(img_path):
#     img = cv2.imread(img_path)
#     results = detector(img_path, conf=0.3)
#     data = {"Glass": [], "Area": [], "Code": [], "Para": [], "Numbers": []}

#     for r in results[0].boxes:
#         cls_id = int(r.cls[0])
#         x1, y1, x2, y2 = map(int, r.xyxy[0])
#         crop = img[y1:y2, x1:x2]
#         ocr_result = ocr.ocr(crop, cls=True)
#         text = " ".join([line[1][0] for line in ocr_result[0]]) if ocr_result[0] else ""

#         if cls_id == 2:  # Glass
#             data["Glass"].append(parse_glass(text))
#         elif cls_id == 4:  # Area
#             data["Area"].append(parse_area(text))
#         elif cls_id == 0:  # Code
#             data["Code"].append(parse_code(text))
#         elif cls_id == 1:  # Para
#             data["Para"].append(parse_para(text))
#         elif cls_id == 5:  # Numbers
#             data["Numbers"].append({"label": text})

#     # Gán kích thước Area vào Glass tương ứng
#     for glass in data["Glass"]:
#         for area in data["Area"]:
#             if area["dai"] and area["rong"]:
#                 glass_numbers = re.findall(r"\d+", normalize_text(" ".join(data["Glass"][data["Glass"].index(glass)]["dong_hang"] or "")))
#                 area_numbers = [str(area["dai"]), str(area["rong"])]
#                 if any(num in glass_numbers for num in area_numbers):
#                     glass["dai"] = area["dai"]
#                     glass["rong"] = area["rong"]
#                     break

#     return data

# # -------------------------
# # 5. Hàm hiển thị kết quả dưới dạng JSON
# # -------------------------
# def show_result(data):
#     numbers_data = data["Numbers"][0] if data["Numbers"] else {}
#     label = numbers_data.get("label", "1/72")
#     label_clean = re.sub(r'[^\d/]', '', label)
#     current_glass, total_glass = map(int, label_clean.split('/')) if '/' in label_clean else (1, 72)

#     image_path = "Ảnh chụp + PDF của trang hiện tại"
#     order = 1  # Giả sử thứ tự, có thể lấy từ Numbers nếu có

#     para_data = data["Para"][0] if data["Para"] else {}
#     sheet_dai = para_data.get("dai", 3345)  # Lấy từ X Dim
#     sheet_rong = para_data.get("rong", 2432)  # Lấy từ Y Dim
#     waste = para_data.get("hao_phi", 5.70)

#     code_data = data["Code"][0] if data["Code"] else {}
#     day = code_data.get("day", 5)

#     result = {
#         "Tổng số tấm kính": total_glass,
#         "Tấm kính hiện tại": f"{current_glass}/{total_glass}",
#         "Hình ảnh": image_path,
#         "Thứ tự": order,
#         "Dài": sheet_dai,
#         "Rộng": sheet_rong,
#         "Dày": day,
#         "Tấm kính con": [{"Dòng hàng": g["dong_hang"], "Dài": g["dai"], "Rộng": g["rong"]} for g in data["Glass"]],
#     }
#     print(json.dumps(result, indent=4, ensure_ascii=False))

# # -------------------------
# # 6. Main
# # -------------------------
# if __name__ == "__main__":
#     result = extract_text("smallpdf-convert-20250825-112418\\CTY REICH-images-13.jpg")
#     show_result(result)

#----------------#
# import cv2
# import re
# from ultralytics import YOLO
# from paddleocr import PaddleOCR
# import json

# # -------------------------
# # 1. Load model
# # -------------------------
# detector = YOLO("runs/detect/train12/weights/best.pt")
# ocr = PaddleOCR(use_angle_cls=True, lang='en')

# # -------------------------
# # 2. Hàm chuẩn hóa OCR text
# # -------------------------
# def normalize_text(text: str) -> str:
#     text = text.strip()
#     text = re.sub(r"\s+", " ", text)
#     text = re.sub(r"[xX×*]", "x", text)
#     return text

# # -------------------------
# # 3. Hàm parse từng loại thông tin
# # -------------------------
# def parse_glass(text: str) -> dict:
#     text = normalize_text(text)
#     match_order = re.search(r"(\d+\/[A-Za-z\s]+)", text)
#     dong_hang = match_order.group(1).strip() if match_order else None
#     # Lấy tất cả số > 0 trong Glass để so với Area
#     numbers = [int(n) for n in re.findall(r"\d+", text)]
#     return {"dong_hang": dong_hang, "numbers": numbers, "dai": None, "rong": None}

# def parse_area(text: str) -> dict:
#     text = normalize_text(text)
#     numbers = [int(n) for n in re.findall(r"\d+", text)]
#     if len(numbers) >= 2:
#         return {"dai": numbers[0], "rong": numbers[1], "numbers": numbers}
#     return {"dai": None, "rong": None, "numbers": numbers}

# def parse_code(text: str) -> dict:
#     text = normalize_text(text)
#     ma = re.search(r"Code\s*(?:Material\s*)?([A-Za-z0-9]+)", text)
#     ma = ma.group(1) if ma else None
#     day = re.search(r"(\d+)\s*mm", text)
#     day = int(day.group(1)) if day else None
#     return {"ma": ma, "day": day}

# def parse_para(text: str) -> dict:
#     text = normalize_text(text)
#     dai = re.search(r"X\s*Dim\.?\s*(\d+)", text)
#     dai = int(dai.group(1)) if dai else None
#     rong = re.search(r"Y\s*Dim\.?\s*(\d+)", text)
#     rong = int(rong.group(1)) if rong else None
#     return {"dai": dai, "rong": rong}

# def parse_numbers(text: str) -> dict:
#     text = normalize_text(text)
#     match = re.search(r"(\d+)\s*/\s*(\d+)", text)
#     if match:
#         current, total = int(match.group(1)), int(match.group(2))
#         return {"current": current, "total": total}
#     return {"current": 1, "total": 1}

# # -------------------------
# # 4. Hàm extract_text từ YOLO + OCR
# # -------------------------
# def extract_text(img_path):
#     img = cv2.imread(img_path)
#     results = detector(img_path, conf=0.3)
#     data = {"Glass": [], "Area": [], "Code": [], "Para": [], "Numbers": []}

#     for r in results[0].boxes:
#         cls_id = int(r.cls[0])
#         x1, y1, x2, y2 = map(int, r.xyxy[0])
#         crop = img[y1:y2, x1:x2]
#         ocr_result = ocr.ocr(crop, cls=True)
#         text = " ".join([line[1][0] for line in ocr_result[0]]) if ocr_result[0] else ""

#         if cls_id == 2:
#             data["Glass"].append(parse_glass(text))
#         elif cls_id == 4:
#             data["Area"].append(parse_area(text))
#         elif cls_id == 0:
#             data["Code"].append(parse_code(text))
#         elif cls_id == 1:
#             data["Para"].append(parse_para(text))
#         elif cls_id == 5:
#             data["Numbers"].append(parse_numbers(text))

#     # Gán giá trị Area vào Glass nếu số trong Glass trùng với số trong Area
#     for glass in data["Glass"]:
#         for area in data["Area"]:
#             area_dai = max(area["dai"], area["rong"])
#             area_rong = min(area["dai"], area["rong"])
            
#             # Nếu bất kỳ số nào trong Glass xuất hiện trong Area
#             if any(num in area["numbers"] for num in glass["numbers"]):
#                 glass["dai"] = area_dai
#                 glass["rong"] = area_rong
#                 break
#         # Nếu không trùng với Area, vẫn lấy số đầu tiên/ thứ tự như mặc định
#         if not glass["dai"]:
#             nums_sorted = sorted(glass["numbers"], reverse=True)
#             glass["dai"] = nums_sorted[0]
#             if len(nums_sorted) >= 2:
#                 glass["rong"] = nums_sorted[1]

#     return data

# # -------------------------
# # 5. Hiển thị kết quả JSON
# # -------------------------
# def show_result(data, img_path):
#     numbers = data["Numbers"][0] if data["Numbers"] else {"current": 1, "total": 1}
#     para = data["Para"][0] if data["Para"] else {"dai": None, "rong": None}
#     code = data["Code"][0] if data["Code"] else {"day": None}

#     result = {
#         "Tổng số tấm kính": numbers["total"],
#         "Tấm kính hiện tại": f"{numbers['current']}/{numbers['total']}",
#         "Hình ảnh": img_path,
#         "Thứ tự": numbers["current"],
#         "Dài": para.get("dai"),
#         "Rộng": para.get("rong"),
#         "Dày": code.get("day"),
#         "Tấm kính con": [
#             {
#                 "Dòng hàng": g["dong_hang"],
#                 "Dài": g["dai"],
#                 "Rộng": g["rong"]
#             } for g in data["Glass"]
#         ]
#     }
#     print(json.dumps(result, indent=4, ensure_ascii=False))

# # -------------------------
# # 6. Main
# # -------------------------
# if __name__ == "__main__":
#     img_path = "smallpdf-convert-20250825-112418\\CTY REICH-images-13.jpg"
#     data = extract_text(img_path)
#     show_result(data, img_path)

#-------------------#
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
    img_path = "smallpdf-convert-20250825-112418\\CTY REICH-images-11.jpg"
    data = extract_text(img_path)
    show_result(data, img_path)
