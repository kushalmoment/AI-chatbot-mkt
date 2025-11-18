import os
import json  # Used to parse the Firebase key
from pathlib import Path
from flask import Flask, send_from_directory, abort
from flask_cors import CORS
from dotenv import load_dotenv  # For loading .env file locally
import firebase_admin
from firebase_admin import credentials

# Load environment variables from .env file (primarily for local development)
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import your chat blueprint
from routes.chat import chat_bp

# --- Firebase Initialization ---
# This block securely loads credentials from Render's environment variables in production,
# but falls back to a local .json file for development.

# 1. Get the key JSON string from the environment variable (for Render)
key_json_string = os.getenv("FIREBASE_KEY_JSON")

if not key_json_string:
    # 2. If not in production (e.g., local), fall back to the local file
    key_path = Path(__file__).parent / 'firebase-key.json'
    try:
        with open(key_path, 'r') as f:
            key_dict = json.load(f)
    except FileNotFoundError:
        raise ValueError("FIREBASE_KEY_JSON env var not set and firebase-key.json not found.")
else:
    # 3. If in production, parse the JSON string from the environment variable
    try:
        key_dict = json.loads(key_json_string)
    except json.JSONDecodeError:
        raise ValueError("Failed to decode FIREBASE_KEY_JSON. Check the environment variable in Render.")

# 4. Initialize Firebase with the loaded credentials (as a dictionary)
cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(cred)
# --- End of Firebase Initialization ---

# Create and configure the Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# --- Serve React Frontend ---
# Point to the static assets (CSS, JS) from the React build
app.static_folder = str((Path(app.root_path) / '..' / 'frontend' / 'build' / 'static').resolve())
app.static_url_path = '/static'

# Define the path to the main frontend build directory
frontend_build_path = (Path(app.root_path) / '..' / 'frontend' / 'build').resolve()

# Register your API blueprint
app.register_blueprint(chat_bp, url_prefix='/api/chat')

# This is the "catch-all" route that serves your React app.
# It handles the root path ('/') and any other path that isn't an API route.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Don't let the frontend route handle API calls
    if path.startswith('api/'):
        abort(404)

    # If the path is a specific file in the build (like 'manifest.json'), serve it
    if path != "" and (frontend_build_path / path).exists():
        return send_from_directory(str(frontend_build_path), path)
    # Otherwise, serve the main 'index.html' for the React app to handle
    else:
        return send_from_directory(str(frontend_build_path), 'index.html')

# Run the server (for local development only)
# Gunicorn will run the 'app' object directly in production.
if __name__ == '__main__':
    app.run(port=5000, debug=True)