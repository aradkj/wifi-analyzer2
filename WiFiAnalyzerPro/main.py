"""
WiFi Analyzer Pro - Main Desktop Application Entry Point
Launches the PySide6 modern dark desktop application.
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt

from app.main_window import MainWindow
from app.utils.resources import get_asset_path, get_app_icon_path


def load_stylesheet() -> str:
    """Load QSS stylesheet file."""
    qss_path = get_asset_path("assets/styles/dark_theme.qss")
    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as exc:
            print(f"Warning: Failed to load stylesheet: {exc}")
    return ""


def main():
    # Ensure working directory is correctly set
    app = QApplication(sys.argv)
    app.setApplicationName("WiFi Analyzer Pro")
    app.setApplicationDisplayName("WiFi Analyzer Pro")
    app.setOrganizationName("WiFiAnalyzerPro")
    app.setOrganizationDomain("wifianalyzerpro.local")

    # Set Application Icon
    icon_path = get_app_icon_path()
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Apply global Dark Theme Stylesheet
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Launch Main Window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
