"""Course dashboard — sidebar + video player + bottom panels + focus mode."""

from __future__ import annotations

import random

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
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


class _FocusSwitch(QPushButton):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(44, 24)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setObjectName("focusSwitch")

    def paintEvent(self, _event) -> None:  # noqa: N802
        w, h = self.width(), self.height()
        r = h // 2
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)

        track = QColor("#7c3aed") if self.isChecked() else QColor("#21262d")
        painter.setBrush(track)
        painter.drawRoundedRect(0, 0, w, h, r, r)

        knob_d = h - 4
        knob_x = w - knob_d - 2 if self.isChecked() else 2
        painter.setBrush(QColor("#f8fafc"))
        painter.drawEllipse(knob_x, 2, knob_d, knob_d)


class DashboardView(QWidget):
    """Composite view shown when the user opens a course.

    Normal mode:  [sidebar 280px] [center: topbar + video + bottom_cards]
    Focus mode:   [icon_rail 52px] [center: topbar + video] [right_panel 320px]
    """

    back_requested = Signal()

    def __init__(self, db: Database, parent: QWidget | None = None):
        super().__init__(parent)
        self.db = db
        self.progress_svc = ProgressService(db)
        self.notes_svc = NotesService(db)
        self._course_id: int | None = None
        self._lesson_id: int | None = None
        self._focus = False
        self._build_ui()
        self._wire()

    # ── Layout ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── 1. Icon rail (focus mode only) ───────────────────────────
        self.icon_rail = QWidget()
        self.icon_rail.setObjectName("iconRail")
        self.icon_rail.setFixedWidth(52)
        rl = QVBoxLayout(self.icon_rail)
        rl.setContentsMargins(0, 12, 0, 12)
        rl.setSpacing(6)
        rl.setAlignment(Qt.AlignmentFlag.AlignTop)

        for label, tip in [("📄", "Courses"), ("📝", "Notes"), ("🍅", "Pomodoro"), ("⚙", "Settings")]:
            b = QPushButton(label)
            b.setObjectName("railIcon")
            b.setFixedSize(42, 42)
            b.setToolTip(tip)
            rl.addWidget(b, alignment=Qt.AlignmentFlag.AlignHCenter)
        rl.addStretch()

        outer.addWidget(self.icon_rail)
        self.icon_rail.hide()

        # ── 2. Course sidebar (normal mode) ──────────────────────────
        self.sidebar = CourseSidebar()
        self.sidebar.setFixedWidth(Config.SIDEBAR_WIDTH)
        outer.addWidget(self.sidebar)

        # ── 3. Center column ─────────────────────────────────────────
        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        # Top bar
        self._build_top_bar(cl)

        # Video player — dominates the vertical space
        self.player = VideoPlayer()
        self.player.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        cl.addWidget(self.player, stretch=1)

        # Bottom area (tabs row + two cards) — fixed strip (mock-aligned)
        self.bottom = QWidget()
        self.bottom.setObjectName("bottomPanels")
        # Normal mode should prioritize the video area.
        self.bottom.setFixedHeight(185)
        bottom_layout = QVBoxLayout(self.bottom)
        bottom_layout.setContentsMargins(12, 4, 12, 8)
        bottom_layout.setSpacing(6)

        tabs = QWidget()
        tabs.setObjectName("bottomTabs")
        tr = QHBoxLayout(tabs)
        tr.setContentsMargins(0, 0, 0, 0)
        tr.setSpacing(18)
        self.tab_notes = QPushButton("Notes")
        self.tab_notes.setObjectName("bottomTabActive")
        self.tab_notes.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tab_notes.setCursor(Qt.CursorShape.PointingHandCursor)
        tr.addWidget(self.tab_notes)

        self.tab_pomo = QPushButton("Pomodoro")
        self.tab_pomo.setObjectName("bottomTab")
        self.tab_pomo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tab_pomo.setCursor(Qt.CursorShape.PointingHandCursor)
        tr.addWidget(self.tab_pomo)
        tr.addStretch()
        bottom_layout.addWidget(tabs)

        self.notes = NotesPanel()
        self.pomodoro = PomodoroTimer()

        self.notes_card = QFrame()
        self.notes_card.setObjectName("panelCard")
        self._ncl = QVBoxLayout(self.notes_card)
        self._ncl.setContentsMargins(0, 0, 0, 0)
        self._ncl.addWidget(self.notes)

        self.pomo_card = QFrame()
        self.pomo_card.setObjectName("panelCard")
        self._pcl = QVBoxLayout(self.pomo_card)
        self._pcl.setContentsMargins(0, 0, 0, 0)
        self._pcl.addWidget(self.pomodoro)

        self.bottom_stack = QStackedWidget()
        self.bottom_stack.setObjectName("bottomStack")
        self.bottom_stack.addWidget(self.notes_card)
        self.bottom_stack.addWidget(self.pomo_card)
        self.bottom_stack.setCurrentIndex(0)
        bottom_layout.addWidget(self.bottom_stack, stretch=1)
        cl.addWidget(self.bottom)

        outer.addWidget(center, stretch=1)

        # ── 4. Focus right panel (focus mode only) ───────────────────
        self.focus_panel = QWidget()
        self.focus_panel.setObjectName("focusPanel")
        self.focus_panel.setFixedWidth(320)
        fpl = QVBoxLayout(self.focus_panel)
        fpl.setContentsMargins(12, 12, 12, 12)
        fpl.setSpacing(12)

        self.fp_pomo_card = QFrame()
        self.fp_pomo_card.setObjectName("panelCard")
        self._fpcl = QVBoxLayout(self.fp_pomo_card)
        self._fpcl.setContentsMargins(0, 0, 0, 0)

        self.fp_notes_card = QFrame()
        self.fp_notes_card.setObjectName("panelCard")
        self._fncl = QVBoxLayout(self.fp_notes_card)
        self._fncl.setContentsMargins(0, 0, 0, 0)

        fpl.addWidget(self.fp_pomo_card, stretch=2)
        fpl.addWidget(self.fp_notes_card, stretch=3)

        outer.addWidget(self.focus_panel)
        self.focus_panel.hide()

    def _build_top_bar(self, parent_layout: QVBoxLayout) -> None:
        bar = QWidget()
        bar.setObjectName("dashTopBar")
        tl = QHBoxLayout(bar)
        tl.setContentsMargins(18, 8, 18, 8)
        tl.setSpacing(12)

        self.btn_back = QPushButton("Courses  >  …")
        self.btn_back.setObjectName("breadcrumbButton")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        tl.addWidget(self.btn_back)

        self.lbl_breadcrumb = QLabel("")
        self.lbl_breadcrumb.setObjectName("breadcrumbLabel")
        self.lbl_breadcrumb.hide()
        tl.addWidget(self.lbl_breadcrumb)

        tl.addStretch()

        self.lbl_focus = QLabel("Focus Mode")
        self.lbl_focus.setObjectName("focusModeLabel")
        tl.addWidget(self.lbl_focus)

        self.chk_focus = _FocusSwitch()
        tl.addWidget(self.chk_focus)

        self.lbl_streak = QLabel("Streak: 0 Days")
        self.lbl_streak.setObjectName("streakChip")
        tl.addWidget(self.lbl_streak)

        self.btn_complete = QPushButton("✓  Mark Complete")
        self.btn_complete.setObjectName("completeButton")
        tl.addWidget(self.btn_complete)

        self.btn_next = QPushButton("Next Lesson →")
        self.btn_next.setObjectName("nextButton")
        tl.addWidget(self.btn_next)

        parent_layout.addWidget(bar)

    # ── Wiring ───────────────────────────────────────────────────────

    def _wire(self) -> None:
        self.sidebar.lesson_selected.connect(self._on_lesson_selected)
        self.sidebar.collapse_requested.connect(lambda: self.chk_focus.setChecked(True))
        self.btn_back.clicked.connect(self._on_back)
        self.btn_complete.clicked.connect(self._on_toggle_complete)
        self.btn_next.clicked.connect(self._on_next)
        self.player.position_changed.connect(self._on_position)
        self.player.video_completed.connect(self._on_video_completed)
        self.notes.note_saved.connect(self._on_note_saved)
        self.notes.note_deleted.connect(self._on_note_deleted)
        self.notes.timestamp_clicked.connect(
            lambda ms: self.player.seek_relative(ms - self.player.get_position())
        )
        self.chk_focus.toggled.connect(self._set_focus_mode)
        self.tab_notes.clicked.connect(lambda: self._set_bottom_tab(0))
        self.tab_pomo.clicked.connect(lambda: self._set_bottom_tab(1))

    def _set_bottom_tab(self, idx: int) -> None:
        self.bottom_stack.setCurrentIndex(idx)
        if idx == 0:
            self.tab_notes.setObjectName("bottomTabActive")
            self.tab_pomo.setObjectName("bottomTab")
        else:
            self.tab_notes.setObjectName("bottomTab")
            self.tab_pomo.setObjectName("bottomTabActive")
        # Force stylesheet refresh for renamed objectName
        self.tab_notes.style().unpolish(self.tab_notes)
        self.tab_notes.style().polish(self.tab_notes)
        self.tab_pomo.style().unpolish(self.tab_pomo)
        self.tab_pomo.style().polish(self.tab_pomo)

    # ── Focus mode toggle ────────────────────────────────────────────

    def _set_focus_mode(self, enabled: bool) -> None:
        self._focus = enabled
        if enabled:
            self.sidebar.hide()
            self.icon_rail.show()
            self.bottom.hide()
            self.pomodoro.set_compact(True)
            self.player.set_focus_ui(True)
            self._fpcl.addWidget(self.pomodoro)
            self._fncl.addWidget(self.notes)
            self.focus_panel.show()
        else:
            self.icon_rail.hide()
            self.focus_panel.hide()
            self.pomodoro.set_compact(False)
            self.player.set_focus_ui(False)
            self._ncl.addWidget(self.notes)
            self._pcl.addWidget(self.pomodoro)
            self.bottom.show()
            self.sidebar.show()

    # ── Public ───────────────────────────────────────────────────────

    def load_course(self, course_id: int) -> None:
        self._course_id = course_id
        course = self.db.get_course(course_id)
        if not course:
            return
        self.btn_back.setText(f"Courses  >  {course.name}")
        self.player.set_title(course.name)
        try:
            streak = self.db.get_streak()
            self.lbl_streak.setText(f"Streak: {streak} Days 🔥" if streak else "Streak: 0 Days")
        except Exception:
            self.lbl_streak.setText("Streak: 0 Days")

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
        if self._focus:
            self.chk_focus.setChecked(False)
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
