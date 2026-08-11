from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QTabWidget,
    QDockWidget
)

from core.compiler import Compiler
from core.runner import ProgramRunner
from core.workspace import WorkspaceError, WorkspaceManager
from core.setting import SettingManager

from browser.codeforces import CodeforcesBrowser
from browser.lqdoj import LqdojBrowser
from browser.vnoi import VnoiBrowser
from browser.google import GoogleBrowser

from ui.code_editor import CodeEditor
from ui.menu_bar import MenuBar
from ui.setting_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BiCP")
        self.resize(1100, 720)
        self.setMinimumSize(500, 300)

        self.workspace = WorkspaceManager()
        self.compiler = Compiler()
        self.runner = ProgramRunner(self.workspace, self.compiler)
        self.settings = SettingManager()
        self.settings.load()

        self.menu = MenuBar(self)
        self.editor = CodeEditor()
        self.input_box = QPlainTextEdit()
        self.output_box = QPlainTextEdit()
        self.find_box = QLineEdit()

        self.run_button = QPushButton("Run")
        # self.rebuild_button = QPushButton("Rebuild")
        self.stop_button = QPushButton("Stop")

        self.codeforces_dock = None
        self.codeforces_browser = None

        self.lqdoj_dock = None
        self.lqdoj_browser = None

        self.vnoi_dock = None
        self.vnoi_browser = None

        self.google_dock = None
        self.google_browser = None

        self.current_lang = self.settings.get("language")

        self._build_ui()
        self._connect_signals()
        self._apply_runtime_settings()
        self._load_workspace()
        self._apply_styles()
        self.setMenuBar(self.menu)

        self.menu.cpp_action.triggered.connect(
            lambda: self.change_language("cpp")
        )

        self.menu.python_action.triggered.connect(
            lambda: self.change_language("python")
        )

        self.menu.save_action.triggered.connect(
            self._save_as
        )

        self.menu.setting_action.triggered.connect(self._show_settings)

        self.menu.codeforces_action.triggered.connect(self._open_codeforces)
        self.menu.lqdoj_action.triggered.connect(self._open_lqdoj)
        self.menu.vnoi_action.triggered.connect(self._open_vnoi)
        self.menu.google_action.triggered.connect(self._open_google)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(8)
        toolbar_layout.addWidget(QLabel("BiCP"))
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.run_button)
        # toolbar_layout.addWidget(self.rebuild_button)
        toolbar_layout.addWidget(self.stop_button)
        main_layout.addWidget(toolbar)

        self.find_box.setPlaceholderText("Find")
        self.find_box.hide()
        main_layout.addWidget(self.find_box)

        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("Program output will appear here.")
        self.input_box.setPlaceholderText("Input")

        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.addWidget(self._panel("INPUT", self.input_box))
        bottom_splitter.addWidget(self._panel("OUTPUT", self.output_box))
        bottom_splitter.setSizes([420, 680])

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(self.editor)
        top_splitter.setSizes([1000])

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_splitter)
        main_splitter.setSizes([520, 200])
        main_layout.addWidget(main_splitter)

        self.stop_button.setEnabled(False)

    def _panel(self, title: str, widget: QWidget) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)
        label = QLabel(title)
        layout.addWidget(label)
        layout.addWidget(widget)
        return panel

    def _connect_signals(self) -> None:
        self.run_button.clicked.connect(lambda: self._run(force_rebuild=False))
        # self.rebuild_button.clicked.connect(lambda: self._run(force_rebuild=True))
        self.stop_button.clicked.connect(self.runner.stop)
        self.runner.output_changed.connect(self.output_box.setPlainText)
        self.runner.busy_changed.connect(self._set_busy)
        self.editor.save_requested.connect(self._save_code)
        self.editor.find_requested.connect(self._show_find)
        self.find_box.returnPressed.connect(self._find_next)
        self.find_box.textChanged.connect(lambda _text: self._find_next())

    def _load_workspace(self) -> None:
        try:
            self.workspace.ensure()
            self.workspace.set_language(self.current_lang)

            # Mỗi lần mở BiCP → tạo code mặc định mới
            self.editor.setPlainText(
                self.workspace.get_default_code()
            )

            self.editor.document().setModified(False)

            self.input_box.setPlainText(
                self.workspace.load_input()
            )

        except WorkspaceError as exc:
            self.output_box.setPlainText(
                f"Workspace error\n\n{exc}"
            )
            
    def _run(self, force_rebuild: bool) -> None:
        self.runner.run(
            self.editor.toPlainText(),
            self.input_box.toPlainText(),
            force_rebuild=force_rebuild,
        )

    def _save_code(self) -> None:

        try:

            self.workspace.set_language(
                self.current_lang
            )

            self.workspace.save_code(
                self.editor.toPlainText()
            )

            self.output_box.setPlainText(
                f"Saved: "
                f"{self.workspace.get_source_path()}"
            )

        except WorkspaceError as exc:

            self.output_box.setPlainText(
                f"Workspace error\n\n{exc}"
            )

    def _save_as(self) -> None:
        if self.current_lang == "cpp":
            default_name = "main.cpp"
            file_filter = "C++ Source (*.cpp);;All Files (*)"

        elif self.current_lang == "python":
            default_name = "main.py"
            file_filter = "Python Files (*.py);;All Files (*)"

        else:
            default_name = "main.txt"
            file_filter = "All Files (*)"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            default_name,
            file_filter
        )

        # Người dùng bấm Cancel
        if not file_path:
            return

        try:

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    self.editor.toPlainText()
                )

            self.setWindowTitle(
                f"BiCP - {file_path}"
            )

            self.editor.document().setModified(
                False
            )

            self.output_box.setPlainText(
                f"Saved:\n{file_path}"
            )

        except OSError as exc:

            self.output_box.setPlainText(
                f"Could not save file:\n\n{exc}"
            )

    def _show_find(self) -> None:
        self.find_box.show()
        self.find_box.setFocus()
        self.find_box.selectAll()

    def _find_next(self) -> None:
        text = self.find_box.text()
        if not text:
            return

        if self.editor.find(text):
            return

        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.setTextCursor(cursor)
        self.editor.find(text)

    def _set_busy(self, busy: bool) -> None:
        self.run_button.setEnabled(not busy)
        # self.rebuild_button.setEnabled(not busy)
        self.stop_button.setEnabled(busy)

    def _apply_runtime_settings(self) -> None:
        self.current_lang = self.settings.get("language", "cpp")

        self.editor.configure_editor(
            self.settings.get_int("font_size", 14),
            self.settings.get_int("tab_size", 4),
        )

        self.compiler.configure(
            self.settings.get("cpp_compiler", "g++") or "g++",
            self.settings.get("cpp_standard", "c++20"),
            self.settings.get("cpp_optimization", "O0"),
        )

        self.runner.configure(
            self.settings.get_int("run_timeout_ms", 3000),
            self.settings.get("python_interpreter"),
        )

        self.workspace.set_default_code(
            "cpp",
            self.settings.get("default_cpp"),
        )
        self.workspace.set_default_code(
            "python",
            self.settings.get("default_python"),
        )

    def _apply_styles(self) -> None:
        if self.settings.get("theme", "dark") == "light":
            self.setStyleSheet(
                """
                QMainWindow, QWidget {
                    background: #f4f6f8;
                    color: #1d2630;
                }
                QLabel {
                    color: #394656;
                    font-weight: 600;
                }
                QPushButton {
                    background: #ffffff;
                    border: 1px solid #c8d0da;
                    border-radius: 4px;
                    color: #1d2630;
                    min-height: 30px;
                    padding: 0 14px;
                }
                QPushButton:hover {
                    background: #e9eef4;
                }
                QPushButton:disabled {
                    color: #99a3af;
                    background: #edf1f5;
                }
                QPlainTextEdit, QLineEdit {
                    background: #ffffff;
                    border: 1px solid #c8d0da;
                    border-radius: 4px;
                    color: #1d2630;
                    selection-background-color: #bfd8f4;
                }
                QSplitter::handle {
                    background: #d5dde7;
                }
                """
            )
            return

        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #101418;
                color: #d7dde5;
            }
            QLabel {
                color: #aeb7c2;
                font-weight: 600;
            }
            QPushButton {
                background: #26313d;
                border: 1px solid #3b4654;
                border-radius: 4px;
                color: #eef3f8;
                min-height: 30px;
                padding: 0 14px;
            }
            QPushButton:hover {
                background: #314052;
            }
            QPushButton:disabled {
                color: #6f7884;
                background: #1b222b;
            }
            QPlainTextEdit, QLineEdit {
                background: #151a20;
                border: 1px solid #2a333d;
                border-radius: 4px;
                color: #e5e9ef;
                selection-background-color: #35516d;
            }
            QSplitter::handle {
                background: #242c35;
            }
            """
        )
    def change_language(self, language: str, persist: bool = True) -> None:
        if self.runner.is_busy():
            self.output_box.setPlainText(
                "A program is currently running.\n"
                "Stop it before changing language."
            )
            return

        if language == self.current_lang:
            return

        try:
            # ==============================
            # Lưu code hiện tại
            # ==============================

            self.workspace.set_language(
                self.current_lang
            )

            self.workspace.save_code(
                self.editor.toPlainText()
            )

            # ==============================
            # Đổi language
            # ==============================

            self.workspace.set_language(
                language
            )

            # ==============================
            # Dùng DEFAULT_CODE
            # ==============================

            self.editor.setPlainText(
                self.workspace.get_default_code()
            )

            self.current_lang = language

            if persist:
                self.settings.set("language", language)
                self.settings.save()

            self.editor.document().setModified(
                False
            )

            self.output_box.clear()

        except WorkspaceError as exc:

            self.output_box.setPlainText(
                f"Workspace error\n\n{exc}"
            )

    def _show_settings(self) -> None:
        old_language = self.current_lang
        dialog = SettingsDialog(self.settings, self)

        if dialog.exec():
            new_language = self.settings.get("language", "cpp")
            self._apply_runtime_settings()
            self._apply_styles()

            if new_language != old_language:
                self.current_lang = old_language
                self.change_language(new_language, persist=False)

            self.output_box.setPlainText(
                "Settings applied."
            )
    def _open_codeforces(self) -> None:
        if self.codeforces_dock is None:

            self.codeforces_dock = QDockWidget(
                "Codeforces",
                self
            )

            self.codeforces_dock.setAllowedAreas(
                Qt.LeftDockWidgetArea |
                Qt.RightDockWidgetArea
            )

            self.codeforces_browser = CodeforcesBrowser()

            self.codeforces_dock.setWidget(
                self.codeforces_browser
            )

            self.addDockWidget(
                Qt.RightDockWidgetArea,
                self.codeforces_dock
            )

        self.codeforces_dock.show()
        self.codeforces_dock.raise_()

    def _open_lqdoj(self) -> None:
        if self.lqdoj_dock is None:

            self.lqdoj_dock = QDockWidget(
                "Lqdoj",
                self
            )

            self.lqdoj_dock.setAllowedAreas(
                Qt.LeftDockWidgetArea |
                Qt.RightDockWidgetArea
            )

            self.lqdoj_browser = LqdojBrowser()

            self.lqdoj_dock.setWidget(
                self.lqdoj_browser
            )

            self.addDockWidget(
                Qt.RightDockWidgetArea,
                self.lqdoj_dock
            )

        self.lqdoj_dock.show()
        self.lqdoj_dock.raise_()

    def _open_vnoi(self) -> None:
        if self.vnoi_dock is None:

            self.vnoi_dock = QDockWidget(
                "VNOI",
                self
            )

            self.vnoi_dock.setAllowedAreas(
                Qt.LeftDockWidgetArea |
                Qt.RightDockWidgetArea
            )

            self.vnoi_browser = VnoiBrowser()

            self.vnoi_dock.setWidget(
                self.vnoi_browser
            )

            self.addDockWidget(
                Qt.RightDockWidgetArea,
                self.vnoi_dock
            )

        self.vnoi_dock.show()
        self.vnoi_dock.raise_()

    def _open_google(self) -> None:
        if self.google_dock is None:

            self.google_dock = QDockWidget(
                "Google",
                self
            )

            self.google_dock.setAllowedAreas(
                Qt.LeftDockWidgetArea |
                Qt.RightDockWidgetArea
            )

            self.google_browser = GoogleBrowser()

            self.google_dock.setWidget(
                self.google_browser
            )

            self.addDockWidget(
                Qt.RightDockWidgetArea,
                self.google_dock
            )

        self.google_dock.show()
        self.google_dock.raise_()