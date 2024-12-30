from datetime import datetime

def parse_datetime(datetime_str):
    """Parse ISO 8601 formatted datetime string to a datetime object."""
    try:
        return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Invalid datetime format. Use ISO 8601 format (e.g., 2024-12-29T15:30:00Z).")
