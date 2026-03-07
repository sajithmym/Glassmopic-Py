"""Custom frameless title bar for Glassmopic with glow effects."""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import (
    Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QAbstractAnimation, QSequentialAnimationGroup, QTimer
)
from PyQt5.QtGui import QFont, QColor, QMouseEvent


class TitleBar(QWidget):
    """Draggable custom title bar with minimize / maximize / close buttons."""

    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(52)
        self._drag_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 10, 0)
        layout.setSpacing(10)

        # App icon / logo dot with glow
        self._logo = QLabel("●")
        self._logo.setObjectName("TitleLogo")
        self._logo.setFont(QFont("Segoe UI", 16))
        self._logo.setStyleSheet("color: #6C63FF; background: transparent;")
        logo_glow = QGraphicsDropShadowEffect(self._logo)
        logo_glow.setBlurRadius(20)
        logo_glow.setOffset(0, 0)
        logo_glow.setColor(QColor(108, 99, 255, 120))
        self._logo.setGraphicsEffect(logo_glow)
        layout.addWidget(self._logo)

        # Title label
        self._title_label = QLabel("Glassmopic Todo")
        self._title_label.setObjectName("TitleLabel")
        self._title_label.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
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
