"""Application main window — manages view stack and global actions."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
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
        self._nav_anim: QParallelAnimationGroup | None = None

        self._build_ui()
        self._build_menus()
        self._wire()
        self._refresh_home()

    # ── UI construction ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Momentum")
        self.setMinimumSize(Config.MIN_WINDOW_WIDTH, Config.MIN_WINDOW_HEIGHT)
        self.resize(1400, 850)

        if Config.ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(Config.ICON_PATH)))

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
        self.home_view.analytics_requested.connect(self._show_analytics)
        self.dashboard_view.back_requested.connect(lambda: self._goto(ViewIndex.HOME))
        self.analytics_view.back_requested.connect(lambda: self._goto(ViewIndex.HOME))

    # ── Navigation ───────────────────────────────────────────────────

    def _goto(self, view: ViewIndex) -> None:
        if view == ViewIndex.HOME:
            self._refresh_home()
        self._animate_to(view.value)

    def _animate_to(self, index: int) -> None:
        if index == self.stack.currentIndex():
            return

        # Stop any in-flight animation.
        if self._nav_anim and self._nav_anim.state() == self._nav_anim.State.Running:
            self._nav_anim.stop()

        current = self.stack.currentWidget()
        nxt = self.stack.widget(index)
        if not current or not nxt:
            self.stack.setCurrentIndex(index)
            return

        # Fade out current, swap, fade in next.
        out_fx = QGraphicsOpacityEffect(current)
        out_fx.setOpacity(1.0)
        current.setGraphicsEffect(out_fx)

        in_fx = QGraphicsOpacityEffect(nxt)
        in_fx.setOpacity(0.0)
        nxt.setGraphicsEffect(in_fx)

        fade_out = QPropertyAnimation(out_fx, b"opacity", self)
        fade_out.setDuration(140)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)

        fade_in = QPropertyAnimation(in_fx, b"opacity", self)
        fade_in.setDuration(160)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InOutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade_out)

        def _swap() -> None:
            self.stack.setCurrentIndex(index)
            fade_in.start()

        fade_out.finished.connect(_swap)

        def _cleanup() -> None:
            # Remove effects to avoid stacking effects and GPU overhead.
            current.setGraphicsEffect(None)
            nxt.setGraphicsEffect(None)

        group.finished.connect(_cleanup)
        self._nav_anim = group
        group.start()

    def _refresh_home(self) -> None:
        courses = self.db.get_all_courses()
        self.home_view.display_courses(courses)
        overview = self.analytics_svc.get_overview()
        weekly_minutes = [m for _, m in self.analytics_svc.get_weekly_data()]
        self.home_view.update_home_stats(
            streak_days=overview.get("streak", 0),
            weekly_minutes=weekly_minutes,
            total_courses=overview.get("total_courses", 0),
            total_hours=overview.get("total_hours", 0.0),
            completed_lessons=overview.get("completed_lessons", 0),
        )

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
