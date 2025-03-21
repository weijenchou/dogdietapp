import requests
from bs4 import BeautifulSoup
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
import os
import sqlite3

# 連接 SQLite 資料庫
def connect_to_db():
    try:
        return sqlite3.connect("dog_breeds.db")
    except sqlite3.Error as err:
        print(f"資料庫連接錯誤: {err}")
        return None

# 新增欄位（如果不存在）
def add_columns_to_table():
    db_connection = connect_to_db()
    if db_connection:
        cursor = db_connection.cursor()

        # 檢查欄位是否存在，如果不存在則新增
        cursor.execute("PRAGMA table_info(dog_breeds);")
        existing_columns = [row[1] for row in cursor.fetchall()]

        columns_to_add = {
            "what_to_feed": "TEXT",
            "how_to_feed": "TEXT",
            "nutritional_tips": "TEXT"
        }

        for column, column_type in columns_to_add.items():
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE dog_breeds ADD COLUMN {column} {column_type};")
                print(f"已新增欄位: {column}")

        db_connection.commit()
        cursor.close()
        db_connection.close()

# 儲存資料到 SQLite
def save_to_db(breed_name, what_to_feed, how_to_feed, nutritional_tips):
    db_connection = connect_to_db()
    if db_connection:
        cursor = db_connection.cursor()

        # 插入或更新資料
        query = """
        INSERT INTO dog_breeds (breed_name, what_to_feed, how_to_feed, nutritional_tips)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(breed_name) DO UPDATE SET 
            what_to_feed = excluded.what_to_feed,
            how_to_feed = excluded.how_to_feed,
            nutritional_tips = excluded.nutritional_tips;
        """
        values = (breed_name, what_to_feed, how_to_feed, nutritional_tips)

        try:
            cursor.execute(query, values)
            db_connection.commit()
            print(f"資料已儲存到資料庫：{breed_name}")
        except sqlite3.Error as err:
            print(f"錯誤: {err}")
        finally:
            cursor.close()
            db_connection.close()

# 中文轉英文的字典
breed_dict = {
    "吉娃娃": "Chihuahua",
    "博美犬": "Pomeranian",
    "約克夏": "Yorkshire Terrier",
    "西施犬": "Shih Tzu",
    "馬爾濟斯": "Maltese",
    "臘腸犬": "Dachshund",
    "玩具貴賓犬": "Toy Poodle",
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
    "邊境牧羊犬": "Border Collie",
}

# 從網頁抓取資料
def fetch_breed_info(breed_input):
    breed_in_english = breed_dict.get(breed_input)
    
    if not breed_in_english:
        print(f"未找到 {breed_input} 對應的英文品種名稱，請確認品種名稱是否正確。")
        return None
    
    breed_in_english_url = breed_in_english.lower().replace(" ", "-")
    url = f"https://www.petmd.com/dog/breeds/{breed_in_english_url}"
    print(f"發送請求到: {url}")

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            print(f"請求失敗，狀態碼: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"請求錯誤：{e}")
        return None

# 翻譯文本為繁體中文
def translate_text_to_chinese(text):
    if text:
        try:
            result = translate_client.translate(text, target_language='zh-TW')
            return result['translatedText']
        except Exception as e:
            print(f"翻譯錯誤: {e}")
            return text
    return text

# 處理 "What To Feed" 的資訊並翻譯
def get_what_to_feed_info(soup):
    if not soup:
        return None

    whattofeed_title = soup.find('h2', string=lambda x: x and 'What To Feed' in x)
    if whattofeed_title:
        paragraphs = []
        current_tag = whattofeed_title.find_next_sibling()
        while current_tag and current_tag.name != 'h3':
            if current_tag.name == 'p':
                paragraphs.append(translate_text_to_chinese(current_tag.get_text(strip=True)))
            current_tag = current_tag.find_next_sibling()
        return "\n".join(paragraphs)
    return "未找到相關資訊"

# 處理 "How To Feed" 的資訊並翻譯
def get_how_to_feed_info(soup):
    if not soup:
        return None

    h3_title = soup.find('h3', string=lambda x: x and 'How To Feed' in x)
    if h3_title:
        paragraphs = []
        current_tag = h3_title.find_next_sibling()
        while current_tag and current_tag.name != 'h3':
            if current_tag.name == 'p':
                paragraphs.append(translate_text_to_chinese(current_tag.get_text(strip=True)))
            current_tag = current_tag.find_next_sibling()
        return "\n".join(paragraphs)
    return "未找到相關資訊"

# 處理 "Nutritional Tips" 的資訊並翻譯
def get_nutritional_tips_info(soup):
    if not soup:
        return None

    h3_title = soup.find('h3', string=lambda x: x and 'Nutritional Tips' in x)
    if h3_title:
        paragraphs = []
        current_tag = h3_title.find_next_sibling()
        while current_tag and current_tag.name != 'h3':
            if current_tag.name == 'p':
                paragraphs.append(translate_text_to_chinese(current_tag.get_text(strip=True)))
            current_tag = current_tag.find_next_sibling()
        return "\n".join(paragraphs)
    return "未找到相關資訊"

# 自動處理所有品種
def process_all_breeds():
    for chinese_name in breed_dict.keys():
        print(f"\n正在處理品種: {chinese_name}")
        soup = fetch_breed_info(chinese_name)
        
        if soup:
            breed_name = chinese_name  
            what_to_feed = get_what_to_feed_info(soup)
            how_to_feed = get_how_to_feed_info(soup)
            nutritional_tips = get_nutritional_tips_info(soup)
            save_to_db(breed_name, what_to_feed, how_to_feed, nutritional_tips)

# 主程序
def main():
    add_columns_to_table()
    process_all_breeds()

if __name__ == "__main__":
    load_dotenv('information.env')
    translate_client = translate.Client.from_service_account_json(os.getenv('GOOGLE_Translation_API_KEY'))
    main()
