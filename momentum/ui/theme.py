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
    background-color: #0a101b;
    color: #e6edf3;
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: #7c3aed;
    selection-color: #ffffff;
}

/* ─── Main Window ────────────────────────────────────────── */
QMainWindow {
    background-color: #0a101b;
}

QMenuBar {
    background-color: #0f1523;
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
    background-color: #121a2a;
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
    background-color: #0f1523;
    color: #8b949e;
    border-top: 1px solid #21262d;
    padding: 4px 12px;
    font-size: 12px;
}

/* ─── Sidebar ────────────────────────────────────────────── */
#sidebar {
    background-color: #0f1523;
    border-right: 1px solid #21262d;
}

#sidebarHeader {
    background-color: #0f1523;
    border-bottom: 1px solid #21262d;
}

#collapseButton {
    background-color: transparent;
    border: 1px solid #21262d;
    border-radius: 8px;
    color: #8b949e;
}
#collapseButton:hover {
    background-color: #21262d;
    color: #e6edf3;
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
    background-color: #0f1523;
    border: none;
    outline: none;
    padding: 8px;
    font-size: 13px;
    selection-background-color: #2d2250;
    selection-color: #c4b5fd;
}
#lessonTree::item {
    padding: 8px 8px;
    border-radius: 6px;
    margin: 1px 4px;
}
#lessonTree::item:selected {
    background-color: #2d2250;
    color: #c4b5fd;
}
#lessonTree::item:hover:!selected {
    background-color: #1c2333;
}
#lessonTree::branch {
    background-color: transparent;
}

/* ─── Video (surface + overlays) ─────────────────────────── */
#videoSurface { background-color: #000000; }

#videoOverlayControls {
    background-color: rgba(15, 21, 32, 200);
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 12px;
}

#videoTitlePill {
    background-color: rgba(45, 91, 98, 235);
    border: 1px solid rgba(172, 226, 220, 130);
    border-radius: 10px;
    padding: 8px 18px;
    color: #e6edf3;
    font-size: 22px;
    font-weight: 700;
}

#playButton {
    background-color: #7c3aed;
    color: #ffffff;
    border: none;
    border-radius: 14px;
    font-size: 15px;
    font-weight: bold;
    padding: 0px;
}
#playButton:hover {
    background-color: #6d28d9;
}
#playButton:pressed {
    background-color: #5b21b6;
}

#transportButton {
    background-color: #21262d;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 14px;
    font-size: 11px;
    padding: 0px;
}
#transportButton:hover {
    background-color: #30363d;
    color: #e6edf3;
    border-color: #484f58;
}
#transportButton:pressed {
    background-color: #3d4450;
}
#transportButton:focus {
    outline: none;
    border-color: #484f58;
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
    background: transparent;
    border: none;
}

#speedButton {
    background-color: rgba(33, 38, 45, 220);
    color: #e6edf3;
    border: 1px solid rgba(255, 255, 255, 20);
    border-radius: 8px;
    font-weight: 600;
}
#speedButton:hover { background-color: rgba(48, 54, 61, 230); }

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

#autoTimestampButton {
    background-color: #21262d;
    color: #cbd5e1;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 14px;
}
#autoTimestampButton:checked {
    border-color: rgba(124, 58, 237, 120);
}

#noteDeleteButton {
    background-color: transparent;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
}
#noteDeleteButton:enabled:hover {
    background-color: #21262d;
    color: #e6edf3;
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
#pomodoroBigTime {
    font-size: 54px;
    font-weight: 300;
    color: #e6edf3;
    font-family: "Consolas", "Courier New", monospace;
}

#pomodoroPrimary {
    background-color: #7c3aed;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 14px;
}
#pomodoroPrimary:hover {
    background-color: #6d28d9;
}

#pomodoroSecondary {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 13px;
}

#pomodoroSettings {
    background-color: transparent;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #8b949e;
    font-size: 14px;
}
#pomodoroSettings:hover { background-color: #21262d; color: #e6edf3; }

#pomodoroRingTime {
    font-size: 22px;
    font-weight: 700;
    color: #e6edf3;
    margin-top: -6px;
}
#pomodoroRingIcon {
    font-size: 16px;
    color: #e6edf3;
}

/* ─── Home View ──────────────────────────────────────────── */
#homeView {
    background-color: #0a101b;
}
#homePageScroll, #courseGrid {
    background: transparent;
    border: none;
}
#homeHero {
    background-color: #0f1523;
    border: 1px solid #202b43;
    border-radius: 20px;
}
#homeHero QWidget {
    background: transparent;
}
#homeScrollViewport {
    background: transparent;
}
#homeView QFrame, #homeView QLabel, #homeView QProgressBar {
    background: transparent;
}
#heroKicker {
    color: #7d8cae;
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 600;
}
#heroTitle {
    color: #f5f7ff;
    font-size: 38px;
    font-weight: 700;
    background: transparent;
}
#heroStatLabel {
    color: #7d8cae;
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: 600;
}
#heroStatValue {
    color: #9cb2ff;
    font-size: 28px;
    font-weight: 700;
}
#heroDivider {
    background-color: #22314e;
    border: none;
}
#homeSectionTitle {
    font-size: 24px;
    font-weight: 700;
    color: #f4f7ff;
    background: transparent;
}
#homeSectionSubtitle {
    font-size: 13px;
    color: #8b97b4;
    background: transparent;
}
#homeLibraryAction {
    color: #8ea2ff;
    font-size: 11px;
    letter-spacing: 1px;
    font-weight: 700;
    background: transparent;
}
#homeAnalyticsButton {
    background-color: rgba(18, 29, 48, 190);
    border: 1px solid #273753;
    border-radius: 10px;
    color: #eef4ff;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 700;
}
#homeAnalyticsButton:hover {
    border-color: #5f7dff;
    background-color: rgba(21, 34, 56, 210);
}

