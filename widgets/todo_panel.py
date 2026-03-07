"""Todo list panel — search, filter, add, and scrollable list of cards."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QScrollArea, QFrame, QLabel, QDialog,
    QFormLayout, QTextEdit, QDateEdit, QMessageBox, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTimer
from PyQt5.QtGui import QFont, QColor

import database as db
from widgets.todo_item import TodoItemWidget


class AddEditDialog(QDialog):
    """Modern glassmorphism dialog for adding or editing a todo."""

    def __init__(self, parent=None, todo: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Todo" if todo else "New Todo")
        self.setMinimumWidth(420)
        self.setObjectName("AddEditDialog")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            #DialogInner {
                background: qlineargradient(x1:0, y1:0, x2:0.3, y2:1,
                    stop:0 rgba(26, 26, 46, 0.98),
                    stop:1 rgba(18, 18, 32, 0.98));
                border: 1px solid rgba(108, 99, 255, 0.3);
                border-radius: 18px;
            }
            QLabel { color: #CDD6F4; font-size: 11px; background: transparent; }
            QLineEdit, QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 52, 0.95), stop:1 rgba(24, 24, 42, 0.95));
                color: #CDD6F4;
                border: 1px solid rgba(108, 99, 255, 0.18);
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 12px;
                selection-background-color: #6C63FF;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid rgba(108, 99, 255, 0.55);
            }
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 52, 0.95), stop:1 rgba(24, 24, 42, 0.95));
                color: #CDD6F4;
                border: 1px solid rgba(108, 99, 255, 0.18);
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 1px solid rgba(108, 99, 255, 0.4);
            }
            QComboBox::drop-down {
                border: none; width: 26px;
                border-left: 1px solid rgba(108, 99, 255, 0.1);
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QComboBox QAbstractItemView {
                background: #1A1A2E;
                color: #CDD6F4;
                border: 1px solid rgba(108, 99, 255, 0.3);
                border-radius: 8px;
                selection-background-color: rgba(108, 99, 255, 0.35);
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 6px;
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background: rgba(108, 99, 255, 0.2);
            }
            QDateEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 52, 0.95), stop:1 rgba(24, 24, 42, 0.95));
                color: #CDD6F4;
                border: 1px solid rgba(108, 99, 255, 0.18);
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 12px;
            }
            QDateEdit:focus {
                border: 1px solid rgba(108, 99, 255, 0.55);
            }
            #SaveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6C63FF, stop:0.5 #7E6FFF, stop:1 #A78BFA);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 28px;
                font-weight: bold;
                font-size: 12px;
            }
            #SaveBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7C73FF, stop:0.5 #9080FF, stop:1 #B79CFA);
            }
            #SaveBtn:pressed {
                background: #5A52E0;
            }
            #CancelBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(49, 50, 68, 0.7), stop:1 rgba(60, 60, 80, 0.7));
                color: #A6ADC8;
                border: 1px solid rgba(108, 99, 255, 0.1);
                border-radius: 10px;
                padding: 12px 28px;
                font-size: 12px;
            }
            #CancelBtn:hover {
                background: rgba(69, 71, 90, 0.9);
                color: #CDD6F4;
                border: 1px solid rgba(108, 99, 255, 0.3);
            }
        """)

        # Outer layout for shadow margin
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        # Inner container
        inner = QWidget()
        inner.setObjectName("DialogInner")

        # Shadow on dialog
        shadow = QGraphicsDropShadowEffect(inner)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(108, 99, 255, 50))
        inner.setGraphicsEffect(shadow)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        heading = QLabel("Edit Todo" if todo else "✨  Add New Todo")
        heading.setFont(QFont("Segoe UI", 15, QFont.DemiBold))
        heading.setStyleSheet("color: #E0E0F8; background: transparent;")
        layout.addWidget(heading)

        # Accent line
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 rgba(108,99,255,0.0), stop:0.3 rgba(108,99,255,0.6),"
            "stop:0.7 rgba(167,139,250,0.6), stop:1 rgba(167,139,250,0.0));"
            "border-radius: 1px;"
        )
        layout.addWidget(line)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("What needs to be done?")
        form.addRow("Title", self.title_edit)

        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Optional description…")
        self.desc_edit.setMaximumHeight(80)
        form.addRow("Description", self.desc_edit)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        self.priority_combo.setCurrentText("Medium")
        form.addRow("Priority", self.priority_combo)

        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("e.g. Work, Personal, Study")
        self.category_edit.setText("General")
        form.addRow("Category", self.category_edit)

        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Due Date", self.due_date_edit)

        layout.addLayout(form)

        # Populate for edit mode
        if todo:
            self.title_edit.setText(todo.get("title", ""))
            self.desc_edit.setPlainText(todo.get("description", ""))
            self.priority_combo.setCurrentText(todo.get("priority", "Medium"))
            self.category_edit.setText(todo.get("category", "General"))
            if todo.get("due_date"):
                self.due_date_edit.setDate(QDate.fromString(todo["due_date"], "yyyy-MM-dd"))

        # Buttons
        layout.addSpacing(6)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("💾  Save" if todo else "＋  Add Todo")
        save_btn.setObjectName("SaveBtn")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._validate_and_accept)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        outer.addWidget(inner)

    def _validate_and_accept(self) -> None:
        if not self.title_edit.text().strip():
            self.title_edit.setStyleSheet(
                "border: 1px solid #FF4757; background: rgba(255,71,87,0.08);")
            QTimer.singleShot(1500, lambda: self.title_edit.setStyleSheet(""))
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "title": self.title_edit.text().strip(),
            "description": self.desc_edit.toPlainText().strip(),
            "priority": self.priority_combo.currentText(),
            "category": self.category_edit.text().strip() or "General",
            "due_date": self.due_date_edit.date().toString("yyyy-MM-dd"),
        }


