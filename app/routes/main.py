from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, request
from flask_cors import CORS

from app.firebase_auth import verify_token
from app.models import AiSummaryExecutions, Task
from app.utils import generate_ai_summary
from .. import db


main = Blueprint("main", __name__)
CORS(main)

MAX_RETRIES = 10


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

    try:

        ai_summary = generate_ai_summary(user_id)

        new_ai_summary = AiSummaryExecutions(
            user_id=user_id,
            summary=ai_summary,
        )

        db.session.add(new_ai_summary)
        db.session.commit()

        return jsonify({"report": ai_summary})

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

    try:

        now = datetime.now(timezone.utc)
        last_24_hours = now - timedelta(hours=24)

        last_user_reports = (
            AiSummaryExecutions.query.filter_by(user_id=user_id)
            .filter(AiSummaryExecutions.generated_at >= last_24_hours)
            .count()
        )

        if last_user_reports > MAX_RETRIES:
            return jsonify({"error": "Too many requests"}), 429

        if last_user_reports > 0:

            last_report = (
                AiSummaryExecutions.query.filter_by(user_id=user_id)
                .filter(AiSummaryExecutions.generated_at >= last_24_hours)
                .order_by(AiSummaryExecutions.generated_at.desc())
                .first()
            )

            ai_summary = generate_ai_summary(
                user_id=user_id, last_user_report=last_report
            )

        ai_summary = generate_ai_summary(user_id=user_id)

        new_ai_summary = AiSummaryExecutions(
            user_id=user_id,
            summary=ai_summary,
        )

        db.session.add(new_ai_summary)
        db.session.commit()

        return jsonify({"report": ai_summary})

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
