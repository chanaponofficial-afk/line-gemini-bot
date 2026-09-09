import os
from flask import Flask, abort, request
from google import genai
from google.genai import types
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ดึง Keys จาก Environment Variables
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ตั้งค่า Gemini SDK
client = genai.Client(api_key=GEMINI_API_KEY)


# ฟังก์ชันอ่านข้อมูลจากไฟล์ prompt.txt
def load_system_instruction():
    if os.path.exists("prompt.txt"):
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    return ""


SYSTEM_INSTRUCTION = load_system_instruction()


@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    try:
        # เรียกใช้ gemini-3.5-flash-lite (โควตาฟรีสูงสุด 500 ครั้ง/วัน)
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            ),
        )
        reply_text = response.text
    except Exception as e:
        print(f"Error: {e}")
        # ป้องกันไม่ให้ส่งข้อความ Error ของระบบไปหาลูกค้า
        reply_text = "ขออภัยด้วยครับ ขณะนี้ระบบบอทยุ่งชั่วคราว โปรดลองใหม่อีกครั้งในภายหลัง"

    # ส่งคำตอบกลับไปหาผู้ใช้ใน LINE
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text=reply_text)
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
