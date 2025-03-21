import requests
from bs4 import BeautifulSoup
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
import os
import mysql.connector

# 連接 MySQL 資料庫
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="dog_breeds"
        )
    except mysql.connector.Error as err:
        print(f"資料庫連接錯誤: {err}")
        return None

def add_columns_to_table():
    db_connection = connect_to_db()
    if db_connection:
        cursor = db_connection.cursor()

        # SQL 語句：新增欄位
        query = """
        ALTER TABLE dog_breeds
        ADD COLUMN what_to_feed TEXT,
        ADD COLUMN how_to_feed TEXT,
        ADD COLUMN nutritional_tips TEXT;
        """
        try:
            cursor.execute(query)
            db_connection.commit()
            print("欄位已新增到 trytrydog 表格")
        except mysql.connector.Error as err:
            print(f"錯誤: {err}")
        finally:
            cursor.close()
            db_connection.close()

# 儲存資料到 MySQL
def save_to_db(breed_name, what_to_feed, how_to_feed, nutritional_tips):
    db_connection = connect_to_db()
    if db_connection:
        cursor = db_connection.cursor()

        # 使用 INSERT ... ON DUPLICATE KEY UPDATE 來避免重複插入
        query = """
        INSERT INTO dog_breeds (breed_name, what_to_feed, how_to_feed, nutritional_tips)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            what_to_feed = VALUES(what_to_feed),
            how_to_feed = VALUES(how_to_feed),
            nutritional_tips = VALUES(nutritional_tips)
        """
        # breed_name 這裡要傳入中文名稱
        values = (breed_name, what_to_feed, how_to_feed, nutritional_tips)
        try:
            cursor.execute(query, values)
            db_connection.commit()
            print(f"資料已儲存到資料庫：{breed_name}")
        except mysql.connector.Error as err:
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

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"請求成功，狀態碼: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            print(f"請求失敗，狀態碼: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print("請求超時！")
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
        print("沒有有效的頁面內容，無法繼續處理。")
        return None

    whattofeed_title = soup.find('h2', string=lambda x: x and 'What To Feed' in x)
    
    if whattofeed_title:
        paragraphs = []
        current_tag = whattofeed_title.find_next_sibling()

        while current_tag and current_tag.name != 'h3':
            if current_tag.name == 'p':
                paragraph_text = current_tag.get_text(strip=False).replace('\n', ' ').strip()
                paragraph_text = paragraph_text.replace('\u00A0', ' ')
                paragraphs.append(translate_text_to_chinese(paragraph_text))
            elif current_tag.name == 'ul':
                list_items = [translate_text_to_chinese(li.get_text(strip=True).replace('\u00A0', ' ')) for li in current_tag.find_all('li')]
                paragraphs.extend(list_items)
            current_tag = current_tag.find_next_sibling()

        return "\n".join(paragraphs) if paragraphs else "未提取到任何段落內容。"
    else:
        return "未找到包含 'What To Feed' 的 <h2> 標籤"

# 處理 "How To Feed" 的資訊並翻譯
def get_how_to_feed_info(soup):
    if not soup:
        print("沒有有效的頁面內容，無法繼續處理。")
        return None

    h3_title = soup.find('h3', string=lambda x: x and 'How To Feed' in x)
    
    if h3_title:
        paragraphs = []
        current_tag = h3_title.find_next_sibling()

        while current_tag:
            if current_tag.name == 'p':
                paragraph_text = current_tag.get_text(strip=False).replace('\n', ' ').strip()
                paragraph_text = paragraph_text.replace('\u00A0', ' ')
                paragraphs.append(translate_text_to_chinese(paragraph_text))
            elif current_tag.name == 'ul':
                list_items = [translate_text_to_chinese(li.get_text(strip=True).replace('\u00A0', ' ')) for li in current_tag.find_all('li')]
                paragraphs.extend(list_items)
            elif current_tag.name == 'h3':
                break
            current_tag = current_tag.find_next_sibling()

        return "\n".join(paragraphs) if paragraphs else "未提取到任何段落內容。"
    else:
        return "未找到 'How To Feed' 相關的 <h3> 標籤"

# 處理 "Nutritional Tips" 的資訊並翻譯
def get_nutritional_tips_info(soup):
    if not soup:
        print("沒有有效的頁面內容，無法繼續處理。")
        return None

    h3_title = soup.find('h3', string=lambda x: x and 'Nutritional Tips' in x)

    if h3_title:
        paragraphs = []
        current_tag = h3_title.find_next_sibling()

        while current_tag:
            if current_tag.name == 'p':
                paragraph_text = current_tag.get_text(strip=False).replace('\n', ' ').strip()
                paragraph_text = paragraph_text.replace('\u00A0', ' ')
                paragraphs.append(translate_text_to_chinese(paragraph_text))
            elif current_tag.name == 'ul':
                list_items = [translate_text_to_chinese(li.get_text(strip=True).replace('\u00A0', ' ')) for li in current_tag.find_all('li')]
                paragraphs.extend(list_items)
            elif current_tag.name == 'h3':
                break
            current_tag = current_tag.find_next_sibling()

        return "\n".join(paragraphs) if paragraphs else "未提取到任何段落內容。"
    else:
        return "未找到 'Nutritional Tips' 相關的標籤"


# 使用for迴圈自動處理所有品種
def process_all_breeds():
    for chinese_name in breed_dict.keys():
        print(f"\n正在處理品種: {chinese_name}")
        soup = fetch_breed_info(chinese_name)
        
        if soup:
            # 使用中文名稱作為 breed_name
            breed_name = chinese_name  
            what_to_feed = get_what_to_feed_info(soup)
            how_to_feed = get_how_to_feed_info(soup)
            nutritional_tips = get_nutritional_tips_info(soup)

            # 儲存資料到資料庫
            save_to_db(breed_name, what_to_feed, how_to_feed, nutritional_tips)
        else:
            print(f"無法處理品種 {chinese_name} 的資料。\n")


# 主程序
def main():
    add_columns_to_table()  # 新增欄位
    process_all_breeds()

if __name__ == "__main__":
    load_dotenv('information.env')
    translate_client = translate.Client.from_service_account_json(os.getenv('GOOGLE_Translation_API_KEY'))
    main()
