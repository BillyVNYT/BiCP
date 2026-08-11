from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.setting import SettingManager


class SettingsDialog(QDialog):
    def __init__(self, settings: SettingManager, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings

        self.setWindowTitle("Settings")
        self.resize(820, 560)

        self._build_ui()
        self._load_values()
        self._connect_signals()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(160)
        self.list_widget.addItems(["General", "Editor", "C++", "Python", "Run"])

        self.pages = QStackedWidget()
        self.pages.addWidget(self._create_general_page())
        self.pages.addWidget(self._create_editor_page())
        self.pages.addWidget(self._create_cpp_page())
        self.pages.addWidget(self._create_python_page())
        self.pages.addWidget(self._create_run_page())

        content_layout.addWidget(self.list_widget)
        content_layout.addWidget(self.pages)
        main_layout.addLayout(content_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.apply_button = QPushButton("Apply")
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        main_layout.addLayout(button_layout)

        self.list_widget.setCurrentRow(0)

    def _connect_signals(self) -> None:
        self.list_widget.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)

    def _create_general_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self._title("General"))

        form = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.language_combo = QComboBox()
        self.language_combo.addItems(["cpp", "python"])
        form.addRow("Theme:", self.theme_combo)
        form.addRow("Default language:", self.language_combo)
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _create_editor_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self._title("Editor"))

        form = QFormLayout()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        self.tab_size_spin = QSpinBox()
        self.tab_size_spin.setRange(1, 12)
        form.addRow("Font size:", self.font_size_spin)
        form.addRow("Tab size:", self.tab_size_spin)
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _create_cpp_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self._title("C++"))

        form = QFormLayout()
        self.cpp_compiler_edit = QLineEdit()
        self.cpp_standard_combo = QComboBox()
        self.cpp_standard_combo.addItems(["c++17", "c++20", "c++23"])
        self.cpp_optimization_combo = QComboBox()
        self.cpp_optimization_combo.addItems(["O0", "O1", "O2", "O3"])
        form.addRow("Compiler:", self.cpp_compiler_edit)
        form.addRow("Standard:", self.cpp_standard_combo)
        form.addRow("Optimization:", self.cpp_optimization_combo)
        layout.addLayout(form)

        layout.addWidget(QLabel("DEFAULT_CPP"))
        self.default_cpp_edit = QPlainTextEdit()
        self.default_cpp_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        layout.addWidget(self.default_cpp_edit)
        return page

    def _create_python_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self._title("Python"))

        form = QFormLayout()
        self.python_interpreter_edit = QLineEdit()
        self.python_interpreter_edit.setPlaceholderText("Leave empty to use current Python")
        form.addRow("Interpreter:", self.python_interpreter_edit)
        layout.addLayout(form)

        layout.addWidget(QLabel("DEFAULT_PYTHON"))
        self.default_python_edit = QPlainTextEdit()
        self.default_python_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        layout.addWidget(self.default_python_edit)
        return page

    def _create_run_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self._title("Run"))

        form = QFormLayout()
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(100, 60000)
        self.timeout_spin.setSingleStep(100)
        self.timeout_spin.setSuffix(" ms")
        form.addRow("Timeout:", self.timeout_spin)
        layout.addLayout(form)
        layout.addStretch()
        return page

    def _title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 20px; font-weight: bold;")
        return label

    def _load_values(self) -> None:
        self.theme_combo.setCurrentText(self.settings.get("theme"))
        self.language_combo.setCurrentText(self.settings.get("language"))
        self.font_size_spin.setValue(self.settings.get_int("font_size", 14))
        self.tab_size_spin.setValue(self.settings.get_int("tab_size", 4))
        self.cpp_compiler_edit.setText(self.settings.get("cpp_compiler"))
        self.cpp_standard_combo.setCurrentText(self.settings.get("cpp_standard"))
        self.cpp_optimization_combo.setCurrentText(self.settings.get("cpp_optimization"))
        self.timeout_spin.setValue(self.settings.get_int("run_timeout_ms", 3000))
        self.python_interpreter_edit.setText(self.settings.get("python_interpreter"))
        self.default_cpp_edit.setPlainText(self.settings.get("default_cpp"))
        self.default_python_edit.setPlainText(self.settings.get("default_python"))

    def accept(self) -> None:
        self.settings.set("theme", self.theme_combo.currentText())
        self.settings.set("language", self.language_combo.currentText())
        self.settings.set("font_size", self.font_size_spin.value())
        self.settings.set("tab_size", self.tab_size_spin.value())
        self.settings.set("cpp_compiler", self.cpp_compiler_edit.text().strip() or "g++")
        self.settings.set("cpp_standard", self.cpp_standard_combo.currentText())
        self.settings.set("cpp_optimization", self.cpp_optimization_combo.currentText())
        self.settings.set("run_timeout_ms", self.timeout_spin.value())
        self.settings.set("python_interpreter", self.python_interpreter_edit.text().strip())
        self.settings.set("default_cpp", self.default_cpp_edit.toPlainText())
        self.settings.set("default_python", self.default_python_edit.toPlainText())
        self.settings.save()
        super().accept()
