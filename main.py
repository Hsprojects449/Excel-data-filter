"""
Main entry point for the Excel Data Filter application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from services.logger import logger

__version__ = "1.0.0"


def main():
    """Main application entry point."""
    logger.info(f"Excel Data Filter v{__version__} starting...")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    logger.info("Application window shown")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
