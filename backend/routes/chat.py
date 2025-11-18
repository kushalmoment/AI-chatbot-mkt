import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore as gcf
from flask import Blueprint, request, jsonify
from services.gemini_service import chat_with_gemini

# Firestoreデータベースのクライアントを初期化
# この初期化は app.py の最初で行うべきです
try:
    db = firestore.client()
except ValueError:
    # アプリがまだ初期化されていない場合（テスト時など）
    # Firebaseがapp.pyで初期化されているはずなので、ここではエラーを投げる
    raise ValueError("Firebase app not initialized. Ensure app.py initializes Firebase before importing this module.")

chat_bp = Blueprint("chat_bp", __name__)

@chat_bp.route("/message", methods=["POST"])
def chat_message():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        # 変更点： フロントから送られたuserIdを取得
        user_id = data.get("userId")
        user_message = data.get("message")

        if not user_id or not user_message:
            return jsonify({"error": "userIdとmessageは必須です"}), 400

        # 1. Gemini APIに応答をリクエスト
        ai_response = chat_with_gemini(user_message)

        if ai_response:
            # 2. 【★最重要★】会話履歴をFirestoreに保存
            try:
                # 'conversations' というコレクションに、ユーザーID名のドキュメントを作成
                conversation_ref = db.collection("conversations").document(user_id)
                
                # そのドキュメント内の 'messages' という配列に、会話を追加していく
                conversation_ref.set({
                    "messages": gcf.ArrayUnion([
                        {"role": "user", "content": user_message, "timestamp": gcf.SERVER_TIMESTAMP},
                        {"role": "assistant", "content": ai_response, "timestamp": gcf.SERVER_TIMESTAMP}
                    ])
                }, merge=True) # merge=Trueで、ドキュメントが存在すれば追記、なければ新規作成
            except Exception as e:
                print(f"Firestoreへの保存中にエラーが発生: {e}")
                # ここではエラーを返さず、会話は続行させる（チャットが止まらないようにするため）

            # 3. フロントエンドに応答を返す
            return jsonify({"reply": ai_response})
        else:
            return jsonify({"error": "AIからの応答がありません"}), 500

    except Exception as e:
        print(f"チャット処理中にエラーが発生: {e}")
        return jsonify({"error": str(e)}), 500