"""Course dashboard — sidebar + video player + notes / pomodoro tabs."""

from __future__ import annotations

import random

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from momentum.config import Config
from momentum.models.database import Database
from momentum.services.notes_service import NotesService
from momentum.services.progress_service import ProgressService
from momentum.ui.notes_panel import NotesPanel
from momentum.ui.pomodoro import PomodoroTimer
from momentum.ui.sidebar import CourseSidebar
from momentum.ui.video_player import VideoPlayer
from momentum.utils.constants import MOTIVATIONAL_MESSAGES


class DashboardView(QWidget):
    """Composite view shown when the user opens a course."""

    back_requested = Signal()

    def __init__(self, db: Database, parent: QWidget | None = None):
        super().__init__(parent)
        self.db = db
        self.progress_svc = ProgressService(db)
        self.notes_svc = NotesService(db)
        self._course_id: int | None = None
        self._lesson_id: int | None = None
        self._build_ui()
        self._wire()

    # ── Layout ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Sidebar
        self.sidebar = CourseSidebar()
        self.sidebar.setFixedWidth(Config.SIDEBAR_WIDTH)
        outer.addWidget(self.sidebar)

        # Main content
        main = QWidget()
        ml = QVBoxLayout(main)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setObjectName("dashToolbar")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(16, 8, 16, 8)

        self.btn_back = QPushButton("← Courses")
        self.btn_back.setObjectName("backButton")
        tl.addWidget(self.btn_back)
        tl.addStretch()

        self.btn_complete = QPushButton("✓  Mark Complete")
        self.btn_complete.setObjectName("completeButton")
        tl.addWidget(self.btn_complete)

        self.btn_next = QPushButton("Next Lesson →")
        self.btn_next.setObjectName("nextButton")
        tl.addWidget(self.btn_next)

        ml.addWidget(toolbar)

        # Video player
        self.player = VideoPlayer()
        ml.addWidget(self.player, stretch=3)

        # Bottom tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("bottomTabs")

        self.notes = NotesPanel()
        self.pomodoro = PomodoroTimer()
        self.tabs.addTab(self.notes, "📝  Notes")
        self.tabs.addTab(self.pomodoro, "🍅  Pomodoro")

        ml.addWidget(self.tabs, stretch=1)
        outer.addWidget(main, stretch=1)

    def _wire(self) -> None:
        self.sidebar.lesson_selected.connect(self._on_lesson_selected)
        self.btn_back.clicked.connect(self._on_back)
        self.btn_complete.clicked.connect(self._on_toggle_complete)
        self.btn_next.clicked.connect(self._on_next)
        self.player.position_changed.connect(self._on_position)
        self.player.video_completed.connect(self._on_video_completed)
        self.notes.note_saved.connect(self._on_note_saved)
        self.notes.note_deleted.connect(self._on_note_deleted)
        self.notes.timestamp_clicked.connect(lambda ms: self.player.seek_relative(ms - self.player.get_position()))

    # ── Public ───────────────────────────────────────────────────────

    def load_course(self, course_id: int) -> None:
        self._course_id = course_id
        course = self.db.get_course(course_id)
        if not course:
            return

        sections = self.db.get_sections(course_id)
        lessons_by_sec: dict[int, list] = {}
        for sec in sections:
            lessons_by_sec[sec["id"]] = self.db.get_lessons_by_section(sec["id"])

        self.sidebar.load_course(course, sections, lessons_by_sec)

        nxt = self.db.get_next_incomplete_lesson(course_id)
        if nxt:
            self._on_lesson_selected(nxt.id)  # type: ignore[arg-type]

    # ── Slots ────────────────────────────────────────────────────────

    def _on_lesson_selected(self, lesson_id: int) -> None:
        self._lesson_id = lesson_id
        lesson = self.db.get_lesson(lesson_id)
        if not lesson:
            return
        pos = self.progress_svc.get_resume_position(lesson_id)
        self.player.load_video(lesson.file_path, pos)
        self.sidebar.highlight_lesson(lesson_id)
        self.notes.set_lesson(lesson_id)
        self.notes.display_notes(self.notes_svc.get_notes(lesson_id))

    def _on_position(self, pos_ms: int, dur_ms: int) -> None:
        if self._lesson_id:
            self.progress_svc.update_position(self._lesson_id, pos_ms, dur_ms)

    def _on_video_completed(self) -> None:
        if not self._lesson_id:
            return
        completed = self.progress_svc.check_auto_complete(
            self._lesson_id, self.player.get_position(), self.player.get_duration()
        )
        if completed:
            self.sidebar.mark_lesson_completed(self._lesson_id)
            self._refresh_progress()
            self._toast(random.choice(MOTIVATIONAL_MESSAGES))

    def _on_toggle_complete(self) -> None:
        if not self._lesson_id:
            return
        now_complete = self.progress_svc.toggle_completion(self._lesson_id)
        if now_complete:
            self.sidebar.mark_lesson_completed(self._lesson_id)
        self._refresh_progress()

    def _on_next(self) -> None:
        if self._course_id:
            nxt = self.db.get_next_incomplete_lesson(self._course_id, self._lesson_id or 0)
            if nxt:
                self._on_lesson_selected(nxt.id)  # type: ignore[arg-type]

    def _on_note_saved(self, content: str, _ts: int) -> None:
        if not self._lesson_id:
            return
        actual_ts = self.player.get_position()
        self.notes_svc.add_note(self._lesson_id, content, actual_ts)
        self.notes.display_notes(self.notes_svc.get_notes(self._lesson_id))

    def _on_note_deleted(self, note_id: int) -> None:
        self.notes_svc.delete_note(note_id)
        if self._lesson_id:
            self.notes.display_notes(self.notes_svc.get_notes(self._lesson_id))

    def _on_back(self) -> None:
        self.player.stop()
        self.back_requested.emit()

    # ── Helpers ──────────────────────────────────────────────────────

    def _refresh_progress(self) -> None:
        if self._course_id:
            course = self.db.get_course(self._course_id)
            if course:
                self.sidebar.update_progress(course)

    def _toast(self, message: str) -> None:
        win = self.window()
        if hasattr(win, "statusBar"):
            win.statusBar().showMessage(message, 5000)
