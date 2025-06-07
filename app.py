from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi('c05d20f53d3052ffc192d6237ee26b27')
handler = WebhookHandler('c05d20f53d3052ffc192d6237ee26b27')

@app.route("/", methods=["POST"])  # 確保路由允許 POST 請求
def webhook():
    try:
        body = request.get_data(as_text=True)  # 取得 POST 請求的內容
        json_data = request.get_json()        # 將內容轉換為 JSON 格式
        signature = request.headers['X-Line-Signature']  # 驗證 LINE 的簽名
        handler.handle(body, signature)       # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']  # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']  # 取得 LINE 收到的訊息類型
        if type == 'text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            print(msg)  # 印出內容
            reply = msg
        else:
            reply = '你傳的不是文字呦～'
        print(reply)
        line_bot_api.reply_message(tk, TextSendMessage(reply))  # 回傳訊息
    except Exception as e:
        print(f"發生錯誤: {e}")  # 如果發生錯誤，印出錯誤訊息
    return 'OK'  # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
