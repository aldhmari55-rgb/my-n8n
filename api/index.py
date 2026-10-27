import os
import requests
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# جلب متغيرات البيئة
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
PAGE_ACCESS_TOKEN = os.environ.get("META_PAGE_ACCESS_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()  # مفتاح الذكاء الاصطناعي مستقبلاً

# تهيئة عميل Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error initializing Supabase: {e}")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "Sadarah AI Agent is running successfully!",
        "supabase_connected": supabase is not None,
        "token_configured": bool(PAGE_ACCESS_TOKEN)
    })

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1. التحقق من الـ Webhook الخاص بـ Meta (GET)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        verify_token = os.environ.get("META_VERIFY_TOKEN", "sadarah_secure_token")
        
        if mode and token:
            if mode == "subscribe" and token == verify_token:
                return challenge, 200
            else:
                return "Verification failed", 403
        return "Hello Meta Webhook", 200

    # 2. استقبال الرسائل والتفاعلات (POST)
    elif request.method == "POST":
        data = request.json
        print("Received Webhook data:", data)

        # حفظ التفاعل الخام في قاعدة بيانات Supabase
        if supabase and data:
            try:
                supabase.table("social_interactions").insert({"payload": data}).execute()
            except Exception as e:
                print(f"Error saving to Supabase: {e}")

        # معالجة الرسائل وإرسال الرد الذكي
        try:
            if data.get("object") == "page":
                for entry in data.get("entry", []):
                    messaging_events = entry.get("messaging", [])
                    for event in messaging_events:
                        sender_id = event.get("sender", {}).id if hasattr(event.get("sender", {}), "get") else event.get("sender", {}).get("id")
                        if event.get("message") and sender_id:
                            message_text = event.get("message", {}).get("text", "")
                            print(f"Message from {sender_id}: {message_text}")
                            
                            # توليد الرد الذكي (AI Persona Response)
                            ai_reply = generate_sadarah_ai_response(message_text)
                            
                            # إرسال الرد الفعلي للعميل عبر Meta API
                            send_facebook_message(sender_id, ai_reply)
                            
        except Exception as e:
            print(f"Error processing messaging event: {e}")

        return jsonify({"status": "received"}). 200

def generate_sadarah_ai_response(user_message):
    """
    توليد رد ذكي يعكس شخصية وكالة صدارة للتسويق والخدمات الرقمية
    """
    msg = user_message.lower()
    
    # قواعد الرد الذكي المبدئية (أو ربطها بنموذج الذكاء الاصطناعي مباشرة)
    if "سعر" in msg or "أسعار" in msg or "باقات" in msg:
        return "أهلاً بك! نقدم في وكالة صدارة باقات تسويقية متكاملة تبدأ من إدارة الحملات وحتى صناعة المحتوى والهويات البصرية. هل تود أن نرسل لك تفاصيل الباقات الحالية؟"
    elif "خدمات" in msg or "التسويق" in msg:
        return "نحن في صدارة نختص بـ: إدارة الحملات الإعلانية الممولة، تصميم الهويات البصرية، إدارة منصات التواصل، وحلول المتاجر الرقمية. كيف يمكننا خدمة نشاطك اليوم؟"
    elif "السلام" in msg or "مرحباً" in msg or "هلا" in msg:
        return "وعليكم السلام ورحمة الله وبركاته! أهلاً بك في وكالة صدارة للتسويق والخدمات الرقمية. معك المساعد الذكي، كيف يمكنني مساعدتك في تطوير عملك وزيادة مبيعاتك اليوم؟"
    else:
        return "أهلاً بك! تم استلام رسالتك في وكالة صدارة للتسويق والخدمات الرقمية، وسيقوم أحد مستشارينا بالتواصل معك قريباً للإجابة على استفسارك بكافة التفاصيل."

def send_facebook_message(recipient_id, text):
    """
    دالة إرسال الرسالة العائدة إلى المستخدم عبر Meta Graph API
    """
    if not PAGE_ACCESS_TOKEN:
        print("Page Access Token is missing!")
        return
        
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print("Meta Send Response:", response.json())
    except Exception as e:
        print(f"Error sending message to Meta: {e}")

if __name__ == "__main__":
    app.run(debug=True)
