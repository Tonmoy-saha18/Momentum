"""Per-lesson notes panel with timestamped entries."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from momentum.models.entities import Note
from momentum.utils.helpers import format_duration


class NotesPanel(QWidget):
    """Notes tab allowing users to create and review timestamped notes."""

    note_saved = Signal(str, int)      # content, video_timestamp_ms
    note_deleted = Signal(int)         # note_id
    timestamp_clicked = Signal(int)    # seek to video_timestamp_ms

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("notesPanel")
        self._current_lesson_id: int | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Notes")
        title.setObjectName("panelTitle")
        header.addWidget(title)
        header.addStretch()

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setFixedHeight(28)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_delete.setEnabled(False)
        header.addWidget(self.btn_delete)
        layout.addLayout(header)

        self.notes_list = QListWidget()
        self.notes_list.setObjectName("notesList")
        self.notes_list.setSpacing(4)
        self.notes_list.currentRowChanged.connect(
            lambda row: self.btn_delete.setEnabled(row >= 0)
        )
        self.notes_list.itemDoubleClicked.connect(self._on_item_dbl)
        layout.addWidget(self.notes_list, stretch=1)

        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("noteInput")
        self.text_edit.setPlaceholderText("Add a note at the current timestamp…")
        self.text_edit.setMaximumHeight(80)
        layout.addWidget(self.text_edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_save = QPushButton("Save Note")
        self.btn_save.setObjectName("saveNoteButton")
        self.btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

    # ── Public ───────────────────────────────────────────────────────

    def set_lesson(self, lesson_id: int) -> None:
        self._current_lesson_id = lesson_id
        self.notes_list.clear()
        self.text_edit.clear()

    def display_notes(self, notes: list[Note]) -> None:
        self.notes_list.clear()
        for note in notes:
            ts = format_duration(note.video_timestamp_ms)
            item = QListWidgetItem(f"[{ts}]  {note.content}")
            item.setData(Qt.ItemDataRole.UserRole, note)
            self.notes_list.addItem(item)

    # ── Slots ────────────────────────────────────────────────────────

    def _on_save(self) -> None:
        content = self.text_edit.toPlainText().strip()
        if content:
            self.note_saved.emit(content, 0)
            self.text_edit.clear()

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
