"""Qt stylesheets for dark and light themes."""


class Theme:
    DARK = "dark"
    LIGHT = "light"

    @staticmethod
    def get_stylesheet(theme: str = "dark") -> str:
        return _DARK_THEME if theme == "dark" else _LIGHT_THEME


# ── Dark Theme ───────────────────────────────────────────────────────

_DARK_THEME = """
/* ─── Global ─────────────────────────────────────────────── */
QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: #7c3aed;
    selection-color: #ffffff;
}

/* ─── Main Window ────────────────────────────────────────── */
QMainWindow {
    background-color: #0d1117;
}

QMenuBar {
    background-color: #161b22;
    color: #e6edf3;
    border-bottom: 1px solid #21262d;
    padding: 2px 0;
}
QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: #21262d;
}
QMenu {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #7c3aed;
}

QStatusBar {
    background-color: #161b22;
    color: #8b949e;
    border-top: 1px solid #21262d;
    padding: 4px 12px;
    font-size: 12px;
}

/* ─── Sidebar ────────────────────────────────────────────── */
#sidebar {
    background-color: #161b22;
    border-right: 1px solid #21262d;
}

#sidebarHeader {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
}

#courseNameLabel {
    font-size: 16px;
    font-weight: 600;
    color: #e6edf3;
    padding-bottom: 4px;
}

#progressLabel {
    font-size: 12px;
    color: #8b949e;
}
#percentLabel {
    font-size: 12px;
    color: #7c3aed;
    font-weight: 600;
}

#courseProgressBar {
    background-color: #21262d;
    border: none;
    border-radius: 3px;
}
#courseProgressBar::chunk {
    background-color: #7c3aed;
    border-radius: 3px;
}

/* ─── Lesson Tree ────────────────────────────────────────── */
#lessonTree {
    background-color: #161b22;
    border: none;
    outline: none;
    padding: 4px;
    font-size: 13px;
}
#lessonTree::item {
    padding: 8px 8px;
    border-radius: 6px;
    margin: 1px 4px;
}
#lessonTree::item:selected {
    background-color: #7c3aed22;
    color: #a78bfa;
}
#lessonTree::item:hover {
    background-color: #21262d;
}
#lessonTree::branch {
    background-color: transparent;
}

/* ─── Video Controls ─────────────────────────────────────── */
#videoControls {
    background-color: #161b22;
    border-top: 1px solid #21262d;
}

#playButton {
    background-color: #7c3aed;
    color: #ffffff;
    border: none;
    border-radius: 20px;
    font-size: 16px;
    font-weight: bold;
}
#playButton:hover {
    background-color: #6d28d9;
}
#playButton:pressed {
    background-color: #5b21b6;
}

QPushButton {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #484f58;
}
QPushButton:pressed {
    background-color: #484f58;
}

#timeLabel {
    color: #8b949e;
    font-size: 12px;
    font-family: "Consolas", "Courier New", monospace;
    min-width: 110px;
}

/* ─── Sliders ────────────────────────────────────────────── */
#videoSlider::groove:horizontal {
    height: 6px;
    background: #21262d;
    border-radius: 3px;
}
#videoSlider::handle:horizontal {
    background: #7c3aed;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
#videoSlider::sub-page:horizontal {
    background: #7c3aed;
    border-radius: 3px;
}

#volumeSlider::groove:horizontal {
    height: 4px;
    background: #21262d;
    border-radius: 2px;
}
#volumeSlider::handle:horizontal {
    background: #8b949e;
    width: 10px;
    height: 10px;
    margin: -3px 0;
    border-radius: 5px;
}
#volumeSlider::sub-page:horizontal {
    background: #8b949e;
    border-radius: 2px;
}

/* ─── Tabs ───────────────────────────────────────────────── */
QTabWidget::pane {
    background-color: #0d1117;
    border: none;
    border-top: 1px solid #21262d;
}
QTabBar::tab {
    background-color: transparent;
    color: #8b949e;
    padding: 10px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
}
QTabBar::tab:selected {
    color: #e6edf3;
    border-bottom: 2px solid #7c3aed;
}
QTabBar::tab:hover {
    color: #e6edf3;
    background-color: #21262d;
}

/* ─── Notes Panel ────────────────────────────────────────── */
#notesPanel {
    background-color: #0d1117;
}
#noteInput {
    background-color: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}
#noteInput:focus {
    border-color: #7c3aed;
}

#notesList {
    background-color: transparent;
    border: none;
    outline: none;
}
#notesList::item {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 6px;
    padding: 10px 12px;
    margin-bottom: 4px;
    color: #e6edf3;
}
#notesList::item:selected {
    border-color: #7c3aed;
}

#saveNoteButton {
    background-color: #7c3aed;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
}
#saveNoteButton:hover {
    background-color: #6d28d9;
}

#panelTitle {
    font-size: 14px;
    font-weight: 600;
    color: #e6edf3;
}

/* ─── Pomodoro ───────────────────────────────────────────── */
#pomodoroPanel {
    background-color: #0d1117;
}
#pomodoroStatus {
    font-size: 12px;
    font-weight: 600;
    color: #7c3aed;
    letter-spacing: 2px;
}
#pomodoroTime {
    font-size: 56px;
    font-weight: 300;
    color: #e6edf3;
    font-family: "Consolas", "Courier New", monospace;
}
#pomodoroProgress {
    background-color: #21262d;
    border: none;
    border-radius: 3px;
}
#pomodoroProgress::chunk {
    background-color: #7c3aed;
    border-radius: 3px;
}
#pomodoroStart {
    background-color: #7c3aed;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 28px;
    font-weight: 600;
    font-size: 14px;
}
#pomodoroStart:hover {
    background-color: #6d28d9;
}
#pomodoroReset {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 28px;
    font-size: 14px;
}
#pomodoroSessions {
    color: #8b949e;
    font-size: 12px;
}

/* ─── Home View ──────────────────────────────────────────── */
#homeView {
    background-color: #0d1117;
}
#appTitle {
    font-size: 28px;
    font-weight: 700;
    color: #e6edf3;
}
#appSubtitle {
    font-size: 14px;
    color: #8b949e;
    padding-top: 2px;
}
#addCourseButton {
    background-color: #7c3aed;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
}
#addCourseButton:hover {
    background-color: #6d28d9;
}

#courseScroll {
    background-color: transparent;
    border: none;
}

/* ─── Course Cards ───────────────────────────────────────── */
#courseCard {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
}
#courseCard:hover {
    border-color: #7c3aed;
    background-color: #1c2333;
}
#cardTitle {
    font-size: 15px;
    font-weight: 600;
    color: #e6edf3;
}
#cardStats {
    font-size: 12px;
    color: #8b949e;
}
#cardProgress {
    background-color: #21262d;
    border: none;
    border-radius: 2px;
}
#cardProgress::chunk {
    background-color: #7c3aed;
    border-radius: 2px;
}
#cardPercent {
    font-size: 12px;
    color: #7c3aed;
    font-weight: 600;
}

#emptyStateText {
    font-size: 15px;
    color: #8b949e;
    line-height: 1.6;
}

/* ─── Dashboard Toolbar ──────────────────────────────────── */
#dashToolbar {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
}
#backButton {
    background-color: transparent;
    border: none;
    color: #8b949e;
    font-size: 13px;
    padding: 6px 12px;
}
#backButton:hover {
    color: #e6edf3;
}
#completeButton {
    background-color: #238636;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 600;
}
#completeButton:hover {
    background-color: #2ea043;
}
#nextButton {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 16px;
}
#nextButton:hover {
    background-color: #30363d;
}

/* ─── Analytics View ─────────────────────────────────────── */
#analyticsView {
    background-color: #0d1117;
}
#pageTitle {
    font-size: 22px;
    font-weight: 700;
    color: #e6edf3;
}
#sectionTitle {
    font-size: 15px;
    font-weight: 600;
    color: #e6edf3;
    padding-top: 8px;
}

#statCard {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
}
#statTitle {
    font-size: 12px;
    color: #8b949e;
    font-weight: 500;
}
#statValue {
    font-size: 28px;
    font-weight: 700;
    color: #e6edf3;
}
#statSubtitle {
    font-size: 11px;
    color: #7c3aed;
}

/* ─── Scroll Bars ────────────────────────────────────────── */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 4px;
    min-width: 30px;
}

/* ─── Tooltips ───────────────────────────────────────────── */
QToolTip {
    background-color: #1c2333;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ─── Message Box ────────────────────────────────────────── */
QMessageBox {
    background-color: #161b22;
}
QMessageBox QLabel {
    color: #e6edf3;
}

/* ─── Video Widget ───────────────────────────────────────── */
QVideoWidget {
    background-color: #000000;
}
"""

