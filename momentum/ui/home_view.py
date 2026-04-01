"""Home / course-library view with hero, course cards, and momentum panel."""

from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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
        self._card_height = 170
        self.setFixedHeight(self._card_height)
        self.setMinimumWidth(240)
        self.setMaximumWidth(360)
        self._apply_shadow()
        self._build()

    def _apply_shadow(self) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.setGraphicsEffect(shadow)

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        icon = QLabel("◈")
        icon.setObjectName("courseCardIcon")
        top.addWidget(icon)
        top.addStretch()
        badge = QLabel("IN PROGRESS" if self.course.progress_percent > 0 else "OFFLINE READY")
        badge.setObjectName("courseCardBadge")
        top.addWidget(badge)
        lay.addLayout(top)

        name = QLabel(self.course.name)
        name.setObjectName("cardTitle")
        name.setWordWrap(True)
        name.setMaximumHeight(44)
        lay.addWidget(name)

        subtitle = QLabel("Continue where you left off")
        subtitle.setObjectName("cardSubtitle")
        lay.addWidget(subtitle)

        lay.addStretch()

        stats = QLabel(
            f"{self.course.completed_lessons}/{self.course.total_lessons} LESSONS COMPLETED"
        )
        stats.setObjectName("cardStats")
        lay.addWidget(stats)

        bar = QProgressBar()
        bar.setObjectName("cardProgress")
        bar.setRange(0, 100)
        bar.setValue(int(self.course.progress_percent))
        bar.setTextVisible(False)
        bar.setFixedHeight(5)
        lay.addWidget(bar)

        pct = QLabel(f"{self.course.progress_percent:.0f}%")
        pct.setObjectName("cardPercent")
        lay.addWidget(pct, alignment=Qt.AlignmentFlag.AlignRight)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.course.id)  # type: ignore[arg-type]
        super().mousePressEvent(event)


