import google.generativeai as genai

# กำหนดรายชื่อโมเดล Lite สองตัวที่มีโควตาตัวละ 500 ครั้ง/วัน
LITE_MODELS = [
    "gemini-3.5-flash-lite",  # ใช้ตัวนี้ก่อน (500 RPD)
    "gemini-3.1-flash-lite",  # ถ้าตัวแรกเต็ม สลับมาตัวนี้ทันที (อีก 500 RPD)
]


def reply_chat(user_message):
    for model_name in LITE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(user_message)
            return response.text  # ตอบสำเร็จ ให้ส่งข้อความกลับทันที
        except Exception as e:
            # ถ้าเจอ Error 429 (โควตาเต็ม) ให้ข้ามไปลองโมเดลถัดไป
            print(f"Model {model_name} quota exceeded. Switching to next...")
            continue

    return "ขออภัยครับ โควตาฟรีประจำวัน (1,000 ครั้ง) เต็มแล้ว"
