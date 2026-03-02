"""Business logic for tracking lesson and course progress."""

from __future__ import annotations

from momentum.config import Config
from momentum.models.database import Database


class ProgressService:
    def __init__(self, db: Database):
        self.db = db

    def update_position(self, lesson_id: int, position_ms: int, duration_ms: int) -> None:
        self.db.update_lesson_progress(lesson_id, position_ms, duration_ms)

    def mark_completed(self, lesson_id: int) -> None:
        lesson = self.db.get_lesson(lesson_id)
        if lesson:
            self.db.mark_lesson_completed(lesson_id)
            self.db.update_course_progress(lesson.course_id)
            self.db.update_daily_activity(lessons_completed=1)

    def toggle_completion(self, lesson_id: int) -> bool:
        """Toggle and return the new completion state."""
        lesson = self.db.get_lesson(lesson_id)
        if not lesson:
            return False
        if lesson.is_completed:
            self.db.mark_lesson_incomplete(lesson_id)
        else:
            self.db.mark_lesson_completed(lesson_id)
            self.db.update_daily_activity(lessons_completed=1)
        self.db.update_course_progress(lesson.course_id)
        return not lesson.is_completed

    def check_auto_complete(
        self, lesson_id: int, position_ms: int, duration_ms: int
    ) -> bool:
        """Return True if the lesson was just auto-completed by reaching the threshold."""
        if duration_ms <= 0:
            return False
        if position_ms / duration_ms < Config.COMPLETION_THRESHOLD:
            return False
        lesson = self.db.get_lesson(lesson_id)
        if lesson and not lesson.is_completed:
            self.mark_completed(lesson_id)
            return True
        return False

    def get_resume_position(self, lesson_id: int) -> int:
        lesson = self.db.get_lesson(lesson_id)
        return lesson.watch_position_ms if lesson else 0
