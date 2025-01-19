from flask import Blueprint, jsonify, request
from flask_cors import CORS
from sqlalchemy import case, false

from app.firebase_auth import verify_token
from app.models import Task, User
from app.utils import parse_datetime
from .. import db


task = Blueprint("task", __name__)
CORS(task)


@task.route("/tasks", methods=["GET"])
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


@task.route("/tasks/<int:section_id>", methods=["GET"])
def get_tasks_by_section(section_id):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    tasks = (
        Task.query.filter_by(user_id=user_id)
        .filter_by(section=section_id)
        .filter(Task.is_completed == false())
        .order_by(
            Task.importance.desc(),
            case((Task.deadline.is_(None), 1), else_=0),
            (Task.deadline.asc()),
        )
        .all()
    )
    return jsonify([task.to_dict() for task in tasks]), 200


@task.route("/task", methods=["POST"])
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
        section=data.get("section", None),
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201


@task.route("/update/<int:task_number>", methods=["PUT"])
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
    task.section = data.get("section", task.section)
    task.importance = data.get("importance", task.importance)

    db.session.commit()
    return jsonify(task.to_dict()), 200


@task.route("/task/<int:task_number>", methods=["DELETE"])
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

    task.is_completed = True
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200
