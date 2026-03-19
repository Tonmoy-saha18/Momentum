"""Collapsible course sidebar showing sections and lessons (Udemy-style)."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from momentum.models.entities import Course, Lesson


class CourseSidebar(QWidget):
    """Left-hand navigation tree for the active course."""

    lesson_selected = Signal(int)
    collapse_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._lesson_items: dict[int, QTreeWidgetItem] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Minimal top strip with collapse control (matches mock)
        header = QWidget()
        header.setObjectName("sidebarHeader")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 10, 12, 10)
        hl.setSpacing(8)

        self.lbl_course = QLabel("")
        self.lbl_course.setObjectName("courseNameLabel")
        self.lbl_course.hide()
        hl.addWidget(self.lbl_course)

        hl.addStretch()

        self.btn_collapse = QPushButton("«")
        self.btn_collapse.setObjectName("collapseButton")
        self.btn_collapse.setFixedSize(28, 28)
        self.btn_collapse.setToolTip("Focus mode")
        self.btn_collapse.clicked.connect(self.collapse_requested.emit)
        hl.addWidget(self.btn_collapse, alignment=Qt.AlignmentFlag.AlignTop)

        root.addWidget(header)

        # Tree
        self.tree = QTreeWidget()
        self.tree.setObjectName("lessonTree")
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setAnimated(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
        _ = course  # progress display intentionally hidden (mock matches tree-only sidebar)

    @staticmethod
    def _set_lesson_text(item: QTreeWidgetItem, lesson: Lesson) -> None:
        icon = "✅" if lesson.is_completed else "○"
        item.setText(0, f"    {icon}  {lesson.title}")

    def _update_progress(self, course: Course) -> None:
        _ = course

    def _on_item_clicked(self, item: QTreeWidgetItem, _col: int) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == "lesson":
            self.lesson_selected.emit(data[1])
