import cv2
import numpy as np
import os
from ultralytics import YOLO

# 定義食物營養表
NUTRITION_TABLE = {
    "Chicken Breast": {"Calories": 115, "Carbohydrate": 0, "Protein": 24, "Fiber": 0},
    "Beef": {"Calories": 288, "Carbohydrate": 0, "Protein": 26.3, "Fiber": 0},
    "Salmon": {"Calories": 139, "Carbohydrate": 0, "Protein": 24.3, "Fiber": 0},
    "Egg": {"Calories": 140, "Carbohydrate": 1.7, "Protein": 13, "Fiber": 0},
    "Sweet Potato": {"Calories": 110, "Carbohydrate": 27.8, "Protein": 1.6, "Fiber": 2.5},
    "Brown Rice": {"Calories": 354, "Carbohydrate": 75.1, "Protein": 7.5, "Fiber": 4.9},
    "Pumpkin": {"Calories": 74, "Carbohydrate": 17.3, "Protein": 1.9, "Fiber": 2.5},
    "Carrot": {"Calories": 41, "Carbohydrate": 9.6, "Protein": 0.9, "Fiber": 2.8},
    "Broccoli": {"Calories": 25, "Carbohydrate": 4.8, "Protein": 2.2, "Fiber": 2.3},
    "Tomato": {"Calories": 18, "Carbohydrate": 4, "Protein": 0.8, "Fiber": 1.1},
    "Blueberry": {"Calories": 57, "Carbohydrate": 14.5, "Protein": 0.7, "Fiber": 2.4},
}

# 全局模型變數
model_path = "best.pt"
yolo_model = None
if os.path.exists(model_path):
    yolo_model = YOLO(model_path)
else:
    print(f"模型檔案 {model_path} 不存在，請確認路徑！")

def detect_food(image_path):
    """使用 YOLO 模型進行食物辨識"""
    if not yolo_model:
        return None
    if not image_path or not os.path.exists(image_path):
        return None

    # 讀取圖片
    img = cv2.imread(image_path)
    if img is None:
        return None

    # 使用 YOLO 模型進行預測
    results = yolo_model.predict(source=img, conf=0.25)

    # 提取辨識結果
    detected_foods = []
    for result in results:
        for box in result.boxes.data:
            class_id = int(box[5])  # 類別 ID
            label = yolo_model.names[class_id]  # 原始標籤
            normalized_label = label.title()
            if normalized_label in NUTRITION_TABLE:
                detected_foods.append(normalized_label)
    return detected_foods

def format_nutrition(detected_foods):
    """格式化辨識出的食物的營養資訊為 LINE 訊息"""
    if not detected_foods:
        return "未辨識到任何食物！"
    response = "以下為辨識到的食材，營養標示都是以每個100克進行計算的\n"
    for food in set(detected_foods):  # 使用 set 避免重複顯示
        nutrition = NUTRITION_TABLE[food]
        response += f"食物: {food}\n"
        response += f"卡路里: {nutrition['Calories']} kcal\n"
        response += f"碳水化合物: {nutrition['Carbohydrate']} g\n"
        response += f"蛋白質: {nutrition['Protein']} g\n"
        response += f"纖維: {nutrition['Fiber']} g\n"
        response += "-" * 20 + "\n"
    return response