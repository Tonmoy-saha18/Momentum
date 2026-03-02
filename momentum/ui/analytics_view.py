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
        self.setMinimumHeight(200)
        self.setObjectName("weeklyChart")
        self._data: list[tuple[str, int]] = []
        self._max_val = 1

    def set_data(self, data: list[tuple[str, int]]) -> None:
        self._data = data
        self._max_val = max((v for _, v in data), default=1) or 1
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        pad = 40
        ch = h - pad * 2
        n = len(self._data)
        bar_w = min(40, (w - pad * 2) // (n * 2))
        spacing = ((w - pad * 2) - bar_w * n) // max(n, 1)

        accent = QColor("#7c3aed")
        text_c = QColor("#8b949e")

        for i, (label, value) in enumerate(self._data):
            x = pad + i * (bar_w + spacing)
            bar_h = int((value / self._max_val) * ch) if self._max_val else 0
            y = pad + ch - bar_h

            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 4, 4)

            painter.setPen(text_c)
            painter.drawText(x, h - 12, bar_w, 16, Qt.AlignmentFlag.AlignCenter, label)

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
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 32)
        root.setSpacing(24)

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
        self._stats_grid.setSpacing(16)
        root.addLayout(self._stats_grid)

        cl = QLabel("Weekly Learning Activity")
        cl.setObjectName("sectionTitle")
        root.addWidget(cl)

        self._chart = _WeeklyChart()
        root.addWidget(self._chart)
        root.addStretch()

    # ── Public ───────────────────────────────────────────────────────

    def update_stats(
        self,
        total_courses: int,
        total_hours: float,
        streak: int,
        completed_lessons: int,
        weekly_data: list[tuple[str, int]],
    ) -> None:
        while self._stats_grid.count():
            item = self._stats_grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        cards = [
            _StatCard("Total Courses", str(total_courses)),
            _StatCard("Learning Time", format_duration_hours(int(total_hours * 3600))),
            _StatCard("Daily Streak", f"{streak} days", "Keep it going!"),
            _StatCard("Lessons Done", str(completed_lessons)),
        ]
        for i, card in enumerate(cards):
            self._stats_grid.addWidget(card, 0, i)

        self._chart.set_data(weekly_data)
