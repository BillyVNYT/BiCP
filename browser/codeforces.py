from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWebEngineWidgets import QWebEngineView


class CodeforcesBrowser(QWebEngineView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.current_zoom = 1.0

        self.zoom_timer = QTimer(self)
        self.zoom_timer.setInterval(16)  # ~60 FPS
        self.zoom_timer.timeout.connect(
            self.update_zoom
        )

        self.setZoomFactor(
            self.current_zoom
        )

        self.setUrl(
            QUrl("https://codeforces.com/")
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not self.zoom_timer.isActive():
            self.zoom_timer.start()

    def update_zoom(self):

        width = self.width()

        target_zoom = width / 1000.0

        target_zoom = max(
            0.5,
            min(1.0, target_zoom)
        )

        # Nội suy để zoom mượt
        self.current_zoom += (
            target_zoom - self.current_zoom
        ) * 0.25

        self.setZoomFactor(
            self.current_zoom
        )

        # Khi gần đạt target thì dừng
        if abs(
            target_zoom - self.current_zoom
        ) < 0.001:

            self.current_zoom = target_zoom

            self.setZoomFactor(
                target_zoom
            )

            self.zoom_timer.stop()