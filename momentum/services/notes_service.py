"""CRUD operations for per-lesson notes."""

from __future__ import annotations

from momentum.models.database import Database
from momentum.models.entities import Note


class NotesService:
    def __init__(self, db: Database):
        self.db = db

    def add_note(self, lesson_id: int, content: str, timestamp_ms: int = 0) -> int:
        return self.db.insert_note(
            Note(lesson_id=lesson_id, content=content, video_timestamp_ms=timestamp_ms)
        )

    def get_notes(self, lesson_id: int) -> list[Note]:
        return self.db.get_notes(lesson_id)

    def update_note(self, note_id: int, content: str) -> None:
        self.db.update_note(note_id, content)

    def delete_note(self, note_id: int) -> None:
        self.db.delete_note(note_id)
