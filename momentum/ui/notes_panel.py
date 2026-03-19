"""Per-lesson notes panel with inline timestamped entry."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from momentum.models.entities import Note
from momentum.utils.helpers import format_duration


class NotesPanel(QWidget):
    """Notes tab with inline timestamped note creation."""

    note_saved = Signal(str, int)      # content, video_timestamp_ms
    note_deleted = Signal(int)         # note_id
    timestamp_clicked = Signal(int)    # seek to video_timestamp_ms

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("notesPanel")
        self._current_lesson_id: int | None = None
        self._current_ts_ms: int = 0
        self._auto_timestamp = True
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Title row
        title_row = QHBoxLayout()
        title = QLabel("Notes")
        title.setObjectName("panelTitle")
        title_row.addWidget(title)
        title_row.addStretch()

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("noteDeleteButton")
        self.btn_delete.setFixedHeight(26)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_delete.setEnabled(False)
        title_row.addWidget(self.btn_delete)
        layout.addLayout(title_row)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self.line_edit = QLineEdit()
        self.line_edit.setObjectName("noteInput")
        self.line_edit.setPlaceholderText("Add a note at 00:00…")
        self.line_edit.returnPressed.connect(self._on_save)
        input_row.addWidget(self.line_edit, stretch=1)

        self.btn_auto_ts = QPushButton("Auto-timestamping on")
        self.btn_auto_ts.setObjectName("autoTimestampButton")
        self.btn_auto_ts.setCheckable(True)
        self.btn_auto_ts.setChecked(True)
        self.btn_auto_ts.clicked.connect(self._toggle_auto_ts)
        input_row.addWidget(self.btn_auto_ts)

        self.btn_add = QPushButton("Add Note")
        self.btn_add.setObjectName("saveNoteButton")
        self.btn_add.clicked.connect(self._on_save)
        input_row.addWidget(self.btn_add)

        layout.addLayout(input_row)

        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.setObjectName("notesList")
        self.notes_list.setSpacing(4)
        self.notes_list.currentRowChanged.connect(
            lambda row: self.btn_delete.setEnabled(row >= 0)
        )
        self.notes_list.itemDoubleClicked.connect(self._on_item_dbl)
        layout.addWidget(self.notes_list, stretch=1)

    # ── Public ───────────────────────────────────────────────────────

    def set_lesson(self, lesson_id: int) -> None:
        self._current_lesson_id = lesson_id
        self.notes_list.clear()
        self.line_edit.clear()

    def display_notes(self, notes: list[Note]) -> None:
        self.notes_list.clear()
        for note in notes:
            ts = format_duration(note.video_timestamp_ms)
            item = QListWidgetItem(f"  {ts}     •     {note.content}")
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)

    def update_timestamp(self, position_ms: int) -> None:
        """Called by the dashboard whenever the video position changes."""
        self._current_ts_ms = position_ms
        if self._auto_timestamp:
            ts = format_duration(position_ms)
            self.line_edit.setPlaceholderText(f"Add a note at {ts}…")

    # ── Slots ────────────────────────────────────────────────────────

    def _on_save(self) -> None:
        content = self.line_edit.text().strip()
        if content:
            self.note_saved.emit(content, self._current_ts_ms if self._auto_timestamp else 0)
            self.line_edit.clear()

    def _on_delete(self) -> None:
        item = self.notes_list.currentItem()
        if item:
            note: Note = item.data(Qt.ItemDataRole.UserRole)
            if note and note.id is not None:
                self.note_deleted.emit(note.id)

    def _on_item_dbl(self, item: QListWidgetItem) -> None:
        note: Note = item.data(Qt.ItemDataRole.UserRole)
        if note:
            self.timestamp_clicked.emit(note.video_timestamp_ms)

    def _toggle_auto_ts(self, checked: bool) -> None:
        self._auto_timestamp = checked
        self.btn_auto_ts.setText("Auto-timestamping on" if checked else "Auto-timestamping off")
        if not checked:
            self.line_edit.setPlaceholderText("Add a note…")
