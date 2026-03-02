"""Shared enumerations and constant values."""

from enum import Enum


class PlaybackState(Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class SessionType(Enum):
    FREE = "free"
    POMODORO = "pomodoro"


class ViewIndex(Enum):
    HOME = 0
    DASHBOARD = 1
    ANALYTICS = 2


MOTIVATIONAL_MESSAGES = [
    "Great job! Keep up the momentum! 🚀",
    "You're making amazing progress! 💪",
    "One step closer to mastery! 🎯",
    "Consistency is key, and you're nailing it! ⭐",
    "Knowledge is power — keep learning! 📚",
    "You're on fire today! 🔥",
    "Small steps lead to big results! 🏆",
]
