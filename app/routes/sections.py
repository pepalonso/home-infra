from flask import Blueprint, jsonify, request
from flask_cors import CORS

from app.firebase_auth import verify_token
from app.models import Section

from .. import db


sections = Blueprint("sections", __name__)
CORS(sections)


@sections.route("/sections", methods=["GET"])
def get_sections():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401
    sections = Section.query.filter_by(user=user_id).all()
    return jsonify([section.to_dict() for section in sections]), 200


@sections.route("/section", methods=["POST"])
def add_route():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    name = request.json.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    new_section = Section(name=name, user=user_id)
    db.session.add(new_section)
    db.session.commit()
    return jsonify(new_section.to_dict()), 201


@sections.route("/section/<int:section_id>", methods=["PUT"])
def update_section(section_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    name = request.json.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    section = Section.query.get(section_id)

    if not section:
        return jsonify({"error": "Section not found"}), 404

    section.name = name
    db.session.commit()

    return jsonify(section.to_dict()), 200


@sections.route("/section/<int:section_id>", methods=["DELETE"])
def delete_section(section_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    section = Section.query.get(section_id)

    if not section:
        return jsonify({"error": "Section not found"}), 404

    db.session.delete(section)
    db.session.commit()

    return jsonify({"message": "Section deleted"}), 200
