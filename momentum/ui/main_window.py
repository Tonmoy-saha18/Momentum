"""Application main window — manages view stack and global actions."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
)

from momentum.config import Config
from momentum.models.database import Database
from momentum.services.analytics_service import AnalyticsService
from momentum.services.folder_parser import FolderParser
from momentum.ui.analytics_view import AnalyticsView
from momentum.ui.dashboard import DashboardView
from momentum.ui.home_view import HomeView
from momentum.ui.theme import Theme
from momentum.utils.constants import ViewIndex


class MainWindow(QMainWindow):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.folder_parser = FolderParser(db)
        self.analytics_svc = AnalyticsService(db)

        self._build_ui()
        self._build_menus()
        self._wire()
        self._refresh_home()

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Momentum")
        self.setMinimumSize(Config.MIN_WINDOW_WIDTH, Config.MIN_WINDOW_HEIGHT)
        self.resize(1400, 850)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_view = HomeView()
        self.dashboard_view = DashboardView(self.db)
        self.analytics_view = AnalyticsView()

        self.stack.addWidget(self.home_view)       # 0 — Home
        self.stack.addWidget(self.dashboard_view)  # 1 — Dashboard
        self.stack.addWidget(self.analytics_view)  # 2 — Analytics

        self.statusBar().showMessage("Welcome to Momentum")

    def _build_menus(self) -> None:
        bar = self.menuBar()

        # File
        file_m = bar.addMenu("&File")
        file_m.addAction("Add Course…", self._on_add_course)
        file_m.addSeparator()
        file_m.addAction("Exit", self.close)

        # View
        view_m = bar.addMenu("&View")
        view_m.addAction("Home", lambda: self._goto(ViewIndex.HOME))
        view_m.addAction("Analytics", self._show_analytics)
        view_m.addSeparator()

        self._dark_act = QAction("Dark Mode", self)
        self._dark_act.setCheckable(True)
        self._dark_act.setChecked(True)
        self._dark_act.toggled.connect(self._toggle_theme)
        view_m.addAction(self._dark_act)

    def _wire(self) -> None:
        self.home_view.course_selected.connect(self._on_course_selected)
        self.home_view.folder_selected.connect(self._on_folder_selected)
        self.dashboard_view.back_requested.connect(lambda: self._goto(ViewIndex.HOME))
        self.analytics_view.back_requested.connect(lambda: self._goto(ViewIndex.HOME))

    # ── Navigation ───────────────────────────────────────────────────

    def _goto(self, view: ViewIndex) -> None:
        if view == ViewIndex.HOME:
            self._refresh_home()
        self.stack.setCurrentIndex(view.value)

    def _refresh_home(self) -> None:
        self.home_view.display_courses(self.db.get_all_courses())

    def _show_analytics(self) -> None:
        ov = self.analytics_svc.get_overview()
        self.analytics_view.update_stats(
            total_courses=ov["total_courses"],
            total_hours=ov["total_hours"],
            streak=ov["streak"],
            completed_lessons=ov["completed_lessons"],
            weekly_data=self.analytics_svc.get_weekly_data(),
        )
        self._goto(ViewIndex.ANALYTICS)

    # ── Slots ────────────────────────────────────────────────────────

    def _on_add_course(self) -> None:
        self.home_view._pick_folder()

    def _on_folder_selected(self, path: str) -> None:
        try:
            course = self.folder_parser.parse_course_folder(path)
            self.statusBar().showMessage(
                f"Loaded: {course.name} ({course.total_lessons} lessons)", 5000
            )
            self._refresh_home()
        except ValueError as exc:
            QMessageBox.warning(self, "Cannot Load Course", str(exc))

    def _on_course_selected(self, course_id: int) -> None:
        self.dashboard_view.load_course(course_id)
        self._goto(ViewIndex.DASHBOARD)

    def _toggle_theme(self, dark: bool) -> None:
        app = QApplication.instance()
        if app:
            app.setStyleSheet(Theme.get_stylesheet(Theme.DARK if dark else Theme.LIGHT))

    # ── Lifecycle ────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:  # noqa: N802
        self.dashboard_view.player.stop()
        super().closeEvent(event)
