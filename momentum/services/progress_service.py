"""Business logic for tracking lesson and course progress."""

from __future__ import annotations

from momentum.config import Config
from momentum.models.database import Database


class ProgressService:
    def __init__(self, db: Database):
        self.db = db
        self._last_lesson_id: int | None = None
        self._last_position_ms: int = 0
        self._pending_watch_ms: int = 0

    def update_position(self, lesson_id: int, position_ms: int, duration_ms: int) -> None:
        self.db.update_lesson_progress(lesson_id, position_ms, duration_ms)
        self._accumulate_watch_time(lesson_id, position_ms)

    def flush_watch_time(self) -> None:
        """Persist buffered watch time into daily_activity."""
        whole_seconds = self._pending_watch_ms // 1000
        if whole_seconds > 0:
            self.db.update_daily_activity(seconds=whole_seconds)
            self._pending_watch_ms %= 1000

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

    def _accumulate_watch_time(self, lesson_id: int, position_ms: int) -> None:
        # New lesson/file: reset pointer so we only measure forward playback deltas.
        if self._last_lesson_id != lesson_id:
            self.flush_watch_time()
            self._last_lesson_id = lesson_id
            self._last_position_ms = position_ms
            return

        delta_ms = position_ms - self._last_position_ms
        self._last_position_ms = position_ms

        # Count only natural forward playback; ignore rewinds and large jumps (seeks).
        if 0 < delta_ms <= 15_000:
            self._pending_watch_ms += delta_ms

        # Flush in small batches to keep stats responsive without excessive DB writes.
        if self._pending_watch_ms >= 5_000:
            self.flush_watch_time()
