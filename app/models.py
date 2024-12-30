from sqlalchemy import null
from . import db
from datetime import datetime, timezone

class User(db.Model):
    id =  db.Column(db.String(255), primary_key=True)
    firebase_uid = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_number = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(255), nullable=False) # this will be a foreign key to the User table
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    importance = db.Column(db.Integer, default=0, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    def to_dict(self):
        """Convert Task object to a dictionary."""
        task_disctionary = {
            'id': self.id,
            'task_number': self.task_number,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'importance': self.importance,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        return {key: value for key, value in task_disctionary.items() if value is not null}