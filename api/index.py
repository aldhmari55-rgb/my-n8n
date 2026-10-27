import os
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# جلب بيانات اتصال Supabase من متغيرات البيئة في Vercel
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def webhook():
    # 1. التحقق من ربط الـ Webhook مع منصة Meta (Facebook & Instagram)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # الرمز السري للتحقق (يمكنك تعديله أو وضعه في Vercel Environment Variables)
        verify_token = os.environ.get("META_VERIFY_TOKEN", "sadarah_secure_token")
        
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                return challenge, 200
            else:
                return 'Forbidden', 403
        return 'Sadarah Social Agent is running successfully!', 200

    # 2. استقبال الرسائل والتفاعلات الواردة (POST)
    if request.method == 'POST':
        data = request.json
        try:
            # تسجيل التفاعل الوارد في جدول social_interactions داخل Supabase
            supabase.table("social_interactions").insert({
                "platform": "facebook_instagram",
                "user_message": str(data),
                "ai_response": "Pending AI Processing"
            }).execute()
            
            return jsonify({"status": "success", "message": "Interaction logged successfully"}), 200
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
