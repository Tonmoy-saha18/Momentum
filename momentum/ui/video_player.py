"""Integrated video player with transport controls and progress tracking."""

from __future__ import annotations

from PySide6.QtCore import QEvent, Qt, QTimer, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from momentum.config import Config
from momentum.utils.helpers import format_duration


class VideoPlayer(QWidget):
    """Self-contained video player widget with play controls."""

    position_changed = Signal(int, int)  # position_ms, duration_ms
    video_completed = Signal()
    playback_started = Signal()
    playback_paused = Signal()
    fullscreen_changed = Signal(bool)

    _AUTOSAVE_INTERVAL_MS = 5_000
    _SEEK_STEP_MS = 10_000

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._current_file: str | None = None
        self._completion_emitted = False
        self._focus_ui = False
        self._kbd_grabbed = False

        self._build_player()
        self._build_ui()
        self._connect_signals()

        self._autosave = QTimer(self)
        self._autosave.setInterval(self._AUTOSAVE_INTERVAL_MS)
        self._autosave.timeout.connect(self._emit_position)

    # ── Player core ──────────────────────────────────────────────────

    def _build_player(self) -> None:
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.audio.setVolume(0.7)
        self.player.setAudioOutput(self.audio)
        self.video_widget = QVideoWidget()
        self.video_widget.installEventFilter(self)
        self.player.setVideoOutput(self.video_widget)

    # ── UI ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        surface = QWidget()
        surface.setObjectName("videoSurface")
        sl = QVBoxLayout(surface)
        sl.setContentsMargins(10, 8, 10, 8)
        sl.setSpacing(8)

        # Top title pill (focus mode screenshot)
        self.title_pill = QLabel("")
        self.title_pill.setObjectName("videoTitlePill")
        self.title_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_pill.setFixedHeight(44)
        self.title_pill.hide()
        sl.addWidget(self.title_pill, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Video surface — takes all available space
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setMinimumHeight(200)
        sl.addWidget(self.video_widget, stretch=1)

        # ── Floating controls overlay (both screenshots) ───────────
        controls_outer = QWidget()
        controls_outer.setObjectName("videoControlsOuter")
        col = QHBoxLayout(controls_outer)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        col.addStretch()

        controls = QFrame()
        controls.setObjectName("videoOverlayControls")
        controls.setFixedHeight(66)
        controls.setMinimumWidth(760)
        controls.setMaximumWidth(980)
        cl = QVBoxLayout(controls)
        cl.setContentsMargins(16, 10, 16, 10)
        cl.setSpacing(6)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("videoSlider")
        self.slider.setRange(0, 0)
        self.slider.setFixedHeight(14)
        cl.addWidget(self.slider)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.setContentsMargins(0, 0, 0, 0)

        self.btn_play = QPushButton("▶")
        self.btn_play.setObjectName("playButton")
        self.btn_play.setFixedSize(30, 30)
        row.addWidget(self.btn_play)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setObjectName("transportButton")
        self.btn_stop.setFixedSize(30, 30)
        self.btn_stop.setToolTip("Stop")
        row.addWidget(self.btn_stop)

        self.btn_back = QPushButton("−10s")
        self.btn_back.setObjectName("transportButton")
        self.btn_back.setFixedSize(46, 30)
        row.addWidget(self.btn_back)

        self.btn_fwd = QPushButton("+10s")
        self.btn_fwd.setObjectName("transportButton")
        self.btn_fwd.setFixedSize(46, 30)
        row.addWidget(self.btn_fwd)

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setObjectName("transportButton")
        self.btn_mute.setFixedSize(30, 30)
        row.addWidget(self.btn_mute)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setObjectName("volumeSlider")
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.setFixedWidth(90)
        self.vol_slider.setFixedHeight(14)
        row.addWidget(self.vol_slider)

        row.addStretch()

        # self.btn_speed = QPushButton("1.5x")
        # self.btn_speed.setObjectName("speedButton")
        # self.btn_speed.setFixedSize(54, 30)
        # self.btn_speed.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # row.addWidget(self.btn_speed)

        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setObjectName("timeLabel")
        self.lbl_time.setFixedWidth(130)
        row.addWidget(self.lbl_time)

        self.btn_fullscreen = QPushButton("⛶")
        self.btn_fullscreen.setObjectName("transportButton")
        self.btn_fullscreen.setFixedSize(30, 30)
        self.btn_fullscreen.setToolTip("Fullscreen")
        row.addWidget(self.btn_fullscreen)

        cl.addLayout(row)
        col.addWidget(controls)
        col.addStretch()
        sl.addWidget(controls_outer, alignment=Qt.AlignmentFlag.AlignBottom)

        root.addWidget(surface, stretch=1)

    # ── Signals ──────────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self.player.positionChanged.connect(self._on_position)
        self.player.durationChanged.connect(self._on_duration)
        self.player.playbackStateChanged.connect(self._on_state)

        self.btn_play.clicked.connect(self.toggle_playback)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_back.clicked.connect(lambda: self.seek_relative(-self._SEEK_STEP_MS))
        self.btn_fwd.clicked.connect(lambda: self.seek_relative(self._SEEK_STEP_MS))
        self.btn_mute.clicked.connect(self.toggle_mute)
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.video_widget.fullScreenChanged.connect(self._on_fullscreen_changed)

        self.slider.sliderMoved.connect(self._on_slider)
        self.vol_slider.valueChanged.connect(self._on_volume)

    # ── Public controls ──────────────────────────────────────────────

    def load_video(self, file_path: str, start_position_ms: int = 0) -> None:
        self._current_file = file_path
        self._completion_emitted = False
        self.player.setSource(QUrl.fromLocalFile(file_path))
        if start_position_ms > 0:
            QTimer.singleShot(500, lambda: self.player.setPosition(start_position_ms))
        self.player.play()
        self._autosave.start()

    def toggle_playback(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def stop(self) -> None:
        self.player.stop()
        self._autosave.stop()

    def seek_relative(self, ms: int) -> None:
        pos = max(0, min(self.player.position() + ms, self.player.duration()))
        self.player.setPosition(pos)

    def toggle_mute(self) -> None:
        muted = not self.audio.isMuted()
        self.audio.setMuted(muted)
        self.btn_mute.setText("🔇" if muted else "🔊")

    def toggle_fullscreen(self) -> None:
        if self.video_widget.isFullScreen():
            self.video_widget.setFullScreen(False)
        else:
            self.video_widget.setFullScreen(True)
            self.video_widget.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def _on_fullscreen_changed(self, fs: bool) -> None:
        self.btn_fullscreen.setToolTip("Exit Fullscreen" if fs else "Fullscreen")
        self.btn_fullscreen.setText("🗗" if fs else "⛶")
        if fs and not self._kbd_grabbed:
            self.video_widget.grabKeyboard()
            self._kbd_grabbed = True
        if not fs and self._kbd_grabbed:
            self.video_widget.releaseKeyboard()
            self._kbd_grabbed = False
        self.fullscreen_changed.emit(fs)

    def eventFilter(self, obj, event):  # noqa: N802
        if obj is self.video_widget and self.video_widget.isFullScreen():
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                self.video_widget.setFullScreen(False)
                return True
        return super().eventFilter(obj, event)

    def get_position(self) -> int:
        return self.player.position()

    def get_duration(self) -> int:
        return self.player.duration()

    def set_focus_ui(self, enabled: bool) -> None:
        """Adjust overlays for focus mode."""
        self._focus_ui = enabled
        self.title_pill.setVisible(enabled and bool(self.title_pill.text().strip()))

    def set_title(self, title: str) -> None:
        self.title_pill.setText(title)
        self.title_pill.setVisible(self._focus_ui and bool(title.strip()))

    # ── Slots ────────────────────────────────────────────────────────

    def _on_position(self, pos: int) -> None:
        if not self.slider.isSliderDown():
            self.slider.setValue(pos)
        dur = self.player.duration()
        self.lbl_time.setText(f"{format_duration(pos)} / {format_duration(dur)}")
        self.position_changed.emit(pos, dur)

        if dur > 0 and not self._completion_emitted and pos >= dur * Config.COMPLETION_THRESHOLD:
            self._completion_emitted = True
            self.video_completed.emit()

    def _on_duration(self, dur: int) -> None:
        self.slider.setRange(0, dur)

    def _on_state(self, state: QMediaPlayer.PlaybackState) -> None:
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setText("⏸")
            self.playback_started.emit()
        else:
            self.btn_play.setText("▶")
            if state == QMediaPlayer.PlaybackState.PausedState:
                self.playback_paused.emit()

    def _on_slider(self, position: int) -> None:
        self.player.setPosition(position)

    def _on_volume(self, value: int) -> None:
        self.audio.setVolume(value / 100.0)

    def _emit_position(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.position_changed.emit(self.player.position(), self.player.duration())
