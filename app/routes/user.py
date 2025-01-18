from flask import Blueprint, jsonify, request
from flask_cors import CORS

from app.firebase_auth import verify_token
from app.models import User

user = Blueprint("user", __name__)
CORS(user)


@user.route("/user", methods=["GET"])
def get_user_info():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    user = User.query.get(user_id)

    return jsonify(user.to_dict()), 200
