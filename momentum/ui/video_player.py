"""Integrated video player with transport controls and progress tracking."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
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

    _AUTOSAVE_INTERVAL_MS = 5_000
    _SEEK_STEP_MS = 10_000

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._current_file: str | None = None
        self._completion_emitted = False

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
        self.player.setVideoOutput(self.video_widget)

    # ── UI ───────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setMinimumHeight(280)
        layout.addWidget(self.video_widget)

        controls = QWidget()
        controls.setObjectName("videoControls")
        cl = QVBoxLayout(controls)
        cl.setContentsMargins(16, 8, 16, 8)
        cl.setSpacing(4)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("videoSlider")
        self.slider.setRange(0, 0)
        cl.addWidget(self.slider)

        row = QHBoxLayout()
        row.setSpacing(8)

        self.btn_play = QPushButton("▶")
        self.btn_play.setObjectName("playButton")
        self.btn_play.setFixedSize(40, 40)
        row.addWidget(self.btn_play)

        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(32, 32)
        row.addWidget(self.btn_stop)

        self.btn_back = QPushButton("⏪ 10s")
        self.btn_back.setFixedSize(56, 32)
        row.addWidget(self.btn_back)

        self.btn_fwd = QPushButton("10s ⏩")
        self.btn_fwd.setFixedSize(56, 32)
        row.addWidget(self.btn_fwd)

        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setObjectName("timeLabel")
        row.addWidget(self.lbl_time)

        row.addStretch()

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(32, 32)
        row.addWidget(self.btn_mute)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setObjectName("volumeSlider")
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.setFixedWidth(100)
        row.addWidget(self.vol_slider)

        cl.addLayout(row)
        layout.addWidget(controls)

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

    def get_position(self) -> int:
        return self.player.position()

    def get_duration(self) -> int:
        return self.player.duration()

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
