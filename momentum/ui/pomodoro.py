"""Built-in Pomodoro focus timer widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from momentum.config import Config


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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Pomodoro Timer")
        title.setObjectName("panelTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.lbl_status = QLabel("FOCUS TIME")
        self.lbl_status.setObjectName("pomodoroStatus")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        self.lbl_time = QLabel(self._fmt(self._remaining))
        self.lbl_time.setObjectName("pomodoroTime")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_time)

        self.progress = QProgressBar()
        self.progress.setObjectName("pomodoroProgress")
        self.progress.setRange(0, self._work)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        layout.addWidget(self.progress)

        btns = QHBoxLayout()
        btns.setSpacing(12)
        btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_start = QPushButton("Start")
        self.btn_start.setObjectName("pomodoroStart")
        self.btn_start.clicked.connect(self.toggle)
        btns.addWidget(self.btn_start)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setObjectName("pomodoroReset")
        self.btn_reset.clicked.connect(self.reset)
        btns.addWidget(self.btn_reset)

        layout.addLayout(btns)

        self.lbl_sessions = QLabel("Sessions: 0")
        self.lbl_sessions.setObjectName("pomodoroSessions")
        self.lbl_sessions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_sessions)

        layout.addStretch()

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
        self._refresh_display(self._work)
        self.lbl_status.setText("FOCUS TIME")
        self.btn_start.setText("Start")

    # ── Internal ─────────────────────────────────────────────────────

    def _tick(self) -> None:
        self._remaining -= 1
        total = self._short_break if self._is_break else self._work
        if self._is_break and self._session_count % self._long_every == 0:
            total = self._long_break
        self._refresh_display(total)
        self.timer_tick.emit(self._remaining)

        if self._remaining <= 0:
            self._clock.stop()
            self._is_running = False
            if not self._is_break:
                self._session_count += 1
                self.lbl_sessions.setText(f"Sessions: {self._session_count}")
                self.session_completed.emit(self._work)
                self._is_break = True
                if self._session_count % self._long_every == 0:
                    self._remaining = self._long_break
                    self.lbl_status.setText("LONG BREAK")
                else:
                    self._remaining = self._short_break
                    self.lbl_status.setText("SHORT BREAK")
            else:
                self._is_break = False
                self._remaining = self._work
                self.lbl_status.setText("FOCUS TIME")
            self._refresh_display(
                self._short_break if self._is_break else self._work
            )
            self.btn_start.setText("Start")

    def _refresh_display(self, total: int) -> None:
        elapsed = total - self._remaining
        self.progress.setRange(0, total)
        self.progress.setValue(max(0, elapsed))
        self.lbl_time.setText(self._fmt(self._remaining))

    @staticmethod
    def _fmt(seconds: int) -> str:
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"
