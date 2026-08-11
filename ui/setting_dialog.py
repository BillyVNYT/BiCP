from PySide6.QtWidgets import (
    QDialog,
    QListWidget,
    QStackedWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QComboBox,
)


class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.resize(700, 450)

        self._build_ui()
        self._connect_signals()

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self):

        main_layout = QVBoxLayout(self)

        # ================================================
        # Content
        # ================================================

        content_layout = QHBoxLayout()

        # --------------------------------
        # Left list
        # --------------------------------

        self.list_widget = QListWidget()

        self.list_widget.setFixedWidth(160)

        self.list_widget.addItems([
            "General",
            "Editor",
            "C++",
            "Python",
            "Run",
        ])

        # --------------------------------
        # Right pages
        # --------------------------------

        self.pages = QStackedWidget()

        self.pages.addWidget(
            self._create_general_page()
        )

        self.pages.addWidget(
            self._create_editor_page()
        )

        self.pages.addWidget(
            self._create_cpp_page()
        )

        self.pages.addWidget(
            self._create_python_page()
        )

        self.pages.addWidget(
            self._create_run_page()
        )

        content_layout.addWidget(
            self.list_widget
        )

        content_layout.addWidget(
            self.pages
        )

        main_layout.addLayout(
            content_layout
        )

        # ================================================
        # Buttons
        # ================================================

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.apply_button = QPushButton(
            "Apply"
        )

        button_layout.addWidget(
            self.cancel_button
        )

        button_layout.addWidget(
            self.apply_button
        )

        main_layout.addLayout(
            button_layout
        )

        # Mặc định chọn General
        self.list_widget.setCurrentRow(0)

    # =====================================================
    # SIGNALS
    # =====================================================

    def _connect_signals(self):

        self.list_widget.currentRowChanged.connect(
            self.pages.setCurrentIndex
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.apply_button.clicked.connect(
            self.accept
        )

    # =====================================================
    # PAGES
    # =====================================================

    def _create_general_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        title = QLabel("General")

        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        layout.addWidget(title)

        layout.addWidget(
            QLabel("General settings")
        )

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Dark",
            "Light",
        ])

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)

        layout.addLayout(theme_layout)

        layout.addStretch()

        return page

    # -----------------------------------------------------

    def _create_editor_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        title = QLabel("Editor")

        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        layout.addWidget(title)

        layout.addWidget(
            QLabel("Editor settings")
        )

        font_layout = QHBoxLayout()
        
        font_label = QLabel("Font size:")

        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "12",
            "14",
            "16",
            "18",
            "20",
        ])

        self.font_combo.setCurrentText("14")

        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)

        tab_space_layout = QHBoxLayout()
        tab_space_label = QLabel("Tab space:")

        self.tab_space_combo = QComboBox()
        self.tab_space_combo.addItems([
            "2",
            "3",
            "4",
            "5",
            "7",
            "8",
            "10",
            "12"
        ])

        self.tab_space_combo.setCurrentText("4")

        tab_space_layout.addWidget(tab_space_label)
        tab_space_layout.addWidget(self.tab_space_combo)

        layout.addLayout(font_layout)
        layout.addLayout(tab_space_layout)

        layout.addStretch()

        return page

    # -----------------------------------------------------

    def _create_cpp_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        title = QLabel("C++")

        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        layout.addWidget(title)

        layout.addWidget(
            QLabel("C++ compiler settings")
        )

        layout.addStretch()

        return page

    # -----------------------------------------------------

    def _create_python_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        title = QLabel("Python")

        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        layout.addWidget(title)

        layout.addWidget(
            QLabel("Python interpreter settings")
        )

        layout.addStretch()

        return page

    # -----------------------------------------------------

    def _create_run_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        title = QLabel("Run")

        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        layout.addWidget(title)

        layout.addWidget(
            QLabel("Run settings")
        )

        layout.addStretch()
        return page