#homeMomentumTabs {
    background-color: rgba(15, 21, 35, 200);
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 14px;
}
#homeMomentumTab, #homeMomentumTabActive {
    border: none;
    border-radius: 10px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
}
#homeMomentumTab {
    background: transparent;
    color: #8b97b4;
}
#homeMomentumTab:hover {
    background-color: rgba(34, 45, 67, 180);
    color: #eef4ff;
}
#homeMomentumTabActive {
    background-color: rgba(95, 125, 255, 180);
    color: #0a101b;
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
    background-color: #121a2a;
    border: 1px solid #25334d;
    border-radius: 14px;
}
#courseCard QWidget {
    background: transparent;
}
#courseCard:hover {
    border-color: #3b7054;
    background-color: #152238;
}
#courseCardIcon {
    color: #73bf96;
    font-size: 15px;
}
#courseCardBadge {
    background-color: #1a2940;
    color: #a4b8d8;
    border: 1px solid #2f486f;
    border-radius: 9px;
    padding: 2px 8px;
    font-size: 9px;
    letter-spacing: 1px;
    font-weight: 700;
}
#cardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #eef2ff;
}
#cardSubtitle {
    font-size: 12px;
    color: #8e9cbc;
}
#cardStats {
    font-size: 10px;
    color: #8e9cbc;
    letter-spacing: 1px;
    font-weight: 600;
}
#cardProgress {
    background-color: #1f2b3f;
    border: 1px solid #2b3d5a;
    border-radius: 3px;
}
#cardProgress::chunk {
    background-color: #2ea043;
    border-radius: 3px;
}
#cardPercent {
    font-size: 11px;
    color: #6dd98f;
    font-weight: 600;
}
#addCourseCard {
    background-color: #0e1524;
    border: 1px dashed #334567;
    border-radius: 14px;
}
#addCourseCard:hover {
    border-color: #6583ff;
}
#addCourseCardPlus {
    font-size: 30px;
    color: #9cb0ff;
}
#addCourseCardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #edf2ff;
}
#addCourseCardSubtitle {
    font-size: 12px;
    color: #8f9cbc;
}
#momentumCard {
    background-color: #0f1523;
    border: 1px solid #202b43;
    border-radius: 16px;
}
#momentumCard QWidget {
    background: transparent;
}
#momentumKpiCard {
    background-color: #121d30;
    border: 1px solid #273753;
    border-radius: 12px;
    min-height: 56px;
}
#momentumKpiTitle {
    color: #8ea0c4;
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: 600;
}
#momentumKpiValue {
    color: #eef4ff;
    font-size: 16px;
    font-weight: 700;
}
#momentumDayChip {
    background-color: #1a263c;
    color: #a5b2d1;
    border: 1px solid #2a3958;
    border-radius: 10px;
    padding: 3px 8px;
    font-size: 10px;
    font-weight: 600;
}
#momentumDayChipActive {
    background-color: #31486e;
    color: #ecf2ff;
    border: 1px solid #4a6797;
    border-radius: 10px;
    padding: 3px 8px;
    font-size: 10px;
    font-weight: 700;
}
#momentumDate {
    color: #8390ad;
    font-size: 10px;
    letter-spacing: 1px;
}
#momentumBar {
    background-color: #222d43;
    border: 1px solid #2b3956;
    border-radius: 8px;
}
#momentumBarActive {
    background-color: #5f7dff;
    border: 1px solid #8aa0ff;
    border-radius: 8px;
}
#momentumChart { background: transparent; }

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

/* Modern lesson top bar (mock-aligned) */
#dashTopBar {
    background-color: #0f1523;
    border-bottom: 1px solid #21262d;
}
#focusModeLabel { color: #cbd5e1; font-size: 13px; }

#dashTitleBlock { background: transparent; }
#dashCourseTitle {
    background: transparent;
    color: #8b949e;
    font-size: 12px;
    padding: 0px;
}
#dashLessonTitle {
    background: transparent;
    color: #e6edf3;
    font-size: 13px;
    font-weight: 600;
    padding: 0px;
}

