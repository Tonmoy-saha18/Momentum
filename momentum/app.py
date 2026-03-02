"""Application bootstrap — creates QApplication, database, and main window."""

from __future__ import annotations

import logging
import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from momentum.config import Config
from momentum.models.database import Database
from momentum.ui.main_window import MainWindow
from momentum.ui.theme import Theme

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(name)s]  %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


class MomentumApp:
    """Thin wrapper that wires the Qt application together."""

    def __init__(self, argv: list[str] | None = None):
        self.qt = QApplication(argv or sys.argv)
        self.qt.setApplicationName(Config.APP_NAME)
        self.qt.setApplicationVersion(Config.VERSION)
        self.qt.setStyleSheet(Theme.get_stylesheet(Theme.DARK))

        font = QFont("Segoe UI", 10)
        self.qt.setFont(font)

        Config.ensure_dirs()
        self.db = Database()
        self.window = MainWindow(self.db)

    def run(self) -> int:
        self.window.show()
        return self.qt.exec()
