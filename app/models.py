from enum import auto
from sqlalchemy import null
from . import db
from datetime import datetime, timezone


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_number = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    importance = db.Column(db.Integer, default=0, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    section = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, onupdate=lambda: datetime.now(timezone.utc), nullable=True
    )

    def to_dict(self):
        """Convert Task object to a dictionary."""
        task_disctionary = {
            "id": self.id,
            "task_number": self.task_number,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "importance": self.importance,
            "is_completed": self.is_completed,
            "section": self.section,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return {
            key: value for key, value in task_disctionary.items() if value is not null
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firebase_uid = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    tasks = db.relationship("Task", backref="user")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert User object to a dictionary."""
        user_dictionary = {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }
        return {
            key: value for key, value in user_dictionary.items() if value is not null
        }


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tasks = db.relationship("Task", backref="task_section")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert Section object to a dictionary."""
        section_dictionary = {
            "id": self.id,
            "name": self.name,
            "user": self.user,
            "created_at": self.created_at.isoformat(),
        }
        return {
            key: value for key, value in section_dictionary.items() if value is not null
        }


class ArchivedTasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_number = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    importance = db.Column(db.Integer, default=0, nullable=True)
    was_completed = db.Column(db.Boolean, nullable=False)
    section = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    archived_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        """Convert ArchivedTasks object to a dictionary."""
        archived_tasks_dictionary = {
            "id": self.id,
            "task_number": self.task_number,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "importance": self.importance,
            "was_completed": self.was_completed,
            "section": self.section,
            "created_at": self.created_at.isoformat(),
            "archived_at": self.archived_at.isoformat(),
        }
        return {
            key: value
            for key, value in archived_tasks_dictionary.items()
            if value is not null
        }


class AiSummaryExecutions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    summary = db.Column(db.JSON, nullable=False)
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert AiSummaryExecutions object to a dictionary."""
        ai_summary_executions_dictionary = {
            "id": self.id,
            "user_id": self.user_id,
            "summary": self.summary,
            "generated_at": self.generated_at.isoformat(),
        }
        return {
            key: value
            for key, value in ai_summary_executions_dictionary.items()
            if value is not null
        }
