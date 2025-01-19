from datetime import datetime
import os


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
