"""Domain entities represented as plain data classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Course:
    name: str
    root_path: str
    id: Optional[int] = None
    total_lessons: int = 0
    completed_lessons: int = 0
    created_at: str = ""
    updated_at: str = ""

    @property
    def progress_percent(self) -> float:
        if self.total_lessons == 0:
            return 0.0
        return (self.completed_lessons / self.total_lessons) * 100.0


@dataclass
class Section:
    course_id: int
    name: str
    id: Optional[int] = None
    order_index: int = 0
    folder_path: str = ""
    lessons: list[Lesson] = field(default_factory=list)


@dataclass
class Lesson:
    section_id: int
    course_id: int
    title: str
    file_path: str
    id: Optional[int] = None
    duration_ms: int = 0
    order_index: int = 0
    is_completed: bool = False
    watch_position_ms: int = 0
    last_watched: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Note:
    lesson_id: int
    content: str
    id: Optional[int] = None
    video_timestamp_ms: int = 0
    created_at: str = ""
    updated_at: str = ""


@dataclass
class StudySession:
    start_time: str
    id: Optional[int] = None
    course_id: Optional[int] = None
    end_time: Optional[str] = None
    duration_seconds: int = 0
    session_type: str = "free"


@dataclass
class DailyActivity:
    date: str
    id: Optional[int] = None
    total_seconds: int = 0
    lessons_completed: int = 0
