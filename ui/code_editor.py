from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802
        self.code_editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    save_requested = Signal()
    find_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.line_number_area = LineNumberArea(self)

        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(11)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

        self.blockCountChanged.connect(self.update_line_number_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self._install_shortcuts()
        self.update_line_number_width(0)
        self.highlight_current_line()

    def configure_editor(
        self,
        font_size: int,
        tab_size: int,
    ) -> None:

        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)
        self.setTabStopDistance(tab_size * self.fontMetrics().horizontalAdvance(" "))
        self.update_line_number_width(0)

    def _install_shortcuts(self) -> None:
        find_action = QAction("Find", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find_requested.emit)
        self.addAction(find_action)

    def line_number_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_width(self, _block_count: int) -> None:
        self.setViewportMargins(self.line_number_width(), 0, 0, 0)

    def update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height(),
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_width(0)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        contents = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                contents.left(),
                contents.top(),
                self.line_number_width(),
                contents.height(),
            )
        )

    def highlight_current_line(self) -> None:
        selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#252a31"))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)
        self.setExtraSelections(selections)

    def paint_line_numbers(self, event) -> None:
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#171b20"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor("#8a939f"))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    str(block_number + 1),
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
