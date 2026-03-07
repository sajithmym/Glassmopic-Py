#!/usr/bin/env python3
"""Glassmopic — Advanced Todo List App (PyQt5)."""

import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

import database as db
from widgets.main_window import MainWindow


def load_stylesheet() -> str:
    qss_path = os.path.join(os.path.dirname(__file__), "resources", "styles.qss")
    if os.path.isfile(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def main() -> None:
    db.init_db()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")

    qss = load_stylesheet()
    if qss:
        app.setStyleSheet(qss)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
