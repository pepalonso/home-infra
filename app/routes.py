from ast import main
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from sqlalchemy import null

from app.firebase_auth import verify_token
from app.utils import parse_datetime
from .models import  Task
from . import db

main = Blueprint('main', __name__)
CORS(main) 

@main.route('/tasks', methods=['GET'])
def get_tasks():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing token'}), 401
    firebase_token = auth_header.split(' ')[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks])


@main.route('/task', methods=['POST'])
def add_task():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing token'}), 401
    firebase_token = auth_header.split(' ')[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    data = request.json

    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    if not data.get('task_number'):
        return jsonify({'error': 'Task number is required'}), 400
    
    if data.get('deadline'):
        try:
            data['deadline'] = parse_datetime(data['deadline'])
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    new_task = Task(
        user_id=user_id,
        title=data['title'],
        task_number=data['task_number'],
        description=data.get('description', None),
        deadline=data.get('deadline', None),
        importance=data.get('importance', None),
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201


@main.route('/update/<int:task_number>', methods=['PUT'])
def update_task(task_number):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing token'}), 401
    firebase_token = auth_header.split(' ')[1]
    user_id = verify_token(firebase_token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    data = request.json

    if data.get('deadline'):
        try:
            data['deadline'] = parse_datetime(data['deadline'])
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
    task = Task.query.filter_by(task_number=task_number).filter_by(user_id=user_id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.is_completed = data.get('is_completed', task.is_completed)
    task.deadline = data.get('deadline', task.deadline)
    task.importance = data.get('importance', task.importance)

    db.session.commit()
    return jsonify(task.to_dict())