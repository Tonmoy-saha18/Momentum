"""SQLite database manager — single repository for all persistence."""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from momentum.config import Config
from momentum.models.entities import (
    Course,
    DailyActivity,
    Lesson,
    Note,
)

logger = logging.getLogger(__name__)

SCHEMA = """\
CREATE TABLE IF NOT EXISTS courses (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT    NOT NULL,
    root_path         TEXT    NOT NULL UNIQUE,
    total_lessons     INTEGER DEFAULT 0,
    completed_lessons INTEGER DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sections (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id    INTEGER NOT NULL,
    name         TEXT    NOT NULL,
    order_index  INTEGER DEFAULT 0,
    folder_path  TEXT,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lessons (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id       INTEGER NOT NULL,
    course_id        INTEGER NOT NULL,
    title            TEXT    NOT NULL,
    file_path        TEXT    NOT NULL UNIQUE,
    duration_ms      INTEGER DEFAULT 0,
    order_index      INTEGER DEFAULT 0,
    is_completed     INTEGER DEFAULT 0,
    watch_position_ms INTEGER DEFAULT 0,
    last_watched     TIMESTAMP,
    completed_at     TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES courses(id)  ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id         INTEGER NOT NULL,
    content           TEXT    NOT NULL,
    video_timestamp_ms INTEGER DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id        INTEGER,
    start_time       TIMESTAMP NOT NULL,
    end_time         TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    session_type     TEXT DEFAULT 'free',
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS daily_activity (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    date              TEXT    NOT NULL UNIQUE,
    total_seconds     INTEGER DEFAULT 0,
    lessons_completed INTEGER DEFAULT 0
);
"""


