"""Home / course-library view — grid of course cards + add-course button."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from momentum.models.entities import Course


# ── Course Card ──────────────────────────────────────────────────────

class CourseCard(QFrame):
    clicked = Signal(int)

    def __init__(self, course: Course, parent: QWidget | None = None):
        super().__init__(parent)
        self.course = course
        self.setObjectName("courseCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(280, 180)
        self._build()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 16)
        lay.setSpacing(8)

        name = QLabel(self.course.name)
        name.setObjectName("cardTitle")
        name.setWordWrap(True)
        name.setMaximumHeight(50)
        lay.addWidget(name)

        lay.addStretch()

        stats = QLabel(
            f"{self.course.completed_lessons}/{self.course.total_lessons} lessons completed"
        )
        stats.setObjectName("cardStats")
        lay.addWidget(stats)

        bar = QProgressBar()
        bar.setObjectName("cardProgress")
        bar.setRange(0, 100)
        bar.setValue(int(self.course.progress_percent))
        bar.setTextVisible(False)
        bar.setFixedHeight(4)
        lay.addWidget(bar)

        pct = QLabel(f"{self.course.progress_percent:.0f}% complete")
        pct.setObjectName("cardPercent")
        lay.addWidget(pct)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.course.id)  # type: ignore[arg-type]
        super().mousePressEvent(event)


# ── Home View ────────────────────────────────────────────────────────

class HomeView(QWidget):
    course_selected = Signal(int)
    folder_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("homeView")
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 32)
        root.setSpacing(24)

        # Header row
        header = QHBoxLayout()
        titles = QVBoxLayout()
        t = QLabel("Momentum")
        t.setObjectName("appTitle")
        titles.addWidget(t)
        sub = QLabel("Your offline learning companion")
        sub.setObjectName("appSubtitle")
        titles.addWidget(sub)
        header.addLayout(titles)
        header.addStretch()

        self.btn_add = QPushButton("＋  Add Course")
        self.btn_add.setObjectName("addCourseButton")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self._pick_folder)
        header.addWidget(self.btn_add, alignment=Qt.AlignmentFlag.AlignBottom)
        root.addLayout(header)

        # Scrollable card grid
        scroll = QScrollArea()
        scroll.setObjectName("courseScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._cards_widget = QWidget()
        self._cards_layout = QGridLayout(self._cards_widget)
        self._cards_layout.setSpacing(20)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self._cards_widget)
        self._scroll = scroll
        root.addWidget(scroll, stretch=1)

        # Empty-state overlay
        self._empty = QWidget(self)
        el = QVBoxLayout(self._empty)
        el.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel("📚")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(icon)
        msg = QLabel("No courses yet.\nClick '＋ Add Course' to load a course folder.")
        msg.setObjectName("emptyStateText")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        el.addWidget(msg)
        root.addWidget(self._empty, stretch=1)

    # ── Public ───────────────────────────────────────────────────────

    def display_courses(self, courses: list[Course]) -> None:
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not courses:
            self._empty.show()
            self._scroll.hide()
            return

        self._empty.hide()
        self._scroll.show()
        cols = 3
        for i, course in enumerate(courses):
            card = CourseCard(course)
            card.clicked.connect(self.course_selected.emit)
            self._cards_layout.addWidget(card, i // cols, i % cols)

    # ── Slots ────────────────────────────────────────────────────────

    def _pick_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Course Folder")
        if folder:
            self.folder_selected.emit(folder)
