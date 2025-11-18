import os
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import your blueprint
from routes.chat import chat_bp

# Initialize Firebase
cred_path = os.getenv("FIREBASE_CRED_PATH")
if not cred_path or not os.path.exists(cred_path):
    raise FileNotFoundError(f"Firebase credential file not found at path: {cred_path}")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Create and configure the Flask app
app = Flask(__name__)
CORS(app)
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# Run the server
if __name__ == '__main__':
    app.run(port=5000, debug=True)