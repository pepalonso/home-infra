from ast import main
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from sqlalchemy import case, false

from app.firebase_auth import verify_token
from app.utils import parse_datetime
from .models import Section, Task, User
from . import db

main = Blueprint("main", __name__)
CORS(main)


@main.route("/tasks", methods=["GET"])
def get_tasks():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401
    tasks = (
        Task.query.filter_by(user_id=user_id)
        .filter(Task.is_completed == false())
        .order_by(
            Task.importance.desc(),
            case((Task.deadline.is_(None), 1), else_=0),
            (Task.deadline.asc()),
        )
        .all()
    )
    return jsonify([task.to_dict() for task in tasks]), 200


@main.route("/task", methods=["POST"])
def add_task():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    data = request.json

    if not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    if not data.get("task_number"):
        return jsonify({"error": "Task number is required"}), 400

    if data.get("deadline"):
        try:
            data["deadline"] = parse_datetime(data["deadline"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    new_task = Task(
        user_id=user_id,
        title=data["title"],
        task_number=data["task_number"],
        description=data.get("description", None),
        deadline=data.get("deadline", None),
        importance=data.get("importance", None),
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201


@main.route("/update/<int:task_number>", methods=["PUT"])
def update_task(task_number):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    data = request.json

    if data.get("deadline"):
        try:
            data["deadline"] = parse_datetime(data["deadline"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    task = (
        Task.query.filter_by(task_number=task_number).filter_by(user_id=user_id).first()
    )
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.is_completed = data.get("is_completed", task.is_completed)
    task.deadline = data.get("deadline", task.deadline)
    task.importance = data.get("importance", task.importance)

    db.session.commit()
    return jsonify(task.to_dict()), 200


@main.route("/new-task-number", methods=["GET"])
def new_task_number():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401
    tasks = Task.query.filter_by(user_id=user_id)
    last_task = tasks.order_by(Task.task_number.desc()).first()
    new_task_number = last_task.task_number + 1 if last_task else 1
    return jsonify({"new_task_number": new_task_number}), 200


@main.route("/delete/<int:task_number>", methods=["DELETE"])
def delete_task(task_number):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    task = (
        Task.query.filter_by(task_number=task_number).filter_by(user_id=user_id).first()
    )
    if not task:
        return jsonify({"error": "Task not found"}), 404

    Task.query.filter_by(id=task.id).delete()
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200


@main.route("/user", methods=["GET"])
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


@main.route("/sections", methods=["GET"])
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


@main.route("/section", methods=["POST"])
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


@main.route("/section/<int:section_id>", methods=["PUT"])
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


@main.route("/section/<int:section_id>", methods=["DELETE"])
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

    Section.query.get(section_id).delete()
    db.session.commit()

    return jsonify({"message": "Section deleted"}), 200
