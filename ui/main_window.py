from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
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
    QFileDialog
)

from core.compiler import Compiler
from core.runner import ProgramRunner
from core.version import VERSION
from core.workspace import WorkspaceError, WorkspaceManager
from ui.code_editor import CodeEditor
from ui.menu_bar import MenuBar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"BiCP v{VERSION}")
        self.resize(1100, 720)
        self.setMinimumSize(760, 460)

        self.current_lang = "cpp"

        self.workspace = WorkspaceManager()
        self.compiler = Compiler()
        self.runner = ProgramRunner(self.workspace, self.compiler)

        self.menu = MenuBar(self)
        self.editor = CodeEditor()
        self.input_box = QPlainTextEdit()
        self.output_box = QPlainTextEdit()
        self.find_box = QLineEdit()

        self.run_button = QPushButton("Run")
        self.rebuild_button = QPushButton("Rebuild")
        self.stop_button = QPushButton("Stop")

        self._build_ui()
        self._connect_signals()
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
            self._save_code
        )

        self.menu.save_as_action.triggered.connect(
            self._save_as
        )

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
        toolbar_layout.addWidget(self.rebuild_button)
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
        self.rebuild_button.clicked.connect(lambda: self._run(force_rebuild=True))
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
        self.rebuild_button.setEnabled(not busy)
        self.stop_button.setEnabled(busy)

    def _apply_styles(self) -> None:
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
    def change_language(self, language: str) -> None:
        if self.runner.is_busy():
            self.output_box.setPlainText(
                "A program is currently running.\n"
                "Stop it before changing language."
            )
            return
        
        if language == self.current_lang:
            return

        try:
            # Lưu code của ngôn ngữ hiện tại
            self.workspace.set_language(
                self.current_lang
            )

            self.workspace.save_code(
                self.editor.toPlainText()
            )

            # Chuyển sang ngôn ngữ mới
            self.workspace.set_language(
                language
            )

            # Load code của ngôn ngữ mới
            self.editor.setPlainText(
                self.workspace.load_code()
            )

            self.current_lang = language

            self.output_box.setPlainText(
                f"Switched to {language.upper()}"
            )

        except WorkspaceError as exc:

            self.output_box.setPlainText(
                f"Workspace error\n\n{exc}"
            )
