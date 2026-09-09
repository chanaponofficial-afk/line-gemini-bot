import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google import genai

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
client = genai.Client(api_key=GEMINI_API_KEY)

# --- กำหนดข้อมูลและความประพฤติของบอทตรงนี้ ---
MY_DATA = """
คุณคือแอดมินตอบแชตของร้าน [ชื่อร้านของคุณ] 
โปรดตอบคำถามโดยใช้ข้อมูลต่อไปนี้เท่านั้น:

[ข้อมูลเกี่ยวกับร้าน]
- เวลาทำการ: เปิดทุกวัน 09:00 - 18:00 น.
- เบอร์โทรติดต่อ: 081-XXX-XXXX
- การจัดส่ง: ส่งฟรีทั่วประเทศ เมื่อซื้อครบ 500 บาท
🚆💙 นั่งรถไฟมาเพื่อสิ่งนี้! 📱✨
ลูกค้าตั้งใจเดินทางมาจากต่างจังหวัด นั่งรถไฟมาหาเราถึง ดลโมบาย สาขาเนทีฟ เพื่อมาผ่อน iPhone 17 📲🔥
ติดต่อสอบถามสินค้า
Don mobile ‼️โปรดระวังมิจฉาชิพ‼️
Line id : @donmobile12345
 https://lin.ee/Wy0J8cv
📍สาขาเนทีฟ 
📞 โทร: 089 - 242 - 2596
📍สาขาโรบินสันฉะเชิงเทรา
📞 โทร: 099-324-9655
💬 Inbox สอบถามได้เลย
💚 มีบริการผ่อนง่าย อนุมัติไว
💚 เครื่องแท้ รับประกัน พร้อม QC ทุกเครื่อง ดูน้อยลง
[รายการสินค้าและราคา]
1. สินค้า A - ราคา 250 บาท (เหมาะสำหรับ...)
2. สินค้า B - ราคา 450 บาท (คุณสมบัติ...)
✅เพจจริงต้องไม่มีโอนเงินก่อน✅
‼️ทำรายการผ่อนที่หน้าร้านเท่านั้น‼️
❌โปรดระวังมิจฉาชีพหลอกให้โอนก่อน❌

ติดต่อสอบถาม Line Official นี้เท่านั้น 🚨
@donmobile12345
คลิกลิ้งนี้เลย 👉🏻 https://lin.ee/V24uH56

เพจ · ร้านจำหน่ายโทรศัพท์มือถือ

099 324 9655

Amarawan2564@gmail.com

ช่วงราคา · ฿฿
[เงื่อนไขการเคลมสินค้า]
- สามารถเปลี่ยนคืนได้ภายใน 7 วันหากสินค้ามีปัญหา
"""

@app.route("/", methods=['GET'])
def index():
    return 'Bot is running!'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    
    try:
        # ส่งข้อมูล MY_DATA แนบไปพร้อมกับ system_instruction
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config={
                'system_instruction': MY_DATA
            }
        )
        reply_text = response.text
    except Exception as e:
        reply_text = f"เกิดข้อผิดพลาด: {str(e)}"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
