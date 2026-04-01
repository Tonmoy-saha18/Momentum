"""Analytics dashboard with stat cards and a weekly activity chart."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from momentum.utils.helpers import format_duration_hours


# ── Stat Card ────────────────────────────────────────────────────────

class _StatCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setFixedHeight(120)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(4)

        lt = QLabel(title)
        lt.setObjectName("statTitle")
        lay.addWidget(lt)

        lv = QLabel(value)
        lv.setObjectName("statValue")
        lay.addWidget(lv)

        if subtitle:
            ls = QLabel(subtitle)
            ls.setObjectName("statSubtitle")
            lay.addWidget(ls)
        lay.addStretch()


# ── Weekly Bar Chart ─────────────────────────────────────────────────

class _WeeklyChart(QWidget):
    """Minimal bar chart rendered with QPainter."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setObjectName("weeklyChart")
        self._data: list[tuple[str, int]] = []
        self._max_val = 1

    def set_data(self, data: list[tuple[str, int]]) -> None:
        self._data = data
        self._max_val = max((v for _, v in data), default=1) or 1
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        pad_x = 28
        pad_top = 22
        pad_bottom = 36
        ch = max(1, h - pad_top - pad_bottom)
        n = len(self._data) if self._data else 7
        bar_w = min(42, max(18, (w - pad_x * 2) // (n * 2)))
        spacing = max(10, ((w - pad_x * 2) - bar_w * n) // max(n, 1))

        accent = QColor("#5f7dff")
        muted = QColor("#222d43")
        text_c = QColor("#8b97b4")
        grid = QColor("#1a263c")

        max_val = max((v for _, v in self._data), default=0)
        all_zero = (not self._data) or max_val <= 0

        # Baseline + subtle grid
        painter.setPen(grid)
        base_y = pad_top + ch
        painter.drawLine(pad_x, base_y, w - pad_x, base_y)
        painter.setPen(QColor(26, 38, 60, 160))
        painter.drawLine(pad_x, pad_top + ch // 2, w - pad_x, pad_top + ch // 2)

        if all_zero:
            painter.setPen(text_c)
            painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, "No activity yet")
            # Still draw day labels if we have them.
            if not self._data:
                painter.end()
                return

        for i, (label, value) in enumerate(self._data):
            x = pad_x + i * (bar_w + spacing)
            bar_h = int((value / self._max_val) * ch) if self._max_val else 0
            y = pad_top + ch - bar_h

            painter.setBrush(accent if value == max_val and max_val > 0 else muted)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 4, 4)

            painter.setPen(text_c)
            painter.drawText(x, h - 18, bar_w, 16, Qt.AlignmentFlag.AlignCenter, label)

            if value:
                painter.drawText(
                    x, y - 18, bar_w, 16, Qt.AlignmentFlag.AlignCenter, f"{value}m"
                )
        painter.end()


# ── Analytics View ───────────────────────────────────────────────────

class AnalyticsView(QWidget):
    back_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("analyticsView")
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("analyticsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        root = QVBoxLayout(content)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(16)

        hdr = QHBoxLayout()
        btn = QPushButton("← Back")
        btn.setObjectName("backButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.back_requested.emit)
        hdr.addWidget(btn)

        title = QLabel("Analytics")
        title.setObjectName("pageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)

        self._stats_grid = QGridLayout()
        self._stats_grid.setHorizontalSpacing(12)
        self._stats_grid.setVerticalSpacing(12)
        root.addLayout(self._stats_grid)

        cl = QLabel("Weekly Learning Activity")
        cl.setObjectName("sectionTitle")
        root.addWidget(cl)

        self._chart = _WeeklyChart()
        root.addWidget(self._chart)

        root.addStretch(1)

        self._cards: list[_StatCard] = []

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._layout_cards()

    def _layout_cards(self) -> None:
        if not getattr(self, "_cards", None):
            return
        while self._stats_grid.count():
            item = self._stats_grid.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)

        cols = 2 if self.width() < 1150 else 4
        for i, card in enumerate(self._cards):
            self._stats_grid.addWidget(card, i // cols, i % cols)

    # ── Public ───────────────────────────────────────────────────────

    def update_stats(
        self,
        total_courses: int,
        total_hours: float,
        streak: int,
        completed_lessons: int,
        weekly_data: list[tuple[str, int]],
    ) -> None:
        for c in getattr(self, "_cards", []):
            c.deleteLater()
        self._cards = [
            _StatCard("Total Courses", str(total_courses)),
            _StatCard("Learning Time", format_duration_hours(int(total_hours * 3600))),
            _StatCard("Daily Streak", f"{streak} days", "Keep it going!"),
            _StatCard("Lessons Done", str(completed_lessons)),
        ]
        self._layout_cards()

        self._chart.set_data(weekly_data)
