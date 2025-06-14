from flask import Flask, request, abort
from database import init_db, insert_default_restaurants
from dotenv import load_dotenv
import os
import traceback
import sqlite3


from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging.models import QuickReply, QuickReplyItem, MessageAction
from linebot.v3.messaging import Configuration,ApiClient,MessagingApi,ReplyMessageRequest,TextMessage
from linebot.v3.webhooks import MessageEvent,TextMessageContent

if not os.path.exists("group_order.db"):
    init_db()
    insert_default_restaurants()

# 讀取 .env 檔案
load_dotenv()

group_orders = {}

app = Flask(__name__)

# 從env讀取 Token 與 Secret
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# 建立 LINE SDK 與處理器
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(CHANNEL_SECRET)


# 查看目前餐廳
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

# 建立餐廳選單
def get_restaurant_quickreply():
    conn = sqlite3.connect("group_order.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Restaurant WHERE active = 1")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    items = []
    for (name,) in rows:
        items.append(
            QuickReplyItem(action=MessageAction(label=name, text=f"[選擇餐廳] {name}"))
        )

    return QuickReply(items=items)

# 根據餐廳提供菜單
def get_menu_by_name(name):
    conn = sqlite3.connect("group_order.db")
    cursor = conn.cursor()
    cursor.execute("SELECT menu FROM Restaurant WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "查無此餐廳"

    menu_dict = json.loads(row[0])
    menu_text = f"📋「{name}」菜單：\n"
    for item, price in menu_dict.items():
        menu_text += f"- {item}: {price} 元\n"
    return menu_text.strip()


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


# 根據使用者輸入回復訊息
@line_handler.add(MessageEvent, message=TextMessageContent)
def get_display_name(event):
    try:
        if event.source.type == "group":
            group_id = event.source.group_id
            user_id = event.source.user_id
            with ApiClient(configuration) as api_client:
                line_api = MessagingApi(api_client)
                profile = line_api.get_group_member_profile(group_id, user_id)
                return profile.display_name
        elif event.source.type == "user":
            user_id = event.source.user_id
            with ApiClient(configuration) as api_client:
                line_api = MessagingApi(api_client)
                profile = line_api.get_profile(user_id)
                return profile.display_name
        else:
            return "未知使用者"
    except Exception as e:
        print("⚠️ 取得使用者名稱失敗：", e)
        return "未知使用者"

def handle_message(event):
    user_text = event.message.text.strip()

    reply_text = ""
    quick_reply = None

    # 1. 使用者輸入 /order → 顯示餐廳選單
    if user_text == "/order":
        group_id = event.source.group_id if event.source.type == "group" else event.source.user_id
        if group_id in group_orders:
            reply_text = "⚠️ 已經有一筆訂單進行中，可以用 /done 結單或 /list 查詢"
        else:
            quick_reply = get_restaurant_quickreply()
            reply_text = "請選擇一間餐廳："
            group_orders[group_id] = {"restaurant": None, "orders": []}

    # 2. 使用者選擇餐廳（QuickReply 回傳訊息格式為：[選擇餐廳] 餐廳名稱）
    elif user_text.startswith("[選擇餐廳]"):
        group_id = event.source.group_id if event.source.type == "group" else event.source.user_id
        selected_name = user_text.replace("[選擇餐廳]", "").strip()

        if group_id not in group_orders:
            reply_text = "⚠️ 請先輸入 /order 發起訂單"
        else:
            group_orders[group_id]["restaurant"] = selected_name
            reply_text = f"✅ 餐廳「{selected_name}」選擇完成！大家可以用 `/join 餐點 數量` 加入訂單囉！"

    elif user_text.startswith("/join"):
        group_id = event.source.group_id if event.source.type == "group" else event.source.user_id

        if group_id not in group_orders or not group_orders[group_id]["restaurant"]:
            reply_text = "⚠️ 請先用 /order 選餐廳"
        else:
            try:
                parts = user_text.split()
                item = parts[1]
                qty = int(parts[2])
                user_id = event.source.user_id
                user_name = get_display_name(event)
                group_orders[group_id]["orders"].append({
                    "user_id": user_id,
                    "user_name": user_name,
                    "item": item,
                    "qty": qty
                })
                reply_text = f"✅ 已加入：{user_name} 點了 {item} x{qty}"
            except:
                reply_text = "請輸入正確格式，例如：/join 雞腿飯 1"


    elif user_text == "/list":
        group_id = event.source.group_id if event.source.type == "group" else event.source.user_id
        if group_id not in group_orders or not group_orders[group_id]["orders"]:
            reply_text = "目前沒有訂單資料"
        else:
            reply_text = f"📦 訂單明細（{group_orders[group_id]['restaurant']}）：\n"
            for o in group_orders[group_id]["orders"]:
                reply_text += f"- 👤 {o['user_name']}：{o['item']} x{o['qty']}\n"


    elif user_text == "/done":
        group_id = event.source.group_id if event.source.type == "group" else event.source.user_id
        if group_id not in group_orders:
            reply_text = "目前沒有進行中的訂單"
        else:
            orders = group_orders[group_id]["orders"]
            if not orders:
                reply_text = "還沒有人點餐喔！"
            else:
                summary = {}
                for o in orders:
                    key = o["item"]
                    summary[key] = summary.get(key, 0) + o["qty"]

                reply_text = f"✅ 訂單結束！{group_orders[group_id]['restaurant']} 統計如下：\n"
                for item, qty in summary.items():
                    reply_text += f"- {item}: {qty} 份\n"
            del group_orders[group_id]

    try:
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text, quick_reply=quick_reply)]
                )
            )
    except Exception as e:
        print("❌ 回覆訊息錯誤：", e)
        traceback.print_exc()




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
