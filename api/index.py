import os
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# جلب متغيرات البيئة وتنظيف أي مسافات زائدة قد تسبب خطأ
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

# تهيئة عميل Supabase فقط إذا كانت المتغيرات موجودة
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
        "message": "Sadarah Social Agent is running successfully!",
        "supabase_connected": supabase is not None
    })

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # التحقق من الـ Webhook الخاص بـ Meta
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

    elif request.method == "POST":
        data = request.json
        # حفظ التفاعل في قاعدة بيانات Supabase إذا كانت متصلة
        if supabase and data:
            try:
                supabase.table("social_interactions").insert({"payload": data}).execute()
            except Exception as e:
                print(f"Error saving to Supabase: {e}")
        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(debug=True)
