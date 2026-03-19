"""Built-in Pomodoro focus timer widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
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


class _PomodoroRing(QWidget):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("pomodoroRing")
        self._remaining = 0
        self._total = 1

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to start/pause")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_icon = QLabel("🍎")
        self.lbl_icon.setObjectName("pomodoroRingIcon")
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_icon)

        self.lbl_time = QLabel("00:00")
        self.lbl_time.setObjectName("pomodoroRingTime")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_time)

        layout.addSpacing(6)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_time(self, remaining_seconds: int, total_seconds: int) -> None:
        self._remaining = max(0, remaining_seconds)
        self._total = max(1, total_seconds)
        m, s = divmod(self._remaining, 60)
        self.lbl_time.setText(f"{m:02d}:{s:02d}")
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        side = min(self.width(), self.height())
        if side <= 10:
            return

        # Reserve some space for labels; ring sits behind them.
        ring_side = int(side * 0.78)
        x = (self.width() - ring_side) // 2
        y = int((self.height() - ring_side) * 0.35)

        rect = (x, y, ring_side, ring_side)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Track
        track = QPen(QColor("#2a2f3a"))
        track.setWidth(10)
        track.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(*rect, 0, 16 * 360)

        # Progress (elapsed)
        elapsed = max(0, self._total - self._remaining)
        progress = 0.0 if self._total <= 0 else min(1.0, elapsed / self._total)

        prog = QPen(QColor("#8b5cf6"))
        prog.setWidth(10)
        prog.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(prog)
        painter.drawArc(*rect, 90 * 16, int(-360 * 16 * progress))


class PomodoroTimer(QWidget):
    """Pomodoro timer with work / short-break / long-break cycles."""

    session_completed = Signal(int)   # duration_seconds of the work session
    timer_tick = Signal(int)          # remaining_seconds

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("pomodoroPanel")

        self._work = Config.POMODORO_WORK_MINUTES * 60
        self._short_break = Config.POMODORO_BREAK_MINUTES * 60
        self._long_break = Config.POMODORO_LONG_BREAK_MINUTES * 60
        self._long_every = Config.POMODORO_SESSIONS_BEFORE_LONG_BREAK

        self._remaining = self._work
        self._is_running = False
        self._is_break = False
        self._session_count = 0

        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self._tick)

        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setObjectName("pomodoroStack")
        root.addWidget(self._stack)

        # ── Full card (normal mode) ────────────────────────────────
        full = QWidget()
        full.setObjectName("pomodoroFull")
        fl = QVBoxLayout(full)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(10)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        lbl_title = QLabel("Pomodoro Timer")
        lbl_title.setObjectName("panelTitle")
        title_row.addWidget(lbl_title)
        title_row.addStretch()
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setObjectName("pomodoroSettings")
        self.btn_settings.setFixedSize(30, 30)
        self.btn_settings.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        title_row.addWidget(self.btn_settings)
        fl.addLayout(title_row)

        self.lbl_time = QLabel(self._fmt(self._remaining))
        self.lbl_time.setObjectName("pomodoroBigTime")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(self.lbl_time)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_start = QPushButton("Start")
        self.btn_start.setObjectName("pomodoroPrimary")
        self.btn_start.clicked.connect(self.toggle)
        btns.addWidget(self.btn_start)

        self.btn_short = QPushButton("Short Break")
        self.btn_short.setObjectName("pomodoroSecondary")
        self.btn_short.clicked.connect(lambda: self.start_break(short=True))
        btns.addWidget(self.btn_short)

        self.btn_long = QPushButton("Long Break")
        self.btn_long.setObjectName("pomodoroSecondary")
        self.btn_long.clicked.connect(lambda: self.start_break(short=False))
        btns.addWidget(self.btn_long)

        fl.addLayout(btns)
        fl.addStretch()

        self._stack.addWidget(full)

        # ── Ring card (focus mode) ────────────────────────────────
        ring_wrap = QWidget()
        ring_wrap.setObjectName("pomodoroRingWrap")
        rl = QVBoxLayout(ring_wrap)
        rl.setContentsMargins(8, 8, 8, 8)
        rl.setSpacing(0)
        rl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ring = _PomodoroRing()
        self.ring.clicked.connect(self.toggle)
        rl.addWidget(self.ring, stretch=1)
        self._stack.addWidget(ring_wrap)

        self._sync_views()

    def set_compact(self, compact: bool) -> None:
        """Focus mode uses compact ring view."""
        self._stack.setCurrentIndex(1 if compact else 0)
        self._sync_views()

    # ── Public ───────────────────────────────────────────────────────

    def toggle(self) -> None:
        if self._is_running:
            self._clock.stop()
            self._is_running = False
            self.btn_start.setText("Resume")
        else:
            self._clock.start()
            self._is_running = True
            self.btn_start.setText("Pause")

    def reset(self) -> None:
        self._clock.stop()
        self._is_running = False
        self._is_break = False
        self._remaining = self._work
        self._sync_views()
        self.btn_start.setText("Start")

    def start_break(self, short: bool = True) -> None:
        self._clock.stop()
        self._is_running = False
        self._is_break = True
        self._remaining = self._short_break if short else self._long_break
        self.btn_start.setText("Start")
        self._sync_views()

    def start_focus(self) -> None:
        self._clock.stop()
        self._is_running = False
        self._is_break = False
        self._remaining = self._work
        self.btn_start.setText("Start")
        self._sync_views()

    # ── Internal ─────────────────────────────────────────────────────

    def _tick(self) -> None:
        self._remaining -= 1
        self._sync_views()
        self.timer_tick.emit(self._remaining)

        if self._remaining <= 0:
            self._clock.stop()
            self._is_running = False
            if not self._is_break:
                self._session_count += 1
                self.session_completed.emit(self._work)
                self._is_break = True
                if self._session_count % self._long_every == 0:
                    self._remaining = self._long_break
                else:
                    self._remaining = self._short_break
            else:
                self._is_break = False
                self._remaining = self._work
            self._sync_views()
            self.btn_start.setText("Start")

    def _sync_views(self) -> None:
        total = self._work
        if self._is_break:
            total = self._long_break if (self._session_count % self._long_every == 0) else self._short_break

        self.lbl_time.setText(self._fmt(self._remaining))
        # Avoid repainting the (hidden) ring view in normal mode; it can cause jitter
        # when the widget is resized/animated in a small drawer.
        if self._stack.currentIndex() == 1:
            self.ring.set_time(self._remaining, total)

    @staticmethod
    def _fmt(seconds: int) -> str:
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"
