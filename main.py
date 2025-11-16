"""
Main entry point for the Excel Data Filter application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.logger import logger
from PyQt6.QtGui import QIcon
import os

__version__ = "1.0.0"


def main():
    """Main application entry point."""
    logger.info(f"Excel Data Filter v{__version__} starting...")

    app = QApplication(sys.argv)
    # Resolve icons from the packaged ui/assets directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    ui_base = os.path.join(base_path, "ui")
    icon_path = os.path.join(ui_base, "assets", "vsn_logo.jpg")
    win_icon_path = os.path.join(ui_base, "assets", "favicon.ico")
    
    # Set light theme as default instead of system theme
    app.setStyle('Fusion')  # Use Fusion style for consistent appearance
    
    # Apply professional light theme palette
    professional_palette = """
    QApplication {
        font-family: 'Segoe UI';
    }
    QWidget {
        background-color: #ffffff;
        color: #2c3e50;
        selection-background-color: #4CAF50;
        selection-color: white;
        font-family: 'Segoe UI';
        font-size: 11px;
    }
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f8f9fa, stop:1 #e9ecef);
    }
    QScrollBar:vertical {
        background: #f8f9fa;
        width: 16px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ced4da, stop:1 #adb5bd);
        border-radius: 7px;
        min-height: 30px;
        border: 1px solid #adb5bd;
    }
    QScrollBar::handle:vertical:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #adb5bd, stop:1 #868e96);
    }
    QScrollBar::handle:vertical:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #868e96, stop:1 #6c757d);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: transparent;
        height: 0px;
    }
    QScrollBar:horizontal {
        background: #f8f9fa;
        height: 16px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ced4da, stop:1 #adb5bd);
        border-radius: 7px;
        min-width: 30px;
        border: 1px solid #adb5bd;
    }
    QScrollBar::handle:horizontal:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #adb5bd, stop:1 #868e96);
    }
    QScrollBar::handle:horizontal:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #868e96, stop:1 #6c757d);
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: transparent;
        width: 0px;
    }
    QToolTip {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #fff3cd, stop:1 #ffeaa7);
        color: #856404;
        border: 1px solid #ffeaa7;
        padding: 6px 8px;
        border-radius: 6px;
        font-family: 'Segoe UI';
        font-size: 10px;
    }
    QMessageBox {
        background-color: #ffffff;
        font-family: 'Segoe UI';
    }
    QMessageBox QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #4CAF50, stop:1 #45a049);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-family: 'Segoe UI';
        font-size: 11px;
        min-width: 80px;
    }
    QMessageBox QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #45a049, stop:1 #3d8b40);
    }
    """
    
    app.setStyleSheet(professional_palette)

    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    #window.setWindowIcon(QIcon(win_icon_path))
    window.show()

    logger.info("Application window shown")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
