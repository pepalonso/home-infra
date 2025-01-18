import os
from flask import Blueprint, jsonify, request
from flask_cors import CORS
import openai

from app.firebase_auth import verify_token
from app.models import Section, Task
from app.utils import load_prompt


main = Blueprint("main", __name__)
CORS(main)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


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

    tasks = Task.query.filter_by(user_id=user_id).all()
    sections = Section.query.filter_by(user=user_id).all()
    try:
        prompt = "Tasks:\n"
        for task in tasks:
            prompt += f"- Name: {task.title}, Description: {task.description}, "
            prompt += f"Deadline: {task.deadline}, Importance: {task.importance}, "
            prompt += f"Section: {task.section}\n"

        prompt += "\nSections:\n"
        for section in sections:
            prompt += f"- {section.name}\n"

        prompt_text = load_prompt("system.txt")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer",
                    "content": prompt_text,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        report_content = completion.choices[0].message.content
        print(report_content)

        return jsonify({"report": report_content})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
