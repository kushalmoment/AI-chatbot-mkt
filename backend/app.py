import os
import json  # ★修正点1： jsonをインポート
from pathlib import Path
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import your blueprint
from routes.chat import chat_bp

# --- ★修正点2： Firebase初期化ブロックを丸ごと置き換え ---
# Initialize Firebase
key_json_string = os.getenv("FIREBASE_KEY_JSON") # Renderで設定した "FIREBASE_KEY_JSON" を読み込む
if not key_json_string:
    # Fallback to local firebase-key.json file for development
    key_path = Path(__file__).parent / 'firebase-key.json'
    try:
        with open(key_path, 'r') as f:
            key_dict = json.load(f)
    except FileNotFoundError:
        raise ValueError("FIREBASE_KEY_JSON environment variable not set and firebase-key.json not found.")
else:
    try:
        # 環境変数から読み込んだJSON文字列を辞書（dict）に変換
        key_dict = json.loads(key_json_string)
    except json.JSONDecodeError:
        raise ValueError("Failed to decode FIREBASE_KEY_JSON. Check the value in Render.")

cred = credentials.Certificate(key_dict) # ファイルパスではなく、中身（辞書）を直接渡す
firebase_admin.initialize_app(cred)
# --- ここまでが置き換えたブロック ---

# Create and configure the Flask app
app = Flask(__name__)
CORS(app)
app.static_folder = str((Path(app.root_path) / '..' / 'frontend' / 'build' / 'static').resolve())
app.static_url_path = '/static'
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# Serve static files from frontend/build
frontend_build_path = (Path(app.root_path) / '..' / 'frontend' / 'build').resolve()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Skip serving frontend for API routes
    if path.startswith('api/'):
        from flask import abort
        abort(404)
    if path != "" and (frontend_build_path / path).exists():
        return send_from_directory(str(frontend_build_path), path)
    else:
        return send_from_directory(str(frontend_build_path), 'index.html')

# Run the server
if __name__ == '__main__':
    app.run(port=5000, debug=True)