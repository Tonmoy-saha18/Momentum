"""Collapsible course sidebar showing sections and lessons (Udemy-style)."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from momentum.models.entities import Course, Lesson


class CourseSidebar(QWidget):
    """Left-hand navigation tree for the active course."""

    lesson_selected = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._lesson_items: dict[int, QTreeWidgetItem] = {}
        self._setup_ui()

    # ── UI construction ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("sidebarHeader")
        hdr = QVBoxLayout(header)
        hdr.setContentsMargins(16, 16, 16, 12)

        self.lbl_course = QLabel("No Course Loaded")
        self.lbl_course.setObjectName("courseNameLabel")
        self.lbl_course.setWordWrap(True)
        hdr.addWidget(self.lbl_course)

        row = QHBoxLayout()
        self.lbl_progress = QLabel("0 / 0 lessons")
        self.lbl_progress.setObjectName("progressLabel")
        row.addWidget(self.lbl_progress)
        self.lbl_percent = QLabel("0%")
        self.lbl_percent.setObjectName("percentLabel")
        row.addWidget(self.lbl_percent, alignment=Qt.AlignmentFlag.AlignRight)
        hdr.addLayout(row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("courseProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        hdr.addWidget(self.progress_bar)

        root.addWidget(header)

        # Tree
        self.tree = QTreeWidget()
        self.tree.setObjectName("lessonTree")
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setAnimated(True)
        self.tree.setRootIsDecorated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        root.addWidget(self.tree)

    # ── Public API ───────────────────────────────────────────────────

    def load_course(
        self,
        course: Course,
        sections: list,
        lessons_by_section: dict[int, list[Lesson]],
    ) -> None:
        self._lesson_items.clear()
        self.tree.clear()
        self.lbl_course.setText(course.name)
        self._update_progress(course)

        for section in sections:
            sec_item = QTreeWidgetItem(self.tree)
            sec_item.setText(0, f"  📁  {section['name']}")
            sec_item.setData(0, Qt.ItemDataRole.UserRole, ("section", section["id"]))
            sec_item.setExpanded(True)
            font = sec_item.font(0)
            font.setBold(True)
            sec_item.setFont(0, font)

            for lesson in lessons_by_section.get(section["id"], []):
                li = QTreeWidgetItem(sec_item)
                self._set_lesson_text(li, lesson)
                li.setData(0, Qt.ItemDataRole.UserRole, ("lesson", lesson.id))
                self._lesson_items[lesson.id] = li

    def mark_lesson_completed(self, lesson_id: int) -> None:
        item = self._lesson_items.get(lesson_id)
        if item:
            text = item.text(0)
            item.setText(0, text.replace("○", "✅").replace("▶", "✅"))

    def highlight_lesson(self, lesson_id: int) -> None:
        item = self._lesson_items.get(lesson_id)
        if item:
            self.tree.setCurrentItem(item)

    def update_progress(self, course: Course) -> None:
        self._update_progress(course)

    # ── Internals ────────────────────────────────────────────────────

    @staticmethod
    def _set_lesson_text(item: QTreeWidgetItem, lesson: Lesson) -> None:
        icon = "✅" if lesson.is_completed else "○"
        item.setText(0, f"    {icon}  {lesson.title}")

    def _update_progress(self, course: Course) -> None:
        self.lbl_progress.setText(f"{course.completed_lessons} / {course.total_lessons} lessons")
        pct = course.progress_percent
        self.lbl_percent.setText(f"{pct:.0f}%")
        self.progress_bar.setValue(int(pct))

    def _on_item_clicked(self, item: QTreeWidgetItem, _col: int) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == "lesson":
            self.lesson_selected.emit(data[1])
