"""Custom frameless title bar for Glassmopic."""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QMouseEvent


class TitleBar(QWidget):
    """Draggable custom title bar with minimize / maximize / close buttons."""

    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(48)
        self._drag_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)

        # App icon / logo dot
        logo = QLabel("●")
        logo.setObjectName("TitleLogo")
        logo.setFont(QFont("Segoe UI", 14))
        logo.setStyleSheet("color: #6C63FF;")
        layout.addWidget(logo)

        # Title label
        self._title_label = QLabel("Glassmopic Todo")
        self._title_label.setObjectName("TitleLabel")
        self._title_label.setFont(QFont("Segoe UI Semibold", 11))
        layout.addWidget(self._title_label)

        layout.addStretch()

        # Stats label (updated externally)
        self._stats_label = QLabel("")
        self._stats_label.setObjectName("StatsLabel")
        self._stats_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self._stats_label)

        # Window control buttons
        for symbol, name, signal in [
            ("—", "MinBtn", self.minimize_clicked),
            ("◻", "MaxBtn", self.maximize_clicked),
            ("✕", "CloseBtn", self.close_clicked),
        ]:
            btn = QPushButton(symbol)
            btn.setObjectName(name)
            btn.setFixedSize(36, 36)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn)

    # --- public helpers ---

    def set_stats_text(self, text: str) -> None:
        self._stats_label.setText(text)

    # --- dragging ---

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.maximize_clicked.emit()
