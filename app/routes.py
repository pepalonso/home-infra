from ast import main
from flask import Blueprint, request, jsonify
from .models import  Task
from . import db

main = Blueprint('main', __name__)

@main.route('/task', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])


@main.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    new_task = Task(
        user_id=data['user_id'],
        title=data['title'],
        description=data.get('description', ''),
        deadline=data.get('deadline', None),
        importance=data.get('importance', 0),
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201


@main.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.is_completed = data.get('is_completed', task.is_completed)
    task.deadline = data.get('deadline', task.deadline)
    task.importance = data.get('importance', task.importance)

    db.session.commit()
    return jsonify(task.to_dict())