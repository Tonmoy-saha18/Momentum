"""Utility helpers used across the application."""

import re


def format_duration(ms: int) -> str:
    """Format milliseconds into HH:MM:SS or MM:SS."""
    total_seconds = max(0, ms) // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def format_duration_hours(total_seconds: int) -> str:
    """Format total seconds into a human-friendly hours/minutes string."""
    total_seconds = max(0, total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def natural_sort_key(text: str):
    """Key function for natural-order sorting (e.g. '2. Intro' before '10. Advanced')."""
    return [int(tok) if tok.isdigit() else tok.lower() for tok in re.split(r"(\d+)", text)]


def sanitize_title(filename: str) -> str:
    """Derive a clean, human-readable title from a file or folder name."""
    name = filename.rsplit(".", 1)[0] if "." in filename else filename
    name = re.sub(r"^[\d.\-_\s]+", "", name)
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r"\s+", " ", name).strip()
    return name if name else filename
