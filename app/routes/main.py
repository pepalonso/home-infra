from datetime import datetime, timedelta, timezone
import os
from weakref import ref
from flask import Blueprint, jsonify, request
from flask_cors import CORS
import openai
from sqlalchemy import false

from app.firebase_auth import verify_token
from app.models import AiSummaryExecutions, Section, Task
from app.utils import load_prompt
from .. import db


main = Blueprint("main", __name__)
CORS(main)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

MAX_RETRIES = 4


@main.route("/")
def index():
    return jsonify({"message": "ruta principal"})


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

    last_archived_task = (
        Task.query.filter_by(user_id=user_id)
        .order_by()
        .order_by(Task.task_number.desc())
        .first()
    )
    new_archived_task_number = (
        last_archived_task.task_number + 1 if last_archived_task else 1
    )

    if new_task_number < new_archived_task_number:
        new_task_number = new_archived_task_number

    return jsonify({"new_task_number": new_task_number}), 200


@main.route("/generate-report", methods=["GET"])
def generate_report():

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    now = datetime.now(timezone.utc)
    last_24_hours = now - timedelta(hours=24)

    last_user_report = (
        AiSummaryExecutions.query.filter_by(user_id=user_id)
        .filter(AiSummaryExecutions.generated_at >= last_24_hours)
        .order_by(AiSummaryExecutions.generated_at.desc())
        .first()
    )

    if last_user_report:
        return jsonify({"report": last_user_report.summary})

    tasks = (
        Task.query.filter_by(user_id=user_id).filter(Task.is_completed == false()).all()
    )
    sections = Section.query.filter_by(user=user_id).all()
    try:
        prompt = "Tasques:\n"
        for task in tasks:
            prompt += f"- Titol: {task.title}, Descriptio: {task.description}, "
            prompt += f"Data limit: {task.deadline}, Importancia: {task.importance}, "
            prompt += f"Secció: {task.section}\n"

        prompt += "\Seccions:\n"
        for section in sections:
            prompt += f"- {section.name}\n"

        prompt_developer = load_prompt("system.txt")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer",
                    "content": prompt_developer,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        report_content = completion.choices[0].message.content

        new_ai_summary = AiSummaryExecutions(
            user_id=user_id,
            summary=report_content,
        )

        db.session.add(new_ai_summary)
        db.session.commit()

        return jsonify({"report": report_content})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@main.route("/refresh-summary", methods=["GET"])
def refresh_report():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    now = datetime.now(timezone.utc)
    last_24_hours = now - timedelta(hours=24)

    last_user_reports = (
        AiSummaryExecutions.query.filter_by(user_id=user_id)
        .filter(AiSummaryExecutions.generated_at >= last_24_hours)
        .count()
    )

    if last_user_reports > MAX_RETRIES:
        return jsonify({"error": "Too many requests"}), 429

    tasks = (
        Task.query.filter_by(user_id=user_id).filter(Task.is_completed == false()).all()
    )
    sections = Section.query.filter_by(user=user_id).all()
    try:
        prompt = "Tasques:\n"
        for task in tasks:
            prompt += f"- Titol: {task.title}, Descriptio: {task.description}, "
            prompt += f"Data limit: {task.deadline}, Importancia: {task.importance}, "
            prompt += f"Secció: {task.section}\n"

        prompt += "\Seccions:\n"
        for section in sections:
            prompt += f"- {section.name}\n"

        prompt_developer = load_prompt("system.txt")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer",
                    "content": prompt_developer,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        report_content = completion.choices[0].message.content

        new_ai_summary = AiSummaryExecutions(
            user_id=user_id,
            summary=report_content,
        )

        db.session.add(new_ai_summary)
        db.session.commit()

        return jsonify({"report": report_content})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@main.route("/get-refreshes-left", methods=["GET"])
def get_refreshes_left():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
    firebase_token = auth_header.split(" ")[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    try:

        now = datetime.now(timezone.utc)
        last_24_hours = now - timedelta(hours=24)

        last_user_reports = (
            AiSummaryExecutions.query.filter_by(user_id=user_id)
            .filter(AiSummaryExecutions.generated_at >= last_24_hours)
            .count()
        )

        return jsonify({"refreshes_left": MAX_RETRIES - last_user_reports})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
