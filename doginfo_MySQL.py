import time
import os
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from google.cloud import translate_v2 as translate  # 使用 Google Cloud Translation API
from dotenv import load_dotenv  # 用來加載 .env 文件

# 加載環境變數
load_dotenv('information.env')

# 中文與英文狗種對照
breed_dict = {
    "吉娃娃": "Chihuahua",
    "博美犬": "Pomeranian",
    "約克夏": "Yorkshire Terrier",
    "西施犬": "Shih Tzu",
    "馬爾濟斯": "Maltese",
    "臘腸犬": "Dachshund",
    "玩具貴賓犬": "Poodle (Toy)",
    "巨型貴賓犬": "Standard Poodle",
    "柴犬": "Shiba Inu",
    "雪納瑞": "Miniature Schnauzer",
    "拉布拉多": "Labrador Retriever",
    "黃金獵犬": "Golden Retriever",
    "法國鬥牛犬": "French Bulldog",
    "比熊犬": "Bichon Frise",
    "西高地白梗": "West Highland White Terrier",
    "柯基": "Pembroke Welsh Corgi",
    "哈士奇": "Siberian Husky",
    "薩摩耶": "Samoyed",
    "杜賓犬": "Doberman Pinscher",
    "大丹犬": "Great Dane",
    "羅威納": "Rottweiler",
    "鬆獅犬": "Chow Chow",
    "米格魯": "Beagle",
    "邊境牧羊犬": "Border Collie"
}

# 英文名稱與 URL 路徑
BREEDS_URL = {
    "Chihuahua": "chihuahua",
    "Pomeranian": "pomeranian",
    "Yorkshire Terrier": "yorkshire-terrier",
    "Shih Tzu": "shih-tzu",
    "Maltese": "maltese",
    "Dachshund": "dachshund",
    "Poodle (Toy)": "poodle-toy",
    "Standard Poodle": "poodle-standard",
    "Shiba Inu": "shiba-inu",
    "Miniature Schnauzer": "miniature-schnauzer",
    "Labrador Retriever": "labrador-retriever",
    "Golden Retriever": "golden-retriever",
    "French Bulldog": "french-bulldog",
    "Bichon Frise": "bichon-frise",
    "West Highland White Terrier": "west-highland-white-terrier",
    "Pembroke Welsh Corgi": "pembroke-welsh-corgi",
    "Siberian Husky": "siberian-husky",
    "Samoyed": "samoyed",
    "Doberman Pinscher": "doberman-pinscher",
    "Great Dane": "great-dane",
    "Rottweiler": "rottweiler",
    "Chow Chow": "chow-chow",
    "Beagle": "beagle",
    "Border Collie":"border-collie"
}

# 初始化 Google Cloud Translation API 客戶端
translate_client = translate.Client.from_service_account_json(os.getenv('GOOGLE_Translation_API_KEY'))

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',  # 資料庫主機
        database='dog_breeds',  # 資料庫名稱
        user='root',  # 資料庫使用者
        password='password'  # 資料庫密碼
    )
    return connection

# 在 MySQL 中創建表格
def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dog_breeds (
        id INT AUTO_INCREMENT PRIMARY KEY,
        breed_name VARCHAR(255),
        height VARCHAR(255),
        weight VARCHAR(255),
        lifespan VARCHAR(255),
        health TEXT,
        recommended_tests TEXT
    )
    """)
    connection.commit()
    cursor.close()
    connection.close()

# 將狗狗資訊插入到資料庫
def insert_breed_info(breed_name, height, weight, lifespan, health, recommended_tests):
    if not height: height = '未知'
    if not weight: weight = '未知'
    if not lifespan: lifespan = '未知'
    if not health: health = '未提供'
    if not recommended_tests: recommended_tests = '未提供'

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    INSERT INTO dog_breeds (breed_name, height, weight, lifespan, health, recommended_tests)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (breed_name, height, weight, lifespan, health, recommended_tests))
    connection.commit()
    cursor.close()
    connection.close()

# 翻譯文本為繁體中文
def translate_text_to_chinese(text):
    if text:
        try:
            result = translate_client.translate(text, target_language='zh-TW')
            return result['translatedText']
        except Exception as e:
            print(f"翻譯失敗: {e}")
            return text
    return text

def get_breed_info(chinese_name):
    if chinese_name not in breed_dict:
        print(f"抱歉，找不到 '{chinese_name}' 的相關資訊，請確認名稱是否正確！")
        return
    
    english_name = breed_dict[chinese_name]
    breed_url_part = BREEDS_URL.get(english_name)
    url = f"https://www.akc.org/dog-breeds/{breed_url_part}/"
    
    # 初始化 Selenium WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    print(f"正在訪問: {url}")
    
    # 等待頁面主要內容加載
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "breed-page__hero__overview__icon-block-wrap"))
    )
    
    # 處理 cookie 彈窗（如果存在） 
    try:
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))  # OneTrust 常見的 Accept 按鈕 ID
        )
        accept_button.click()
        print("已關閉 cookie 彈窗")
    except:
        print("未找到 cookie 彈窗，繼續執行")

    info = {
        "身高": "",
        "體重": "",
        "壽命": "",
        "健康": "",
        "推薦檢測": ""
    }
    
    # 提取身高、體重、壽命
    vital_stats = driver.find_element(By.CLASS_NAME, "breed-page__hero__overview__icon-block-wrap")
    subtitles = vital_stats.find_elements(By.TAG_NAME, "p")
    for subtitle in subtitles:
        text = subtitle.text.strip().lower()
        if "inches" in text:
            info["身高"] = text
        elif "pounds" in text:
            info["體重"] = text
        elif "years" in text:
            info["壽命"] = text
    
    # 滾動並提取健康資訊與推薦檢測
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "breed-table__accordion-padding__p"))
    )
    
    # 點擊所有健康相關標籤
    for health_section in driver.find_elements(By.CLASS_NAME, "breed-page__health"):
        try:
            driver.execute_script("arguments[0].click();", health_section) 
        except Exception as e:
            print(f"無法點擊健康區塊: {e}")
    
    # 提取健康描述
    element = driver.find_element(By.XPATH, "//div[@data-js-component='breedPage']") 
    data = element.get_attribute("data-js-props")
    
    import json
    data_dict = json.loads(data)
    health_desc = data_dict['settings']['breed_data']['health'][breed_url_part]['akc_org_health']
    if health_desc:
        translated_health = translate_text_to_chinese(health_desc)
        info["健康"] = translated_health
    
    # 提取推薦檢測
    tests = data_dict['settings']['breed_data']['health'][breed_url_part]['tests_pipe_delimited_list']
    if tests:
        translated_tests = translate_text_to_chinese(tests)
        info["推薦檢測"] = translated_tests
    
    # 把資料寫入資料庫
    insert_breed_info(chinese_name, info["身高"], info["體重"], info["壽命"], info["健康"], info["推薦檢測"])
    
    # 輸出結果
    print(f"\n{chinese_name} ({english_name}):")
    for key, value in info.items():
        print(f"{key}: {value if value else '未找到相關資訊'}")
    print("-" * 50)

def main():
    create_table()  # 確保資料表已創建
    print("開始自動抓取所有 25 種狗品種的資料並存入資料庫...")
    for chinese_name in breed_dict.keys():
        get_breed_info(chinese_name)
        time.sleep(2)  # 添加延遲避免過度請求
    print("所有資料已成功抓取並存入資料庫！")

if __name__ == "__main__":
    main()
