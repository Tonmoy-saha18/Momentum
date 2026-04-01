"""Application-wide configuration constants."""

import sys
from pathlib import Path


class Config:
    APP_NAME = "Momentum"
    VERSION = "1.0.0"

    # Paths
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent
    _RUNTIME_ROOT = Path(getattr(sys, "_MEIPASS", _PROJECT_ROOT))
    APP_DIR = Path.home() / ".momentum"
    DB_PATH = APP_DIR / "momentum.db"
    ICON_PATH = _RUNTIME_ROOT / "resources" / "icons" / "momentum.png"

    # Video
    VIDEO_EXTENSIONS = frozenset({
        ".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v",
    })
    COMPLETION_THRESHOLD = 0.90

    # Pomodoro defaults (seconds)
    POMODORO_WORK_MINUTES = 25
    POMODORO_BREAK_MINUTES = 5
    POMODORO_LONG_BREAK_MINUTES = 15
    POMODORO_SESSIONS_BEFORE_LONG_BREAK = 4

    # UI
    SIDEBAR_WIDTH = 300
    MIN_WINDOW_WIDTH = 1200
    MIN_WINDOW_HEIGHT = 750

    @classmethod
    def ensure_dirs(cls) -> None:
        cls.APP_DIR.mkdir(parents=True, exist_ok=True)
