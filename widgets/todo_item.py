"""Individual todo item card widget with animations."""

from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QSizePolicy, QGraphicsDropShadowEffect, QWidget,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QPoint
from PyQt5.QtGui import QFont, QColor

from widgets.animations import ShadowAnimator, animate_shadow


PRIORITY_COLORS = {
    "Critical": "#FF4757",
    "High": "#FF6B6B",
    "Medium": "#FFA502",
    "Low": "#2ED573",
}

PRIORITY_GLOW = {
    "Critical": QColor(255, 71, 87, 55),
    "High": QColor(255, 107, 107, 40),
    "Medium": QColor(255, 165, 2, 30),
    "Low": QColor(46, 213, 115, 30),
}


class TodoItemWidget(QFrame):
    """A single todo card with checkbox, info, and action buttons + hover animation."""

    toggled = pyqtSignal(int, bool)       # (id, completed)
    edit_requested = pyqtSignal(int)       # (id)
    delete_requested = pyqtSignal(int)     # (id)

    def __init__(self, todo: dict, parent=None):
        super().__init__(parent)
        self.todo = todo
        self.setObjectName("TodoCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(76)
        self.setCursor(Qt.PointingHandCursor)

        # Shadow with priority-tinted glow
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(16)
        self._shadow.setOffset(0, 3)
        glow_color = PRIORITY_GLOW.get(todo.get("priority", "Medium"), QColor(0, 0, 0, 35))
        self._shadow.setColor(glow_color)
        self.setGraphicsEffect(self._shadow)

        # Shadow animator for hover
        self._shadow_anim = ShadowAnimator(self._shadow, self)
        self._hover_anim = None

        self._build_ui()
        self._apply_completed_style()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(12)

        # Priority bar (gradient pill)
        pri_bar = QWidget()
        pri_bar.setFixedSize(4, 40)
        color = PRIORITY_COLORS.get(self.todo["priority"], "#FFA502")
        pri_bar.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {color}, stop:1 rgba(108,99,255,0.3));"
            f"border-radius: 2px;"
        )
        root.addWidget(pri_bar)

        # Checkbox
        self._check = QCheckBox()
        self._check.setChecked(bool(self.todo["completed"]))
        self._check.stateChanged.connect(self._on_toggle)
        root.addWidget(self._check)

        # Text column
        text_col = QVBoxLayout()
        text_col.setSpacing(3)

        self._title = QLabel(self.todo["title"])
        self._title.setObjectName("TodoTitle")
        self._title.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
        self._title.setWordWrap(True)
        text_col.addWidget(self._title)

        meta_parts = []
        if self.todo.get("category"):
            meta_parts.append(f"📁 {self.todo['category']}")
        if self.todo.get("priority"):
            meta_parts.append(f"⚡ {self.todo['priority']}")
        if self.todo.get("due_date"):
            meta_parts.append(f"📅 {self.todo['due_date']}")

        if meta_parts:
            meta = QLabel("   ".join(meta_parts))
            meta.setObjectName("TodoMeta")
            meta.setFont(QFont("Segoe UI", 8))
            text_col.addWidget(meta)

        if self.todo.get("description"):
            desc = QLabel(self.todo["description"])
            desc.setObjectName("TodoDesc")
            desc.setFont(QFont("Segoe UI", 9))
            desc.setWordWrap(True)
            desc.setMaximumHeight(36)
            text_col.addWidget(desc)

        root.addLayout(text_col, stretch=1)

        # Action buttons
        btn_col = QVBoxLayout()
        btn_col.setSpacing(5)

        edit_btn = QPushButton("✎")
        edit_btn.setObjectName("EditBtn")
        edit_btn.setFixedSize(32, 32)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Edit")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.todo["id"]))
        btn_col.addWidget(edit_btn)

        del_btn = QPushButton("🗑")
        del_btn.setObjectName("DeleteBtn")
        del_btn.setFixedSize(32, 32)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.todo["id"]))
        btn_col.addWidget(del_btn)

        root.addLayout(btn_col)

    # --- hover animation ---

    def enterEvent(self, event) -> None:
        self._hover_anim = animate_shadow(self._shadow_anim, 28, 5, duration=220)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover_anim = animate_shadow(self._shadow_anim, 16, 3, duration=280)
        super().leaveEvent(event)

    # --- fade-in entrance animation ---

    def play_entrance(self, delay_ms: int = 0) -> None:
        """Animate card appearing with opacity + slide up."""
        opacity_fx = QGraphicsOpacityEffect(self)
        opacity_fx.setOpacity(0.0)
        self.setGraphicsEffect(opacity_fx)

        # Opacity anim
        self._entrance_opacity = QPropertyAnimation(opacity_fx, b"opacity", self)
        self._entrance_opacity.setDuration(380)
        self._entrance_opacity.setStartValue(0.0)
        self._entrance_opacity.setEndValue(1.0)
        self._entrance_opacity.setEasingCurve(QEasingCurve.OutCubic)

        # Slide anim
        start = self.pos()
        self._entrance_slide = QPropertyAnimation(self, b"pos", self)
        self._entrance_slide.setDuration(380)
        self._entrance_slide.setStartValue(QPoint(start.x(), start.y() + 20))
        self._entrance_slide.setEndValue(start)
        self._entrance_slide.setEasingCurve(QEasingCurve.OutCubic)

        # Restore shadow after entrance finished
        def _restore_shadow():
            glow_color = PRIORITY_GLOW.get(self.todo.get("priority", "Medium"), QColor(0, 0, 0, 35))
            self._shadow = QGraphicsDropShadowEffect(self)
            self._shadow.setBlurRadius(16)
            self._shadow.setOffset(0, 3)
            self._shadow.setColor(glow_color)
            self.setGraphicsEffect(self._shadow)
            self._shadow_anim = ShadowAnimator(self._shadow, self)

        self._entrance_opacity.finished.connect(_restore_shadow)

        from PyQt5.QtCore import QTimer
        QTimer.singleShot(delay_ms, self._entrance_opacity.start)
        QTimer.singleShot(delay_ms, self._entrance_slide.start)

    def _on_toggle(self, state: int) -> None:
        self.toggled.emit(self.todo["id"], state == Qt.Checked)
        self._apply_completed_style()

    def _apply_completed_style(self) -> None:
        completed = self._check.isChecked()
        if completed:
            self._title.setStyleSheet("color: #585B70; text-decoration: line-through; background: transparent;")
        else:
            self._title.setStyleSheet("color: #E0E0F8; background: transparent;")
