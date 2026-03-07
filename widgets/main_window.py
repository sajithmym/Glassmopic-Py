"""Frameless main window with glassmorphism effect and rounded corners."""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QAbstractAnimation, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath, QLinearGradient, QRadialGradient

from widgets.title_bar import TitleBar
from widgets.todo_panel import TodoPanel


class MainWindow(QMainWindow):
    """Single frameless window with rounded corners and glass background."""

    BORDER_RADIUS = 18

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glassmopic Todo")
        self.setMinimumSize(480, 600)
        self.resize(620, 800)

        # Frameless + translucent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._is_maximized = False

        # Central wrapper
        central = QWidget()
        central.setObjectName("CentralBg")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Title bar
        self._title_bar = TitleBar(self)
        self._title_bar.minimize_clicked.connect(self.showMinimized)
        self._title_bar.maximize_clicked.connect(self._toggle_maximize)
        self._title_bar.close_clicked.connect(self.close)
        root.addWidget(self._title_bar)

        # Todo panel
        self._todo_panel = TodoPanel(self)
        self._todo_panel.stats_changed.connect(self._title_bar.set_stats_text)
        root.addWidget(self._todo_panel, stretch=1)

        # Drop shadow on the whole window
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        central.setGraphicsEffect(shadow)

    # --- rounded painting ---

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        r = self.BORDER_RADIUS if not self._is_maximized else 0
        w, h = self.width(), self.height()
        path.addRoundedRect(0, 0, w, h, r, r)

        # Deep gradient background
        bg = QLinearGradient(0, 0, w * 0.3, h)
        bg.setColorAt(0.0, QColor(18, 18, 32, 248))
        bg.setColorAt(0.35, QColor(14, 14, 26, 252))
        bg.setColorAt(0.7, QColor(18, 18, 30, 250))
        bg.setColorAt(1.0, QColor(12, 12, 24, 252))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg))
        painter.drawPath(path)

        # Subtle accent glow at top-center
        glow = QRadialGradient(w * 0.5, 0, w * 0.5)
        glow.setColorAt(0.0, QColor(108, 99, 255, 18))
        glow.setColorAt(0.5, QColor(108, 99, 255, 6))
        glow.setColorAt(1.0, QColor(108, 99, 255, 0))
        painter.setBrush(QBrush(glow))
        painter.drawPath(path)

        # Border glow
        border_pen = QPen(QColor(108, 99, 255, 45), 1.2)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.end()

    # --- maximize toggle ---

    def _toggle_maximize(self) -> None:
        if self._is_maximized:
            self.showNormal()
            self._is_maximized = False
        else:
            self.showMaximized()
            self._is_maximized = True

    # --- resize handles (8px border) ---

    _GRIP = 8

    def _edge_at(self, pos):
        x, y, w, h = pos.x(), pos.y(), self.width(), self.height()
        g = self._GRIP
        edges = Qt.Edges()
        if x < g:
            edges |= Qt.LeftEdge
        if x > w - g:
            edges |= Qt.RightEdge
        if y < g:
            edges |= Qt.TopEdge
        if y > h - g:
            edges |= Qt.BottomEdge
        return edges

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and not self._is_maximized:
            edges = self._edge_at(event.pos())
            if edges:
                self.windowHandle().startSystemResize(edges)
                event.accept()
                return
        super().mousePressEvent(event)
