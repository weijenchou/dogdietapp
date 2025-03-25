# main.py
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
import sqlite3
from datetime import datetime
import tempfile
import dogdietyolo  # 匯入 dogdietyolo 模組

app = Flask(__name__)

# 替換成你的 LINE Bot 憑證
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# 初始化 SQLite 資料庫
def init_db():
    conn = sqlite3.connect('dog_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dogs (
        name TEXT PRIMARY KEY,
        birthday TEXT,
        weight REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS daily_records (
        name TEXT,
        date TEXT,
        calories REAL,
        water REAL,
        poop TEXT,
        FOREIGN KEY (name) REFERENCES dogs (name)
    )''')
    conn.commit()
    conn.close()

init_db()

# 歡迎訊息
welcome_message = """您好，我是寵物飲食機器人，請問需要什麼服務
1:新增寵物檔案
2:查看寵物檔案
3:今日營養標準
4:不可食用食物
5:保健建議
6:今日紀錄
7:查看今天紀錄
8:拍攝包裝計算卡路里(大包裝須分量)
9:拍攝鮮食計算卡路里
10:推薦寵物餐廳
請回覆你需求的數字"""

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_input = event.message.text
    user_id = event.source.user_id

    if user_input == "開始" or user_input == "start":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))
    elif user_input == "1":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入狗狗的名字："))
    elif user_input == "2":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入要查詢狗狗的名字："))
    elif user_input == "3":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入狗狗的名字：\n狗狗的狀態：\n1.正在發育的幼犬(4個月以下)\n2.正在發育的幼犬(4個月-1歲)\n3.結紮成年犬(1-7歲)\n4.未結紮成年犬(1-7歲)\n5.輕度減肥成年犬\n6.重度減肥成年犬\n7.過瘦成年犬\n8.輕度活動量\n9.劇烈活動量\n10.高齡犬\n11.懷孕中的狗媽媽\n12.哺乳中的狗媽媽\n13.生病成年犬\n請輸入狗狗目前的狀態(輸入對應數字)："))
    elif user_input == "4":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="要小心不要讓狗狗吃到這些食物喔！\n\n水果：葡萄、櫻桃、鳳梨、生番茄、酪梨、柑橘類、果核、種子\n蔬菜：蔥、韭菜、洋蔥、大蒜、辛香料\n其他：蘆薈、巧克力、夏威夷果、野生蘑菇、牛奶、生肉、糕點類\n\n幫狗狗準備的食物，請記得要全部煮熟並切成小塊喔~"))
    elif user_input == "5":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你家的狗狗是哪個品種：\n1.吉娃娃\n2.博美犬\n3.約克夏\n4.西施犬\n5.馬爾濟斯\n6.臘腸犬\n7.玩具貴賓犬\n8.巨型貴賓犬\n9.柴犬\n10.雪納瑞\n11.拉布拉多\n12.黃金獵犬\n13.法國鬥牛犬\n14.比熊犬\n15.西高地白梗\n16.柯基\n17.哈士奇\n18.薩摩耶\n19.杜賓犬\n20.大丹犬\n21.羅威納\n22.鬆獅犬\n23.米格魯\n24.邊境牧羊犬\n請輸入狗狗的品種(輸入對應數字)："))
    elif user_input == "6":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入狗狗的名字：\n今天狗狗攝取了多少卡路里：\n今天狗狗喝了多少水：\n今天狗狗有沒有上大號(Y/N)："))
    elif user_input == "7":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入狗狗的名字："))
    elif user_input == "8":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請上傳一張含成分的包裝照片"))
    elif user_input == "9":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請上傳一張含所有食材的照片(建議為未料理前)"))
    elif user_input == "10":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="搜尋寵物餐廳：\n1.目前位置\n2.輸入目的地名稱\n請輸入對應數字:"))
    elif "名字" in user_input and "生日" in user_input and "體重" in user_input:
        name = user_input.split("名字:")[1].split(" ")[0]
        birthday = user_input.split("生日:")[1].split(" ")[0]
        weight = float(user_input.split("體重:")[1].split(" ")[0])
        age = (datetime.now() - datetime.strptime(birthday, "%Y-%m-%d")).days // 365
        reply = f"狗狗的名字：{name}\n狗狗的生日：{birthday}\n狗狗的體重：{weight}公斤\n狗狗的年齡：{age}\n資料是否儲存？(Y/N)"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    elif user_input in ["Y", "N"] and "資料是否儲存" in event.message.text:
        if user_input == "Y":
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="資料已儲存！"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="資料未儲存。"))

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    if "包裝" in event.message.text:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請問這次餵食的克數"))
    elif "食材" in event.message.text:
        # 下載用戶上傳的圖片
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in message_content.iter_content():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # 使用 dogdietyolo.py 進行圖片分析
        detected_foods = dogdietyolo.detect_food(temp_file_path)
        response = dogdietyolo.format_nutrition(detected_foods)
        
        # 清理臨時檔案
        os.unlink(temp_file_path)
        
        # 回傳結果
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)