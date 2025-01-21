from datetime import datetime, timedelta, timezone
import os
import openai
from sqlalchemy import false, true

from app.models import ArchivedTasks, Section, Task
from sqlalchemy import union_all, func

from app import db


openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

MAX_RETRIES = 4


def parse_datetime(datetime_str):
    """Parse ISO 8601 formatted datetime string to a datetime object."""
    try:
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(
            "Invalid datetime format. Use ISO 8601 format (e.g., 2024-12-29T15:30:00Z)."
        )


def load_prompt(filename):
    prompts_folder = os.path.join(os.path.dirname(__file__), "prompts")
    file_path = os.path.join(prompts_folder, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise Exception(f"Prompt file '{filename}' not found in {prompts_folder}.")


def get_current_tasks(user_id):
    """
    Fetch all incomplete tasks for the user.
    """
    return (
        db.session.query(
            Task.id,
            Task.title,
            Task.description,
            Task.deadline,
            Task.importance,
            Task.created_at,
            Task.updated_at,
            Section.name.label("section_name"),
        )
        .filter(Task.user_id == user_id, Task.is_completed == false())
        .outerjoin(Section, Task.section == Section.id)
        .order_by(Task.deadline.asc())
        .all()
    )


def get_recent_completed_tasks(user_id, limit=20):
    """
    Fetch the most recent completed tasks, combining current and archived tasks.
    """
    completed_tasks_query = union_all(
        db.session.query(
            Task.id.label("id"),
            Task.title.label("title"),
            Task.description.label("description"),
            Task.deadline.label("deadline"),
            Task.importance.label("importance"),
            Task.updated_at.label("completed_at"),
            Task.section.label("section"),
        ).filter(Task.user_id == user_id, Task.is_completed == true()),
        db.session.query(
            ArchivedTasks.id.label("id"),
            ArchivedTasks.title.label("title"),
            ArchivedTasks.description.label("description"),
            ArchivedTasks.deadline.label("deadline"),
            ArchivedTasks.importance.label("importance"),
            ArchivedTasks.archived_at.label("completed_at"),
            ArchivedTasks.section.label("section"),
        ).filter(ArchivedTasks.user_id == user_id),
    ).subquery()

    return (
        db.session.query(
            completed_tasks_query.c.id,
            completed_tasks_query.c.title,
            completed_tasks_query.c.description,
            completed_tasks_query.c.deadline,
            completed_tasks_query.c.importance,
            completed_tasks_query.c.completed_at,
            Section.name.label("section_name"),
        )
        .outerjoin(Section, completed_tasks_query.c.section == Section.id)
        .order_by(completed_tasks_query.c.completed_at.desc())
        .limit(limit)
        .all()
    )


def get_task_stats(user_id, days=30):
    """
    Fetch the number of tasks created and completed in the last N days (default: 30 days).
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    tasks_union = union_all(
        db.session.query(
            Task.created_at.label("created_at"),
            Task.is_completed.cast(db.Integer).label("is_completed"),
        ).filter(Task.user_id == user_id),
        db.session.query(
            ArchivedTasks.created_at.label("created_at"),
            db.literal(1).label("is_completed"),
        ).filter(ArchivedTasks.user_id == user_id),
    ).subquery()

    return (
        db.session.query(
            func.date(tasks_union.c.created_at).label("day"),
            func.count().label("created_count"),
            func.sum(tasks_union.c.is_completed).label("completed_count"),
        )
        .filter(tasks_union.c.created_at >= start_date)
        .group_by(func.date(tasks_union.c.created_at))
        .all()
    )


def generate_ai_summary(user_id, last_user_report=None):
    """
    Generate a productivity summary using OpenAI's API, based on the user's tasks, completed tasks,
    and historical stats.

    Parameters:
        user_id (str): The ID of the user requesting the report.
        last_user_report (ai_report object): The content of the last AI report (optional).

    Returns:
        json: The generated AI summary content.
    """
    tasks = get_current_tasks(user_id)
    completed_tasks = get_recent_completed_tasks(user_id, limit=20)
    task_stats = get_task_stats(user_id, days=30)

    prompt = "### Task Summary\n\n"
    prompt += "#### Current Tasks:\n"
    try:
        for task in tasks:
            title = task[1]  # Second element is 'title'
            description = task[2]  # Third element is 'description'
            deadline = task[3]  # Fourth element is 'deadline'
            importance = task[4]  # Fifth element is 'importance'
            section = task[7]  # Section name
            prompt += (
                f"- Title: {title}, Description: {description}, "
                f"Deadline: {deadline}, Importance: {importance}, Section: {section}\n"
            )

        prompt += "\n#### Last 30 Completed Tasks:\n"
        for task in completed_tasks:
            prompt += (
                f"- Title: {task.title}, Completed Date: {task.completed_at}, "
                f"Importance: {task.importance}, Deadline: {task.deadline}\n"
            )
        prompt += "\n#### Weekly Stats:\n"
        for stat in task_stats:
            prompt += (
                f"- {stat.day}: {stat.created_count} tasks created, "
                f"{stat.completed_count} tasks completed.\n"
            )

        if last_user_report:
            prompt += f"\n#### Last Report on date{last_user_report.generated_at}:\n{last_user_report.summary}\n"
    except Exception:
        raise

    system_prompt = """
    You are a productivity assistant designed to generate concise, engaging, and motivational summaries for users in **Catalan**.
    - Highlight recent accomplishments and trends, such as productivity improvements, task streaks, or records.
    - Avoid repeating feedback already provided in the last report.
    - Provide constructive feedback if the user has low productivity, but always frame it in a positive, encouraging way.
    - Conclude with a preview of the user's upcoming tasks, emphasizing urgency and importance.
    - End the summary with either a motivational quote or a fun fact related to the user's tasks, to leave the user inspired or entertained.
    - Preserve the structure and formatting of the output, with subtitles and bullet points where applicable.
    """

    user_prompt = f"""
    ### Dades de tasques de l'usuari:
    {prompt}
    Genera un resum de productivitat amb:
    - De 1 a 4 punts destacant assoliments recents, tendències o àrees de millora.
    - Una previsió de les tasques pendents basant-se en la seva importància i terminis.
    - Acaba el resum amb una cita motivadora o una curiositat que s'alineï amb les tasques recents de l'usuari.
    - El resum generat ha de ser atractiu, concís, motivador i no ha de superar les 10 línies.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content

    except Exception:
        raise