# ── Light Theme ──────────────────────────────────────────────────────

_LIGHT_THEME = """
QWidget {
    background-color: #ffffff;
    color: #1f2328;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: #7c3aed;
    selection-color: #ffffff;
}

QMainWindow { background-color: #ffffff; }

QMenuBar {
    background-color: #f6f8fa;
    color: #1f2328;
    border-bottom: 1px solid #d0d7de;
    padding: 2px 0;
}
QMenuBar::item { padding: 6px 12px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #eaeef2; }
QMenu {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item { padding: 8px 24px; border-radius: 4px; }
QMenu::item:selected { background-color: #7c3aed; color: #ffffff; }

QStatusBar {
    background-color: #f6f8fa;
    color: #656d76;
    border-top: 1px solid #d0d7de;
    padding: 4px 12px;
    font-size: 12px;
}

#sidebar { background-color: #f6f8fa; border-right: 1px solid #d0d7de; }
#sidebarHeader { background-color: #f6f8fa; border-bottom: 1px solid #d0d7de; }
#courseNameLabel { font-size: 16px; font-weight: 600; color: #1f2328; }
#progressLabel { font-size: 12px; color: #656d76; }
#percentLabel { font-size: 12px; color: #7c3aed; font-weight: 600; }

#courseProgressBar { background-color: #eaeef2; border: none; border-radius: 3px; }
#courseProgressBar::chunk { background-color: #7c3aed; border-radius: 3px; }

#lessonTree { background-color: #f6f8fa; border: none; padding: 4px; }
#lessonTree::item { padding: 8px 8px; border-radius: 6px; margin: 1px 4px; }
#lessonTree::item:selected { background-color: #7c3aed22; color: #6d28d9; }
#lessonTree::item:hover { background-color: #eaeef2; }
#lessonTree::branch { background-color: transparent; }

#videoControls { background-color: #f6f8fa; border-top: 1px solid #d0d7de; }
#playButton { background-color: #7c3aed; color: #fff; border: none; border-radius: 20px; font-size: 16px; }
#playButton:hover { background-color: #6d28d9; }

QPushButton {
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #eaeef2; }

#timeLabel { color: #656d76; font-size: 12px; font-family: "Consolas", monospace; min-width: 110px; }

#videoSlider::groove:horizontal { height: 6px; background: #eaeef2; border-radius: 3px; }
#videoSlider::handle:horizontal { background: #7c3aed; width: 14px; height: 14px; margin: -4px 0; border-radius: 7px; }
#videoSlider::sub-page:horizontal { background: #7c3aed; border-radius: 3px; }

QTabWidget::pane { background-color: #ffffff; border: none; border-top: 1px solid #d0d7de; }
QTabBar::tab { background: transparent; color: #656d76; padding: 10px 20px; border: none; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #1f2328; border-bottom: 2px solid #7c3aed; }
QTabBar::tab:hover { color: #1f2328; background-color: #f6f8fa; }

#notesPanel { background-color: #ffffff; }
#noteInput { background-color: #f6f8fa; color: #1f2328; border: 1px solid #d0d7de; border-radius: 8px; padding: 8px 12px; }
#noteInput:focus { border-color: #7c3aed; }
#notesList { background-color: transparent; border: none; }
#notesList::item { background-color: #f6f8fa; border: 1px solid #eaeef2; border-radius: 6px; padding: 10px; margin-bottom: 4px; }
#saveNoteButton { background-color: #7c3aed; color: #fff; border: none; border-radius: 6px; padding: 8px 20px; font-weight: 600; }

#pomodoroPanel { background-color: #ffffff; }
#pomodoroStatus { font-size: 12px; font-weight: 600; color: #7c3aed; letter-spacing: 2px; }
#pomodoroTime { font-size: 56px; font-weight: 300; color: #1f2328; font-family: "Consolas", monospace; }
#pomodoroProgress { background-color: #eaeef2; border: none; border-radius: 3px; }
#pomodoroProgress::chunk { background-color: #7c3aed; border-radius: 3px; }
#pomodoroStart { background-color: #7c3aed; color: #fff; border: none; border-radius: 6px; padding: 10px 28px; font-weight: 600; font-size: 14px; }
#pomodoroReset { background-color: #f6f8fa; color: #1f2328; border: 1px solid #d0d7de; border-radius: 6px; padding: 10px 28px; }
#pomodoroSessions { color: #656d76; font-size: 12px; }

#homeView { background-color: #ffffff; }
#appTitle { font-size: 28px; font-weight: 700; color: #1f2328; }
#appSubtitle { font-size: 14px; color: #656d76; }
#addCourseButton { background-color: #7c3aed; color: #fff; border: none; border-radius: 8px; padding: 10px 24px; font-size: 14px; font-weight: 600; }
#courseScroll { background-color: transparent; border: none; }

#courseCard { background-color: #f6f8fa; border: 1px solid #d0d7de; border-radius: 12px; }
#courseCard:hover { border-color: #7c3aed; background-color: #f0f0ff; }
#cardTitle { font-size: 15px; font-weight: 600; color: #1f2328; }
#cardStats { font-size: 12px; color: #656d76; }
#cardProgress { background-color: #eaeef2; border: none; border-radius: 2px; }
#cardProgress::chunk { background-color: #7c3aed; border-radius: 2px; }
#cardPercent { font-size: 12px; color: #7c3aed; font-weight: 600; }
#emptyStateText { font-size: 15px; color: #656d76; }

#dashToolbar { background-color: #f6f8fa; border-bottom: 1px solid #d0d7de; }
#backButton { background: transparent; border: none; color: #656d76; padding: 6px 12px; }
#backButton:hover { color: #1f2328; }
#completeButton { background-color: #1a7f37; color: #fff; border: none; border-radius: 6px; padding: 6px 16px; font-weight: 600; }
#nextButton { background-color: #f6f8fa; color: #1f2328; border: 1px solid #d0d7de; border-radius: 6px; padding: 6px 16px; }

#analyticsView { background-color: #ffffff; }
#pageTitle { font-size: 22px; font-weight: 700; color: #1f2328; }
#sectionTitle { font-size: 15px; font-weight: 600; color: #1f2328; }
#statCard { background-color: #f6f8fa; border: 1px solid #d0d7de; border-radius: 12px; }
#statTitle { font-size: 12px; color: #656d76; }
#statValue { font-size: 28px; font-weight: 700; color: #1f2328; }
#statSubtitle { font-size: 11px; color: #7c3aed; }

QScrollBar:vertical { background: transparent; width: 8px; }
QScrollBar::handle:vertical { background: #d0d7de; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QVideoWidget { background-color: #000000; }
QToolTip { background-color: #ffffff; color: #1f2328; border: 1px solid #d0d7de; border-radius: 6px; padding: 6px 10px; }
QMessageBox { background-color: #ffffff; }
"""
