"""Home / course-library view with hero, course cards, and momentum panel."""

from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
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


class _MomentumChart(QWidget):
    """7-day bar strip with per-day color glows (home momentum)."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("momentumChart")
        self.setMinimumHeight(140)
        self._minutes: list[int] = [0] * 7

    def set_minutes(self, minutes: list[int]) -> None:
        m = minutes[-7:] if minutes else [0] * 7
        if len(m) < 7:
            m = [0] * (7 - len(m)) + m
        self._minutes = m
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        pad_x = 14
        pad_top = 10
        pad_bottom = 32
        inner_w = max(1, w - pad_x * 2)
        inner_h = max(1, h - pad_top - pad_bottom)

        n = 7
        gap = max(10, inner_w // 36)
        bar_w = max(20, (inner_w - gap * (n - 1)) // n)
        total_w = bar_w * n + gap * (n - 1)
        start_x = pad_x + max(0, (inner_w - total_w) // 2)

        max_m = max(self._minutes) if self._minutes else 0

        grid = QColor("#1a263c")
        axis = QColor("#2b3956")
        text = QColor("#8b97b4")

        palette = [
            QColor("#5f7dff"),  # Mon - blue
            QColor("#22c55e"),  # Tue - green
            QColor("#a78bfa"),  # Wed - violet
            QColor("#38bdf8"),  # Thu - cyan
            QColor("#f59e0b"),  # Fri - amber
            QColor("#fb7185"),  # Sat - rose
            QColor("#34d399"),  # Sun - mint
        ]

        # Baseline + mid grid line
        base_y = pad_top + inner_h
        painter.setPen(axis)
        painter.drawLine(pad_x, base_y, w - pad_x, base_y)
        painter.setPen(QColor(grid.red(), grid.green(), grid.blue(), 160))
        painter.drawLine(pad_x, pad_top + inner_h // 2, w - pad_x, pad_top + inner_h // 2)

        # Empty state
        if max_m <= 0:
            painter.setPen(text)
            painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, "No activity yet")
            painter.end()
            return

        for i in range(n):
            x = start_x + i * (bar_w + gap)
            minutes = self._minutes[i] if i < len(self._minutes) else 0

            # Proper bar height with small minimum so non-zero shows.
            bar_h = int((minutes / max_m) * inner_h) if minutes > 0 else 0
            # Ensure label can always sit centered inside.
            bar_h = max(22, bar_h) if minutes > 0 else 2
            bar_h = min(inner_h, bar_h)
            y = base_y - bar_h

            base = palette[i % len(palette)]

            # Per-day glow behind the bar
            if minutes > 0:
                glow = QColor(base)
                glow.setAlpha(70)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow)
                painter.drawRoundedRect(x - 3, y - 3, bar_w + 6, bar_h + 6, 10, 10)

            # Bar fill
            fill = QColor(base if minutes > 0 else QColor("#222d43"))
            fill.setAlpha(210 if minutes > 0 else 200)
            painter.setBrush(fill)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 8, 8)

            # Time label centered inside bar (always, when minutes > 0)
            if minutes > 0:
                label = self._format_minutes(minutes)
                f = painter.font()
                f.setPointSize(9 if bar_h >= 26 and bar_w >= 44 else 8)
                f.setBold(True)
                painter.setFont(f)
                painter.setPen(QColor("#0a101b"))
                painter.drawText(x, y, bar_w, bar_h, Qt.AlignmentFlag.AlignCenter, label)

            # Day label below axis
            painter.setPen(text)
            day = ["M", "T", "W", "T", "F", "S", "S"][i]
            painter.drawText(x, h - 20, bar_w, 16, Qt.AlignmentFlag.AlignCenter, day)

        painter.end()

    @staticmethod
    def _format_minutes(minutes: int) -> str:
        if minutes < 60:
            return f"{minutes}m"
        h = minutes // 60
        m = minutes % 60
        if m == 0:
            return f"{h}h"
        return f"{h}h{m:02d}"


# ── Home View ────────────────────────────────────────────────────────

class HomeView(QWidget):
    course_selected = Signal(int)
    folder_selected = Signal(str)
    analytics_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("homeView")
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

        # Momentum analytics section header (with tabs)
        mh = QHBoxLayout()
        mh.setContentsMargins(0, 0, 0, 0)
        mt = QLabel("Your Momentum")
        mt.setObjectName("homeSectionTitle")
        mh.addWidget(mt)
        mh.addStretch()

        tabs = QWidget()
        tabs.setObjectName("homeMomentumTabs")
        tl = QHBoxLayout(tabs)
        tl.setContentsMargins(6, 6, 6, 6)
        tl.setSpacing(6)

        self.btn_momentum_tab = QPushButton("Momentum")
        self.btn_momentum_tab.setObjectName("homeMomentumTabActive")
        self.btn_momentum_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_momentum_tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tl.addWidget(self.btn_momentum_tab)

        self.btn_analytics_tab = QPushButton("Analytics")
        self.btn_analytics_tab.setObjectName("homeMomentumTab")
        self.btn_analytics_tab.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_analytics_tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_analytics_tab.clicked.connect(self.analytics_requested.emit)
        tl.addWidget(self.btn_analytics_tab)

        mh.addWidget(tabs, alignment=Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(mh)

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

        self._momentum_chart = _MomentumChart()
        ml.addWidget(self._momentum_chart)
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

        self._momentum_chart.set_minutes(minutes)

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
