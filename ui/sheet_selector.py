"""
Sheet selection dialog for Excel files with multiple sheets.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFrame,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap, QCursor
from typing import Optional, List


class SheetSelectionDialog(QDialog):
    """Dialog for selecting a sheet from an Excel file with multiple sheets."""

    def __init__(self, sheet_names: List[str], parent=None):
        super().__init__(parent)
        self.sheet_names = sheet_names
        self.selected_sheet = None
        self._init_ui()

    def _init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Select Excel Sheet")
        self.setFixedSize(450, 350)
        self.setModal(True)
        
        # Apply consistent styling
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-radius: 10px;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header section
        header_label = QLabel("📊 Select Sheet to Load")
        header_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f3f4);
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 5px;
            }
        """
        )
        layout.addWidget(header_label)

        # Info label
        info_label = QLabel(f"This Excel file contains {len(self.sheet_names)} sheet(s). Please select one:")
        info_label.setFont(QFont("Segoe UI", 11))
        info_label.setStyleSheet("color: #495057; margin-bottom: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Sheet list
        self.sheet_list = QListWidget()
        self.sheet_list.setStyleSheet(
            """
            QListWidget {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 12px;
                padding: 5px;
                outline: none;
            }
            QListWidget:focus {
                border: 2px solid #4CAF50;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 15px;
                border: none;
                border-radius: 6px;
                margin: 2px;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c8e6c9, stop:1 #a5d6a7);
                color: #2e7d32;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                font-weight: bold;
                outline: none;
                border: none;
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }
        """
        )

        # Add sheets to the list
        for i, sheet_name in enumerate(self.sheet_names):
            item = QListWidgetItem(f"📄 {sheet_name}")
            item.setData(Qt.ItemDataRole.UserRole, sheet_name)
            self.sheet_list.addItem(item)
            
            # Select first sheet by default
            if i == 0:
                item.setSelected(True)
                self.sheet_list.setCurrentItem(item)

        # Handle double-click to confirm selection
        self.sheet_list.itemDoubleClicked.connect(self._on_sheet_double_clicked)
        
        layout.addWidget(self.sheet_list, 1)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("border: 1px solid #e9ecef; margin: 5px 0px;")
        layout.addWidget(separator)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        buttons_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c757d, stop:1 #5a6268);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6268, stop:1 #495057);
                cursor: pointer;
            }
        """
        )
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        # Load Selected button
        load_btn = QPushButton("✅ Load Selected Sheet")
        load_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        load_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 11px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
                cursor: pointer;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
        """
        )
        load_btn.clicked.connect(self._on_load_clicked)
        load_btn.setDefault(True)
        buttons_layout.addWidget(load_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def _on_sheet_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on sheet item."""
        self.selected_sheet = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def _on_load_clicked(self):
        """Handle load button click."""
        current_item = self.sheet_list.currentItem()
        if current_item:
            self.selected_sheet = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a sheet to load.")

    def get_selected_sheet(self) -> Optional[str]:
        """Get the selected sheet name."""
        return self.selected_sheet