#focusSwitch { background: transparent; }
#focusSwitch::indicator {
    width: 42px;
    height: 22px;
    border-radius: 11px;
    background: #21262d;
    border: 1px solid #30363d;
}
#focusSwitch::indicator:checked {
    background: #7c3aed;
    border: 1px solid #6d28d9;
}
#streakChip {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 6px 10px;
    color: #d1d5db;
}
#bottomTabs { background: transparent; }
#bottomTab, #bottomTabActive {
    background: transparent;
    border: none;
    padding: 4px 0px;
    font-size: 13px;
}
#bottomTab { color: #8b949e; }
#bottomTab:hover { color: #e6edf3; }
#bottomTabActive {
    color: #a78bfa;
    border-bottom: 2px solid #7c3aed;
    font-weight: 600;
}

#bottomDrawerHandle {
    background-color: rgba(33, 38, 45, 140);
    border: 1px solid rgba(255, 255, 255, 16);
    border-radius: 9px;
    color: #8b949e;
    padding: 0px;
    font-size: 12px;
}
#bottomDrawerHandle:hover {
    background-color: rgba(48, 54, 61, 170);
    color: #e6edf3;
}

#bottomDrawerPreview {
    color: #8b949e;
    background: transparent;
    padding: 6px 2px 2px 2px;
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

#prevButton {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 16px;
}
#prevButton:hover {
    background-color: #30363d;
}
#prevButton:disabled {
    color: #6b7280;
    border-color: #2a2f3a;
    background-color: #1b202a;
}

#panelCard {
    background-color: #0f1523;
    border: 1px solid #21262d;
    border-radius: 14px;
}

#focusPanel {
    background-color: #0a101b;
    border-left: 1px solid #21262d;
}

/* ─── Icon Rail (Focus Mode) ────────────────────────────── */
#iconRail {
    background-color: #0f1523;
    border-right: 1px solid #21262d;
}
#railIcon {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    color: #8b949e;
    font-size: 18px;
    padding: 0px;
}
#railIcon:hover {
    background-color: #21262d;
    color: #e6edf3;
}

/* ─── Analytics View ─────────────────────────────────────── */
#analyticsView {
    background-color: #0a101b;
}
#analyticsScroll, #weeklyChart { background: transparent; border: none; }
#analyticsView QLabel { background: transparent; }

#backButton {
    background-color: rgba(18, 29, 48, 180);
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 10px;
    color: #eef4ff;
    padding: 7px 12px;
    font-weight: 700;
}
#backButton:hover {
    background-color: rgba(21, 34, 56, 210);
    border-color: #5f7dff;
}
#pageTitle {
    font-size: 24px;
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
    background-color: #0f1523;
    border: 1px solid #202b43;
    border-radius: 12px;
}
#statCard QLabel { background: transparent; }
#statTitle {
    font-size: 12px;
    color: #8ea0c4;
    font-weight: 600;
}
#statValue {
    font-size: 28px;
    font-weight: 700;
    color: #e6edf3;
}
#statSubtitle {
    font-size: 11px;
    color: #8ea2ff;
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
#lessonTree::item:selected { background-color: #ede9fe; color: #5b21b6; }
#lessonTree::item:hover:!selected { background-color: #eaeef2; }
#lessonTree::branch { background-color: transparent; }

#videoControls { background-color: #f6f8fa; border-top: 1px solid #d0d7de; }
#playButton { background-color: #7c3aed; color: #fff; border: none; border-radius: 16px; font-size: 15px; font-weight: bold; padding: 0px; }
#playButton:hover { background-color: #6d28d9; }

#transportButton { background-color: #eaeef2; color: #656d76; border: 1px solid #d0d7de; border-radius: 14px; font-size: 11px; padding: 0px; }
#transportButton:hover { background-color: #d8dee4; color: #1f2328; border-color: #afb8c1; }
#transportButton:pressed { background-color: #ced5dc; }
#transportButton:focus { outline: none; border-color: #afb8c1; }

QPushButton {
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 14px;
}
QPushButton:hover { background-color: #eaeef2; }

#timeLabel { color: #656d76; font-size: 12px; font-family: "Consolas", monospace; background: transparent; border: none; }

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
#pomodoroTime { font-size: 40px; font-weight: 300; color: #1f2328; font-family: "Consolas", monospace; }
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
#dashTopBar { background-color: #f6f8fa; border-bottom: 1px solid #d0d7de; }
#breadcrumbLabel { color: #656d76; font-size: 13px; }
#streakChip { background-color: #ffffff; border: 1px solid #d0d7de; border-radius: 10px; padding: 6px 10px; color: #1f2328; }
#focusToggle { background-color: #ffffff; border: 1px solid #d0d7de; border-radius: 10px; padding: 6px 10px; }
#focusToggle:hover { background-color: #eaeef2; }
#panelCard { background-color: #ffffff; border: 1px solid #d0d7de; border-radius: 14px; }
#focusPanel { background-color: #ffffff; border-left: 1px solid #d0d7de; }
#iconRail { background-color: #f6f8fa; border-right: 1px solid #d0d7de; }
#railIcon { background: transparent; border: none; border-radius: 10px; color: #656d76; font-size: 18px; padding: 0px; }
#railIcon:hover { background-color: #eaeef2; color: #1f2328; }
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
