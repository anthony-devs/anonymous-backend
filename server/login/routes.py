from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from datetime import datetime
from extensions import get_mongo

login_bp = Blueprint("login", __name__)

# -------------------------------
# Helper function for timestamps
# -------------------------------
def now():
    return datetime.utcnow()

# -------------------------------
# LOGIN / CREATE USER
# -------------------------------
@login_bp.route("/login", methods=["POST"])
def login():
    """
    Login or create a user.
    Expects JSON:
    {
        "username": "<username>",
        "device_id": "<device_id>"
    }

    Returns:
        JWT token with identity=username and device_id claim
    """
    data = request.get_json()
    username = data.get("username")
    device_id = data.get("device_id")

    if not username or not device_id:
        return jsonify({"error": "username and device_id required"}), 400

    db = get_mongo(current_app)
    users = db.users

    # Check if user exists
    user = users.find_one({"username": username})

    # -------------------------------
    # Generate non-expiring JWT token
    # -------------------------------
    token = create_access_token(
        identity=username,
        additional_claims={"device_id": device_id},
        expires_delta=False  # <--- NEVER EXPIRES
    )

    if not user:
        # Create new user
        users.insert_one({
            "username": username,
            "device_id": device_id,
            "jwt": token,
            "created_at": now(),
            "last_active_at": now()
        })
    else:
        # Enforce one device only
        if user["device_id"] != device_id:
            return jsonify({"error": "Account locked to another device"}), 403

        # Update last_active timestamp
        users.update_one(
            {"username": username},
            {"$set": {"last_active_at": now()}}
        )

    return jsonify({"access_token": token})
