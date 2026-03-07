"""Individual todo item card widget."""

from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QSizePolicy, QGraphicsDropShadowEffect, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor


PRIORITY_COLORS = {
    "Critical": "#FF4757",
    "High": "#FF6B6B",
    "Medium": "#FFA502",
    "Low": "#2ED573",
}


class TodoItemWidget(QFrame):
    """A single todo card with checkbox, info, and action buttons."""

    toggled = pyqtSignal(int, bool)       # (id, completed)
    edit_requested = pyqtSignal(int)       # (id)
    delete_requested = pyqtSignal(int)     # (id)

    def __init__(self, todo: dict, parent=None):
        super().__init__(parent)
        self.todo = todo
        self.setObjectName("TodoCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(72)

        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

        self._build_ui()
        self._apply_completed_style()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        # Priority bar
        pri_bar = QWidget()
        pri_bar.setFixedWidth(4)
        color = PRIORITY_COLORS.get(self.todo["priority"], "#FFA502")
        pri_bar.setStyleSheet(f"background: {color}; border-radius: 2px;")
        root.addWidget(pri_bar)

        # Checkbox
        self._check = QCheckBox()
        self._check.setChecked(bool(self.todo["completed"]))
        self._check.stateChanged.connect(self._on_toggle)
        root.addWidget(self._check)

        # Text column
        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        self._title = QLabel(self.todo["title"])
        self._title.setObjectName("TodoTitle")
        self._title.setFont(QFont("Segoe UI Semibold", 11))
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
            desc.setMaximumHeight(40)
            text_col.addWidget(desc)

        root.addLayout(text_col, stretch=1)

        # Action buttons
        btn_col = QVBoxLayout()
        btn_col.setSpacing(4)

        edit_btn = QPushButton("✎")
        edit_btn.setObjectName("EditBtn")
        edit_btn.setFixedSize(30, 30)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Edit")
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.todo["id"]))
        btn_col.addWidget(edit_btn)

        del_btn = QPushButton("🗑")
        del_btn.setObjectName("DeleteBtn")
        del_btn.setFixedSize(30, 30)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.todo["id"]))
        btn_col.addWidget(del_btn)

        root.addLayout(btn_col)

    def _on_toggle(self, state: int) -> None:
        self.toggled.emit(self.todo["id"], state == Qt.Checked)
        self._apply_completed_style()

    def _apply_completed_style(self) -> None:
        completed = self._check.isChecked()
        opacity = "0.55" if completed else "1.0"
        strike = "line-through" if completed else "none"
        self._title.setStyleSheet(f"opacity: {opacity}; text-decoration: {strike};")
        if completed:
            self._title.setStyleSheet("color: #888; text-decoration: line-through;")
        else:
            self._title.setStyleSheet("")
