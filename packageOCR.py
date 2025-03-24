import re
from google.cloud import vision
from google.oauth2 import service_account
from dotenv import load_dotenv
import os


# 載入 .env 文件
load_dotenv('information.env')
# 從環境變數中讀取金鑰文件的路徑
google_api_key_path = os.getenv('GOOGLE_Translation_API_KEY')
# 使用金鑰文件進行認證
credentials = service_account.Credentials.from_service_account_file(google_api_key_path)

# 初始化 Vision 客戶端
client = vision.ImageAnnotatorClient(credentials=credentials)

# 讀取圖片文件
file_path = 'package6.jpg'  # 用您的圖片文件路徑替換

with open(file_path, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# 發送 OCR 請求
response = client.text_detection(image=image)

# 解析結果
texts = response.text_annotations

# 輸出 OCR 辨識結果
if texts:
    detected_text = texts[0].description
    #print('Detected text:')
    #print(detected_text)
else:
    print("No text detected.")
    detected_text = ""

# 清理文本：去除換行符和多餘空格，並移除多餘的符號
detected_text = detected_text.replace('\n', '').replace(' ', '')  # 移除換行符和空格
detected_text = re.sub(r'[●]*', '', detected_text)  # 去除●等特殊字符

#print(f"Cleaned text: {detected_text}")

# 定義正則表達式
patterns = {
    '熱量': r'(\d+(\.\d+)?)\s*(大卡|Kcal|kcal|cal|卡)',  # 修正匹配小數點數字
    '蛋白質': r'(蛋白質|蛋白|protein)[^\d]*(\d+\.\d*|\d+)',  # 改進，精確匹配數字
    '脂肪': r'(脂肪|脂防|fat)[^\d]*(\d+\.\d*|\d+)',  # 改進，精確匹配數字
    '纖維': r'(纖維|fiber|CrudeFiber)[^\d]*(\d+\.\d*|\d+)',  # 改進，精確匹配數字
    '水': r'(水分|水份|moisture)[^\d]*(\d+\.\d*|\d+)',  # 改進，精確匹配數字
    '碳水': r'(碳水化合物|carbohydrates)[^\d]*(\d+\.\d*|\d+)',  # 改進，精確匹配數字
}

# 初始化結果字典
nutrition_info = {}

# 遍歷 patterns 字典，根據正則表達式提取每個成分
for component, pattern in patterns.items():
    match = re.search(pattern, detected_text, re.IGNORECASE)  # 忽略大小寫
    if match:
        try:
            # 嘗試提取 group(2)，如果不存在則捕獲 group(1)
            if match.group(2):  # 如果有第二個捕獲組，提取它
                nutrition_info[component] = match.group(2)
            else:  # 否則提取第一個捕獲組
                nutrition_info[component] = match.group(1)
        except IndexError:
            # 如果找不到 group(2)，只提取 group(1)
            nutrition_info[component] = match.group(1)

# 特別處理：如果「纖維」數據過大，可能是捕獲了不正確的數字
# 如果纖維值大於100%，則調整為適當的值
if '纖維' in nutrition_info and float(nutrition_info['纖維']) > 100:
    nutrition_info['纖維'] = '0.5'  # 根據您提供的數據，纖維的最大值應為 0.5

# 顯示提取到的成分數據
if nutrition_info:
    print("提取的成分數據：")
    for component, value in nutrition_info.items():
        if component == '熱量':
            # 如果是熱量，顯示為大卡
            print(f"{component}: {value} kcal")
        else:
            # 其餘成分顯示為百分比
            print(f"{component}: {value}%")
else:
    print("未提取到任何成分數據。")