class Database:
    """Central repository wrapping all SQLite operations."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.DB_PATH
        Config.ensure_dirs()
        self._init_db()

    # ── connection helper ────────────────────────────────────────────

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        with self._connection() as conn:
            conn.executescript(SCHEMA)
        logger.info("Database ready at %s", self.db_path)

    # ── Course CRUD ──────────────────────────────────────────────────

    def insert_course(self, course: Course) -> int:
        with self._connection() as conn:
            cur = conn.execute(
                "INSERT INTO courses (name, root_path, total_lessons) VALUES (?, ?, ?)",
                (course.name, course.root_path, course.total_lessons),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def get_course(self, course_id: int) -> Optional[Course]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
        return self._row_to_course(row) if row else None

    def get_all_courses(self) -> list[Course]:
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM courses ORDER BY updated_at DESC").fetchall()
        return [self._row_to_course(r) for r in rows]

    def get_course_by_path(self, root_path: str) -> Optional[Course]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM courses WHERE root_path = ?", (root_path,)).fetchone()
        return self._row_to_course(row) if row else None

    def update_course_progress(self, course_id: int) -> None:
        with self._connection() as conn:
            conn.execute(
                """UPDATE courses SET
                       completed_lessons = (SELECT COUNT(*) FROM lessons WHERE course_id = ? AND is_completed = 1),
                       total_lessons     = (SELECT COUNT(*) FROM lessons WHERE course_id = ?),
                       updated_at        = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (course_id, course_id, course_id),
            )

    def delete_course(self, course_id: int) -> None:
        with self._connection() as conn:
            conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))

    # ── Section CRUD ─────────────────────────────────────────────────

    def insert_section(self, course_id: int, name: str, order_index: int, folder_path: str) -> int:
        with self._connection() as conn:
            cur = conn.execute(
                "INSERT INTO sections (course_id, name, order_index, folder_path) VALUES (?, ?, ?, ?)",
                (course_id, name, order_index, folder_path),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def get_sections(self, course_id: int):
        """Return list of sqlite3.Row objects for sections."""
        with self._connection() as conn:
            return conn.execute(
                "SELECT * FROM sections WHERE course_id = ? ORDER BY order_index", (course_id,)
            ).fetchall()

    # ── Lesson CRUD ──────────────────────────────────────────────────

    def insert_lesson(self, lesson: Lesson) -> int:
        with self._connection() as conn:
            cur = conn.execute(
                """INSERT INTO lessons
                       (section_id, course_id, title, file_path, duration_ms, order_index)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    lesson.section_id,
                    lesson.course_id,
                    lesson.title,
                    lesson.file_path,
                    lesson.duration_ms,
                    lesson.order_index,
                ),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def get_lesson(self, lesson_id: int) -> Optional[Lesson]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
        return self._row_to_lesson(row) if row else None

    def get_lessons_by_section(self, section_id: int) -> list[Lesson]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM lessons WHERE section_id = ? ORDER BY order_index", (section_id,)
            ).fetchall()
        return [self._row_to_lesson(r) for r in rows]

    def get_all_lessons(self, course_id: int) -> list[Lesson]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM lessons WHERE course_id = ? ORDER BY section_id, order_index",
                (course_id,),
            ).fetchall()
        return [self._row_to_lesson(r) for r in rows]

    def update_lesson_progress(self, lesson_id: int, position_ms: int, duration_ms: int = 0) -> None:
        with self._connection() as conn:
            if duration_ms > 0:
                conn.execute(
                    """UPDATE lessons
                       SET watch_position_ms = ?, duration_ms = ?, last_watched = CURRENT_TIMESTAMP
                       WHERE id = ?""",
                    (position_ms, duration_ms, lesson_id),
                )
            else:
                conn.execute(
                    "UPDATE lessons SET watch_position_ms = ?, last_watched = CURRENT_TIMESTAMP WHERE id = ?",
                    (position_ms, lesson_id),
                )

    def mark_lesson_completed(self, lesson_id: int) -> None:
        with self._connection() as conn:
            conn.execute(
                "UPDATE lessons SET is_completed = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (lesson_id,),
            )

    def mark_lesson_incomplete(self, lesson_id: int) -> None:
        with self._connection() as conn:
            conn.execute(
                "UPDATE lessons SET is_completed = 0, completed_at = NULL WHERE id = ?",
                (lesson_id,),
            )

    def get_next_incomplete_lesson(self, course_id: int, current_lesson_id: int = 0) -> Optional[Lesson]:
        with self._connection() as conn:
            row = conn.execute(
                """SELECT l.* FROM lessons l
                   JOIN sections s ON l.section_id = s.id
                   WHERE l.course_id = ? AND l.is_completed = 0 AND l.id > ?
                   ORDER BY s.order_index, l.order_index LIMIT 1""",
                (course_id, current_lesson_id),
            ).fetchone()
            if row is None:
                row = conn.execute(
                    """SELECT l.* FROM lessons l
                       JOIN sections s ON l.section_id = s.id
                       WHERE l.course_id = ? AND l.is_completed = 0
                       ORDER BY s.order_index, l.order_index LIMIT 1""",
                    (course_id,),
                ).fetchone()
        return self._row_to_lesson(row) if row else None

    def get_previous_lesson(self, course_id: int, current_lesson_id: int) -> Optional[Lesson]:
        """Return the lesson immediately preceding the current one in course order."""
        if current_lesson_id <= 0:
            return None

        with self._connection() as conn:
            cur = conn.execute(
                """SELECT s.order_index AS sec_order, l.order_index AS lesson_order
                   FROM lessons l
                   JOIN sections s ON l.section_id = s.id
                   WHERE l.course_id = ? AND l.id = ?
                   LIMIT 1""",
                (course_id, current_lesson_id),
            ).fetchone()
            if cur is None:
                return None

            row = conn.execute(
                """SELECT l.* FROM lessons l
                   JOIN sections s ON l.section_id = s.id
                   WHERE l.course_id = ?
                     AND (
                       s.order_index < ?
                       OR (s.order_index = ? AND l.order_index < ?)
                     )
                   ORDER BY s.order_index DESC, l.order_index DESC
                   LIMIT 1""",
                (course_id, cur["sec_order"], cur["sec_order"], cur["lesson_order"]),
            ).fetchone()
        return self._row_to_lesson(row) if row else None

    # ── Notes CRUD ───────────────────────────────────────────────────

    def insert_note(self, note: Note) -> int:
        with self._connection() as conn:
            cur = conn.execute(
                "INSERT INTO notes (lesson_id, content, video_timestamp_ms) VALUES (?, ?, ?)",
                (note.lesson_id, note.content, note.video_timestamp_ms),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def get_notes(self, lesson_id: int) -> list[Note]:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM notes WHERE lesson_id = ? ORDER BY video_timestamp_ms", (lesson_id,)
            ).fetchall()
        return [self._row_to_note(r) for r in rows]

    def update_note(self, note_id: int, content: str) -> None:
        with self._connection() as conn:
            conn.execute(
                "UPDATE notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (content, note_id),
            )

    def delete_note(self, note_id: int) -> None:
        with self._connection() as conn:
            conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    # ── Study Sessions ───────────────────────────────────────────────

    def start_study_session(self, course_id: Optional[int], session_type: str = "free") -> int:
        with self._connection() as conn:
            cur = conn.execute(
                "INSERT INTO study_sessions (course_id, start_time, session_type) VALUES (?, CURRENT_TIMESTAMP, ?)",
                (course_id, session_type),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def end_study_session(self, session_id: int) -> None:
        with self._connection() as conn:
            conn.execute(
                """UPDATE study_sessions SET
                       end_time = CURRENT_TIMESTAMP,
                       duration_seconds = CAST(
                           (julianday(CURRENT_TIMESTAMP) - julianday(start_time)) * 86400 AS INTEGER
                       )
                   WHERE id = ?""",
                (session_id,),
            )

    # ── Daily Activity ───────────────────────────────────────────────

    def update_daily_activity(self, seconds: int = 0, lessons_completed: int = 0) -> None:
        today = date.today().isoformat()
        with self._connection() as conn:
            conn.execute(
                """INSERT INTO daily_activity (date, total_seconds, lessons_completed)
                   VALUES (?, ?, ?)
                   ON CONFLICT(date) DO UPDATE SET
                       total_seconds     = daily_activity.total_seconds + excluded.total_seconds,
                       lessons_completed = daily_activity.lessons_completed + excluded.lessons_completed""",
                (today, seconds, lessons_completed),
            )

    def get_daily_activity(self, days: int = 30) -> list[DailyActivity]:
        since = (date.today() - timedelta(days=days)).isoformat()
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM daily_activity WHERE date >= ? ORDER BY date", (since,)
            ).fetchall()
        return [self._row_to_daily_activity(r) for r in rows]

    def get_streak(self) -> int:
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT date FROM daily_activity WHERE total_seconds > 0 ORDER BY date DESC"
            ).fetchall()
        if not rows:
            return 0
        streak = 0
        expected = date.today()
        for row in rows:
            activity_date = date.fromisoformat(row["date"])
            if activity_date == expected:
                streak += 1
                expected -= timedelta(days=1)
            elif activity_date < expected:
                break
        return streak

    def get_total_watch_time_seconds(self) -> int:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(total_seconds), 0) AS total FROM daily_activity"
            ).fetchone()
        return row["total"] if row else 0

    def get_weekly_watch_time_seconds(self) -> int:
        activities = self.get_daily_activity(days=7)
        return sum(a.total_seconds for a in activities)

    def get_streak_time_seconds(self) -> int:
        """Return total watch seconds accumulated in the current streak window."""
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT date, total_seconds FROM daily_activity WHERE total_seconds > 0 ORDER BY date DESC"
            ).fetchall()
        if not rows:
            return 0

        total_seconds = 0
        expected = date.today()
        for row in rows:
            activity_date = date.fromisoformat(row["date"])
            if activity_date == expected:
                total_seconds += row["total_seconds"]
                expected -= timedelta(days=1)
            elif activity_date < expected:
                break
        return total_seconds

    # ── Row → Entity converters ──────────────────────────────────────

    @staticmethod
    def _row_to_course(row: sqlite3.Row) -> Course:
        return Course(
            id=row["id"],
            name=row["name"],
            root_path=row["root_path"],
            total_lessons=row["total_lessons"],
            completed_lessons=row["completed_lessons"],
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )

    @staticmethod
    def _row_to_lesson(row: sqlite3.Row) -> Lesson:
        return Lesson(
            id=row["id"],
            section_id=row["section_id"],
            course_id=row["course_id"],
            title=row["title"],
            file_path=row["file_path"],
            duration_ms=row["duration_ms"],
            order_index=row["order_index"],
            is_completed=bool(row["is_completed"]),
            watch_position_ms=row["watch_position_ms"],
            last_watched=row["last_watched"],
            completed_at=row["completed_at"],
        )

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> Note:
        return Note(
            id=row["id"],
            lesson_id=row["lesson_id"],
            content=row["content"],
            video_timestamp_ms=row["video_timestamp_ms"],
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )

    @staticmethod
    def _row_to_daily_activity(row: sqlite3.Row) -> DailyActivity:
        return DailyActivity(
            id=row["id"],
            date=row["date"],
            total_seconds=row["total_seconds"],
            lessons_completed=row["lessons_completed"],
        )