class TodoPanel(QWidget):
    """Main panel: toolbar + scrollable todo list."""

    stats_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TodoPanel")
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 8, 16, 16)
        root.setSpacing(10)

        # --- Toolbar: search + filters + add ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._search = QLineEdit()
        self._search.setObjectName("SearchBox")
        self._search.setPlaceholderText("🔍  Search todos…")
        self._search.setMinimumHeight(40)
        self._search.textChanged.connect(self.refresh)
        toolbar.addWidget(self._search, stretch=2)

        self._filter_status = QComboBox()
        self._filter_status.setObjectName("FilterCombo")
        self._filter_status.addItems(["All", "Active", "Completed"])
        self._filter_status.setMinimumHeight(40)
        self._filter_status.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self._filter_status)

        self._filter_priority = QComboBox()
        self._filter_priority.setObjectName("FilterCombo")
        self._filter_priority.addItems(["All", "Low", "Medium", "High", "Critical"])
        self._filter_priority.setMinimumHeight(40)
        self._filter_priority.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self._filter_priority)

        add_btn = QPushButton("＋  New Todo")
        add_btn.setObjectName("AddBtn")
        add_btn.setMinimumHeight(40)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._on_add)
        # Glow effect on add button
        btn_glow = QGraphicsDropShadowEffect(add_btn)
        btn_glow.setBlurRadius(22)
        btn_glow.setOffset(0, 3)
        btn_glow.setColor(QColor(108, 99, 255, 90))
        add_btn.setGraphicsEffect(btn_glow)
        toolbar.addWidget(add_btn)

        root.addLayout(toolbar)

        # --- Scroll area for cards ---
        scroll = QScrollArea()
        scroll.setObjectName("TodoScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        self._list_container = QWidget()
        self._list_container.setObjectName("ListContainer")
        self._list_container.setStyleSheet("#ListContainer { background: transparent; }")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(4, 4, 4, 4)
        self._list_layout.setSpacing(10)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        root.addWidget(scroll)

    # --- actions ---

    def _on_add(self) -> None:
        dlg = AddEditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            db.add_todo(**data)
            self.refresh()

    def _on_edit(self, todo_id: int) -> None:
        todos = db.get_all_todos()
        todo = next((t for t in todos if t["id"] == todo_id), None)
        if not todo:
            return
        dlg = AddEditDialog(self, todo)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.get_data()
            db.update_todo(todo_id, **data)
            self.refresh()

    def _on_delete(self, todo_id: int) -> None:
        reply = QMessageBox.question(
            self, "Delete Todo",
            "Are you sure you want to delete this todo?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            db.delete_todo(todo_id)
            self.refresh()

    def _on_toggle(self, todo_id: int, completed: bool) -> None:
        db.update_todo(todo_id, completed=int(completed))
        self.refresh()

    # --- refresh ---

    def refresh(self) -> None:
        # Clear existing items
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        status_map = {"All": None, "Active": "active", "Completed": "completed"}
        status = status_map.get(self._filter_status.currentText())
        priority = self._filter_priority.currentText()
        search = self._search.text().strip()

        todos = db.get_all_todos(filter_status=status, search=search, priority=priority)

        if not todos:
            empty = QLabel("No todos yet — click  ＋ New Todo  to get started!")
            empty.setObjectName("EmptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            empty.setFont(QFont("Segoe UI", 12))
            empty.setStyleSheet("color: #585B70; padding: 60px 20px; background: transparent;")
            self._list_layout.insertWidget(0, empty)
        else:
            cards = []
            for i, t in enumerate(todos):
                card = TodoItemWidget(t, self)
                card.toggled.connect(self._on_toggle)
                card.edit_requested.connect(self._on_edit)
                card.delete_requested.connect(self._on_delete)
                self._list_layout.insertWidget(self._list_layout.count() - 1, card)
                cards.append((card, i))

            # Staggered entrance animation
            for card, idx in cards:
                card.play_entrance(delay_ms=idx * 45)

        # Emit stats
        stats = db.get_statistics()
        self.stats_changed.emit(f"✅ {stats['completed']}  /  📋 {stats['total']}")
