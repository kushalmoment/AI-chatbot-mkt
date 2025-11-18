from flask import Blueprint, request, jsonify
from services.gemini_service import chat_with_gemini

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/message', methods=['POST'])
def handle_chat():
    """
    Handles the chat request, calls the Gemini service, and returns a response.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data['message']
    
    # Call the function that talks to the Gemini API
    bot_response = chat_with_gemini(user_message)
    
    # Return the response or an error to the frontend
    if bot_response:
        return jsonify({"reply": bot_response})
    else:
        return jsonify({"error": "Failed to get a response from the AI"}), 500
