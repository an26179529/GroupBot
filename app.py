from flask import Flask, request, abort
from database import init_db, insert_default_restaurants
from dotenv import load_dotenv
import os
import traceback
import sqlite3


from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

if not os.path.exists("group_order.db"):
    init_db()
    insert_default_restaurants()

# 讀取 .env 檔案
load_dotenv()

# 建立 Flask 應用
app = Flask(__name__)

# 從環境變數讀取 Token 與 Secret
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# 檢查是否讀取成功（除錯用）
print("CHANNEL_ACCESS_TOKEN =", CHANNEL_ACCESS_TOKEN)
print("CHANNEL_SECRET =", CHANNEL_SECRET)

# 建立 LINE SDK 配置與處理器
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(CHANNEL_SECRET)

def get_restaurant_list():
    conn = sqlite3.connect("group_order.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Restaurant WHERE active = 1")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "目前沒有可用的餐廳喔～"

    reply = "目前可選餐廳：\n"
    for idx, (id, name) in enumerate(rows, start=1):
        reply += f"{idx}. {name}\n"
    return reply.strip()



# Render/Vercel 健康檢查用
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running!", 200


# Webhook 路由（LINE 發訊息會打這個）
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)

    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.warning("❌ Invalid signature.")
        abort(400)
    except Exception as e:
        app.logger.error(f"❌ Webhook 處理錯誤: {e}")
        traceback.print_exc()
        abort(500)

    return 'OK'


# 接收使用者文字訊息的事件處理器
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip()

    # 新增處理指令：/restaurants
    if user_text in ["/restaurants", "查餐廳"]:
        reply_text = get_restaurant_list()
    else:
        reply_text = f"你說的是：{user_text}"

    try:
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
    except Exception as e:
        print("❌ 回覆訊息錯誤：", e)
        traceback.print_exc()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
