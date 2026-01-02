from flask import request, jsonify
from flask_jwt_extended import create_access_token
from bson.objectid import ObjectId
from datetime import datetime
from pymongo import ASCENDING

from . import login_bp
from extensions import mongo_client
from flask import current_app


def now():
    return datetime.utcnow()


@login_bp.record_once
def setup_indexes(state):
    app = state.app
    db = mongo_client[app.config["DB_NAME"]]

    users = db.users
    messages = db.messages

    # Auto delete after 28 days
    users.create_index(
        [("last_active_at", ASCENDING)],
        expireAfterSeconds=28 * 24 * 60 * 60
    )

    messages.create_index(
        [("created_at", ASCENDING)],
        expireAfterSeconds=28 * 24 * 60 * 60
    )


@login_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    device_id = data.get("device_id")

    if not username or not device_id:
        return jsonify({"error": "username and device_id required"}), 400

    db = mongo_client[current_app.config["DB_NAME"]]
    users = db.users

    user = users.find_one({"username": username})

    # Create account if new
    if not user:
        user_id = users.insert_one({
            "username": username,
            "device_id": device_id,
            "created_at": now(),
            "last_active_at": now()
        }).inserted_id
    else:
        # Enforce one-device rule
        if user["device_id"] != device_id:
            return jsonify({
                "error": "Account locked to another device"
            }), 403

        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_active_at": now()}}
        )
        user_id = user["_id"]

    token = create_access_token(
        identity=str(user_id),
        additional_claims={"device_id": device_id}
    )

    return jsonify({"access_token": token})
