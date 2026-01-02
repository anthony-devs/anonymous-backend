from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from extensions import get_mongo

messages_bp = Blueprint("messages", __name__)

# -------------------------------
# GET MESSAGES (JWT-protected)
# -------------------------------
@messages_bp.route("/get", methods=["GET"])
@jwt_required()
def get_messages():
    claims = get_jwt()
    db = get_mongo(current_app)
    users = db.users
    messages = db.messages

    user = users.find_one({"username": claims["sub"]})
    username = user["username"] if user else None
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    cursor = messages.find({"to_username": username}).sort("created_at", -1)

    result = [{"content": m["content"], "created_at": m["created_at"].isoformat()} for m in cursor]

    # Update last active
    users.update_one({"username": username}, {"$set": {"last_active_at": datetime.utcnow()}})

    return jsonify({"messages": result})


# -------------------------------
# ADD MESSAGE (PUBLIC, ANONYMOUS)
# -------------------------------
@messages_bp.route("/add", methods=["POST"])
def add_message():
    """
    Anyone can send a message to a username.
    No JWT required. Completely anonymous.
    """
    db = get_mongo(current_app)
    users = db.users
    messages = db.messages

    data = request.get_json()
    to_username = data.get("to_username")
    content = data.get("content")

    if not to_username or not content:
        return jsonify({"error": "to_username and content are required"}), 400

    # Ensure recipient exists
    recipient = users.find_one({"username": to_username})
    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404

    # Insert anonymous message
    messages.insert_one({
        "to_username": to_username,
        "content": content,
        "created_at": datetime.utcnow()
    })

    return jsonify({"status": "Message sent"}), 201