class AddCourseCard(QFrame):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("addCourseCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._card_height = 170
        self.setFixedHeight(self._card_height)
        self.setMinimumWidth(240)
        self.setMaximumWidth(360)
        self._apply_shadow()
        self._build()

    def _apply_shadow(self) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 7)
        shadow.setColor(QColor(0, 0, 0, 95))
        self.setGraphicsEffect(shadow)

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)
        lay.addStretch()

        plus = QLabel("+")
        plus.setObjectName("addCourseCardPlus")
        plus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(plus)

        title = QLabel("Add New Course")
        title.setObjectName("addCourseCardTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("Import from Udemy, Coursera, or local files")
        sub.setObjectName("addCourseCardSubtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addStretch()

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


# ── Home View ────────────────────────────────────────────────────────

class HomeView(QWidget):
    course_selected = Signal(int)
    folder_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("homeView")
        self._momentum_bars: list[QFrame] = []
        self._momentum_day_chips: list[QLabel] = []
        self._daily_minutes: list[int] = [0] * 7
        self._kpi_values: dict[str, QLabel] = {}
        self._courses: list[Course] = []
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        page_scroll = QScrollArea()
        page_scroll.setObjectName("homePageScroll")
        page_scroll.setWidgetResizable(True)
        page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        page_scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(page_scroll)

        content = QWidget()
        page_scroll.setWidget(content)

        root = QVBoxLayout(content)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(16)

        # Hero banner
        hero = QFrame()
        hero.setObjectName("homeHero")
        hero.setMinimumHeight(154)
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(24, 18, 24, 18)
        hl.setSpacing(8)

        kick = QLabel("FOCUS MODE ACTIVE")
        kick.setObjectName("heroKicker")
        hl.addWidget(kick)

        title = QLabel("Welcome back,\nLearner!")
        title.setObjectName("heroTitle")
        hl.addWidget(title)

        stats = QHBoxLayout()
        stats.setSpacing(16)
        stat1 = QVBoxLayout()
        s1 = QLabel("MOMENTUM STREAK")
        s1.setObjectName("heroStatLabel")
        stat1.addWidget(s1)
        self.lbl_streak = QLabel("0 days")
        self.lbl_streak.setObjectName("heroStatValue")
        stat1.addWidget(self.lbl_streak)
        stats.addLayout(stat1)

        divider = QFrame()
        divider.setObjectName("heroDivider")
        divider.setFixedWidth(1)
        stats.addWidget(divider)

        stat2 = QVBoxLayout()
        s2 = QLabel("WEEKLY PROGRESS")
        s2.setObjectName("heroStatLabel")
        stat2.addWidget(s2)
        self.lbl_week = QLabel("0%")
        self.lbl_week.setObjectName("heroStatValue")
        stat2.addWidget(self.lbl_week)
        stats.addLayout(stat2)
        stats.addStretch()
        hl.addLayout(stats)
        root.addWidget(hero)

        # Section heading
        sec = QHBoxLayout()
        left = QVBoxLayout()
        t = QLabel("Active Courses")
        t.setObjectName("homeSectionTitle")
        left.addWidget(t)
        sub = QLabel("Continue where you left off")
        sub.setObjectName("homeSectionSubtitle")
        left.addWidget(sub)
        sec.addLayout(left)
        sec.addStretch()
        view = QLabel("VIEW LIBRARY")
        view.setObjectName("homeLibraryAction")
        sec.addWidget(view, alignment=Qt.AlignmentFlag.AlignBottom)
        root.addLayout(sec)

        # Course grid (outer page handles vertical scrolling)
        self._cards_widget = QWidget()
        self._cards_widget.setObjectName("courseGrid")
        self._cards_layout = QGridLayout(self._cards_widget)
        self._cards_layout.setHorizontalSpacing(14)
        self._cards_layout.setVerticalSpacing(14)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self._cards_widget)

        # Momentum analytics section
        mt = QLabel("Your Momentum")
        mt.setObjectName("homeSectionTitle")
        root.addWidget(mt)

        momentum = QFrame()
        momentum.setObjectName("momentumCard")
        ml = QVBoxLayout(momentum)
        ml.setContentsMargins(16, 12, 16, 12)
        ml.setSpacing(12)

        # KPI strip
        kpis = QHBoxLayout()
        kpis.setSpacing(10)
        for key, title in [
            ("streak", "CURRENT STREAK"),
            ("week_minutes", "THIS WEEK"),
            ("hours", "TOTAL WATCH TIME"),
            ("lessons", "LESSONS DONE"),
        ]:
            card = QFrame()
            card.setObjectName("momentumKpiCard")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(10, 8, 10, 8)
            cl.setSpacing(2)
            lbl_title = QLabel(title)
            lbl_title.setObjectName("momentumKpiTitle")
            cl.addWidget(lbl_title)
            lbl_value = QLabel("0")
            lbl_value.setObjectName("momentumKpiValue")
            cl.addWidget(lbl_value)
            self._kpi_values[key] = lbl_value
            kpis.addWidget(card)
        ml.addLayout(kpis)

        days = QHBoxLayout()
        days.setSpacing(6)
        for label in ["M", "T", "W", "T", "F", "S", "S"]:
            c = QLabel(label)
            c.setObjectName("momentumDayChip")
            days.addWidget(c)
            self._momentum_day_chips.append(c)
        days.addStretch()
        self.lbl_momentum_date = QLabel("")
        self.lbl_momentum_date.setObjectName("momentumDate")
        days.addWidget(self.lbl_momentum_date)
        ml.addLayout(days)

        bars = QHBoxLayout()
        bars.setSpacing(8)
        for _ in range(7):
            b = QFrame()
            b.setObjectName("momentumBar")
            b.setFixedHeight(10)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            bars.addWidget(b)
            self._momentum_bars.append(b)
        ml.addLayout(bars)
        self.lbl_momentum_empty = QLabel("No recent activity yet. Start a lesson to build momentum.")
        self.lbl_momentum_empty.setObjectName("homeSectionSubtitle")
        self.lbl_momentum_empty.hide()
        ml.addWidget(self.lbl_momentum_empty)
        root.addWidget(momentum)

    # ── Public ───────────────────────────────────────────────────────

    def display_courses(self, courses: list[Course]) -> None:
        self._courses = list(courses)
        self._rebuild_cards()

    def _rebuild_cards(self) -> None:
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        cols = self._columns_for_width()
        card_w = self._card_width_for_columns(cols)
        i = 0
        for course in self._courses:
            card = CourseCard(course)
            card.setFixedWidth(card_w)
            card.clicked.connect(self.course_selected.emit)
            self._cards_layout.addWidget(card, i // cols, i % cols)
            i += 1

        add = AddCourseCard()
        add.setFixedWidth(card_w)
        add.clicked.connect(self._pick_folder)
        self._cards_layout.addWidget(add, i // cols, i % cols)

    def _columns_for_width(self) -> int:
        margins = 44  # root left + right
        spacing = self._cards_layout.horizontalSpacing()
        available = max(1, self.width() - margins)
        min_card = 260
        cols = (available + spacing) // (min_card + spacing)
        return max(1, min(3, cols))

    def _card_width_for_columns(self, cols: int) -> int:
        margins = 44  # root left + right
        spacing = self._cards_layout.horizontalSpacing() * (cols - 1)
        available = max(240, self.width() - margins - spacing)
        return max(240, min(320, available // cols))

    def update_home_stats(
        self,
        streak_days: int,
        weekly_minutes: list[int],
        total_courses: int = 0,
        total_hours: float = 0.0,
        completed_lessons: int = 0,
    ) -> None:
        minutes = weekly_minutes[-7:] if weekly_minutes else [0] * 7
        if len(minutes) < 7:
            minutes = [0] * (7 - len(minutes)) + minutes
        self._daily_minutes = minutes

        self.lbl_streak.setText(f"{streak_days} day{'s' if streak_days != 1 else ''}")

        total_week = sum(minutes)
        # Progress against a realistic weekly target of 7h (60m/day).
        weekly_pct = int(min(100, round((total_week / 420.0) * 100)))
        trend = "↗" if len(minutes) > 1 and minutes[-1] >= minutes[-2] else ""
        self.lbl_week.setText(f"{weekly_pct}% {trend}".strip())

        # Momentum KPI values (all real values from DB analytics).
        self._kpi_values["streak"].setText(f"{streak_days} day{'s' if streak_days != 1 else ''}")
        self._kpi_values["week_minutes"].setText(f"{total_week} min")
        self._kpi_values["hours"].setText(f"{total_hours:.1f} h")
        self._kpi_values["lessons"].setText(f"{completed_lessons} / {max(1, total_courses)} courses")

        today = date.today()
        start = today - timedelta(days=6)
        self.lbl_momentum_date.setText(f"{start.strftime('%b %d').upper()} - {today.strftime('%b %d').upper()}")

        max_minutes = max(minutes) if minutes else 0
        active_idx = max(range(len(minutes)), key=lambda i: minutes[i]) if max_minutes > 0 else -1

        for i, bar in enumerate(self._momentum_bars):
            if max_minutes == 0:
                h = 10
            else:
                # Normalize to visible range while still reflecting relative effort.
                h = 10 + int((minutes[i] / max_minutes) * 32)
            bar.setFixedHeight(max(10, h))
            bar.setObjectName("momentumBarActive" if i == active_idx and minutes[i] > 0 else "momentumBar")
            bar.setToolTip(f"{minutes[i]} minute(s)")
            bar.style().unpolish(bar)
            bar.style().polish(bar)

        day_labels = ["M", "T", "W", "T", "F", "S", "S"]
        for i, chip in enumerate(self._momentum_day_chips):
            chip.setText(day_labels[i])
            chip.setObjectName("momentumDayChipActive" if i == active_idx and minutes[i] > 0 else "momentumDayChip")
            chip.style().unpolish(chip)
            chip.style().polish(chip)

        has_activity = total_week > 0
        self.lbl_momentum_empty.setVisible(not has_activity)

    # ── Slots ────────────────────────────────────────────────────────

    def _pick_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Course Folder")
        if folder:
            self.folder_selected.emit(folder)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        # Reflow cards for smaller laptop screens.
        self._rebuild_cards()
