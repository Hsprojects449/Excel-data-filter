"""
Simple Filter Panel - Just a button to open the popup filter manager
This keeps the main window clean and uncluttered
"""

from typing import List, Dict
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QCursor
from typing import List
from loguru import logger
from ui.popup_filter_window import PopupFilterWindow


class SimpleFilterPanel(QWidget):
    """Simple filter panel with just a button to open popup filter manager."""

    filters_applied = pyqtSignal(list, str)  # filters, logic (AND/OR)

    def __init__(self):
        super().__init__()
        self.columns: List[str] = []
        self.popup_window = None
        
        # Store current filters
        self.current_filters: List[Dict] = []
        self.current_logic: str = "AND"
        
        # Set compact size policy (no fixed height to avoid extra gap)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self._init_ui()

    def _init_ui(self):
        """Initialize the simple filter panel UI."""
        layout = QHBoxLayout()
        # Tighter margins and spacing to reduce gap below this panel
        layout.setContentsMargins(16, 8, 16, 6)
        layout.setSpacing(10)

        # Filter manager label
        filter_label = QLabel("🔍 Data Filtering:")
        filter_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        filter_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 8px;
                background: transparent;
            }
        """)
        layout.addWidget(filter_label)

        # Open filter manager button
        open_filter_btn = QPushButton("🛠️ Open Filter Manager")
        open_filter_btn.setMinimumHeight(34)
        open_filter_btn.setMinimumWidth(200)
        open_filter_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        open_filter_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #4CAF50);
                border: 2px solid rgba(255, 255, 255, 0.4);
                cursor: pointer;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3e8e41, stop:1 #45a049);
            }
        """
        )
        open_filter_btn.clicked.connect(self._open_filter_manager)
        layout.addWidget(open_filter_btn)

        # Clear filters button
        clear_filters_btn = QPushButton("🗑️ Clear All Filters")
        clear_filters_btn.setMinimumHeight(34)
        clear_filters_btn.setMinimumWidth(180)
        clear_filters_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_filters_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc3545, stop:1 #c82333);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c82333, stop:1 #dc3545);
                border: 2px solid rgba(255, 255, 255, 0.4);
                cursor: pointer;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bd2130, stop:1 #c82333);
            }
        """
        )
        clear_filters_btn.clicked.connect(self._clear_all_filters)
        layout.addWidget(clear_filters_btn)

        # Filter status label
        self.status_label = QLabel("No filters active")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-style: italic;
            }
        """)
        layout.addWidget(self.status_label)

        layout.addStretch()  # Push everything to the left

        self.setLayout(layout)
        
        # Style the panel background
        self.setStyleSheet("""
            SimpleFilterPanel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-bottom: 2px solid #e9ecef;
                border-radius: 8px;
            }
        """)

    def set_columns(self, columns: List[str], dataframe=None):
        """Set available columns for filtering.
        Columns ending with _v1/_uni are excluded from filtering per requirements.
        Also detect numeric columns (all non-empty values numeric) for dynamic operator display."""
        self.columns = [col for col in columns if not col.lower().endswith(("_v1", "_uni"))]
        self.numeric_columns = []
        try:
            if dataframe is not None:
                import polars as pl
                for col in self.columns:
                    try:
                        s = dataframe[col]
                        # Direct numeric dtypes
                        if s.dtype in (
                            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                            pl.Float32, pl.Float64
                        ):
                            self.numeric_columns.append(col)
                            continue
                        # For Utf8 columns, inspect content
                        if s.dtype == pl.Utf8:
                            values = [v for v in s.to_list() if v is not None and str(v).strip() != ""]
                            if values and all(__import__("re").match(r"^-?\d+(\.\d+)?$", str(v).strip()) for v in values):
                                self.numeric_columns.append(col)
                    except Exception:
                        continue
        except Exception:
            # Fallback: leave numeric_columns empty on failure
            pass
        logger.info(
            f"SimpleFilterPanel: Set {len(self.columns)} columns (numeric: {len(getattr(self,'numeric_columns', []))})"
        )

    def _open_filter_manager(self):
        """Open the popup filter manager window."""
        if not self.columns:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        try:
            # Create popup window with current filters
            self.popup_window = PopupFilterWindow(
                self.window(), 
                self.columns,
                numeric_columns=getattr(self, "numeric_columns", []),
                current_filters=self.current_filters,
                current_logic=self.current_logic
            )
            self.popup_window.filters_applied.connect(self._on_filters_applied)
            
            # Show the popup
            self.popup_window.exec()
            
            logger.info("Opened filter manager popup")
            
        except Exception as e:
            logger.error(f"Failed to open filter manager: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to open filter manager: {str(e)}")

    def _on_filters_applied(self, filters: list, logic: str):
        """Handle filters applied from popup window."""
        logger.info(f"Received filters from popup: {len(filters)} filters with {logic} logic")
        
        # Store current filters for future editing
        self.current_filters = filters
        self.current_logic = logic
        
        # Update status label
        if filters:
            self.status_label.setText(f"Active: {len(filters)} filter(s) with {logic} logic")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #155724;
                    padding: 8px 12px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d4edda, stop:1 #c3e6cb);
                    border: 1px solid #c3e6cb;
                    border-radius: 8px;
                    font-weight: bold;
                }
            """)
        else:
            self.status_label.setText("No filters active")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    padding: 8px 12px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    font-style: italic;
                }
            """)
        
        # Emit the signal to main window
        self.filters_applied.emit(filters, logic)

    def _clear_all_filters(self):
        """Clear all filters."""
        # Clear stored filters
        self.current_filters = []
        self.current_logic = "AND"
        
        self.status_label.setText("No filters active")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                padding: 8px 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-style: italic;
            }
        """)
        
        logger.info("Cleared all filters from simple panel")
        # Emit empty filters to reset data
        self.filters_applied.emit([], "AND")