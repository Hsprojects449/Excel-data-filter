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

        layout.addStretch()  # Push edit controls to the right
        
        # Edit counter label (will be controlled by preview_table)
        self.edit_counter_label = QLabel("✏️ Edits: 0")
        self.edit_counter_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_counter_label.setStyleSheet("""
            QLabel {
                color: #e67e22;
                padding: 6px 12px;
                background: #fff3e0;
                border: 1px solid #ffb74d;
                border-radius: 6px;
            }
        """)
        self.edit_counter_label.setVisible(False)  # Hidden until edits are made
        layout.addWidget(self.edit_counter_label)
        
        # Undo all button (will be controlled by preview_table)
        self.undo_all_btn = QPushButton("↶ Undo All")
        self.undo_all_btn.setMinimumHeight(34)
        self.undo_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.undo_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e67e22, stop:1 #d35400);
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
                    stop:0 #d35400, stop:1 #c0392b);
                border: 2px solid rgba(255, 255, 255, 0.4);
                cursor: pointer;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
        """)
        self.undo_all_btn.setVisible(False)  # Hidden until edits are made
        layout.addWidget(self.undo_all_btn)

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
        
        if dataframe is None:
            logger.warning("No dataframe provided to set_columns - numeric detection skipped")
        
        try:
            if dataframe is not None:
                import polars as pl
                import re
                logger.debug(f"Starting numeric detection for {len(self.columns)} columns")
                
                for col in self.columns:
                    try:
                        s = dataframe[col]
                        logger.debug(f"Checking column '{col}' with dtype: {s.dtype}")
                        
                        # Direct numeric dtypes
                        if s.dtype in (
                            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
                            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
                            pl.Float32, pl.Float64
                        ):
                            self.numeric_columns.append(col)
                            logger.info(f"✓ Column '{col}' detected as numeric (dtype: {s.dtype})")
                            continue
                        
                        # For Utf8 columns, inspect content - filter out null/empty first
                        if s.dtype == pl.Utf8:
                            # Get all values, filter nulls and empty strings
                            all_values = s.to_list()
                            non_empty_values = [v for v in all_values if v is not None and str(v).strip() != ""]
                            
                            logger.debug(f"Column '{col}': {len(all_values)} total, {len(non_empty_values)} non-empty")
                            
                            # Need at least some values to check
                            if len(non_empty_values) < 1:
                                logger.debug(f"Column '{col}': skipped (no non-empty values)")
                                continue
                            
                            # Sample up to 200 values for checking (better coverage)
                            sample_values = non_empty_values[:200]
                            
                            # Check if values are numeric (allow decimals and negative numbers)
                            numeric_count = 0
                            for v in sample_values:
                                v_str = str(v).strip()
                                # Match: optional minus, digits, optional decimal point and digits
                                if re.match(r'^-?\d+\.?\d*$', v_str):
                                    numeric_count += 1
                            
                            # Consider numeric if at least 80% are numeric (allows for some errors/headers)
                            threshold = 0.8
                            ratio = numeric_count / len(sample_values)
                            
                            if ratio >= threshold:
                                self.numeric_columns.append(col)
                                logger.info(f"✓ Column '{col}' detected as numeric string ({numeric_count}/{len(sample_values)} = {ratio:.1%} numeric)")
                            else:
                                logger.debug(f"Column '{col}' is Utf8 but not numeric ({numeric_count}/{len(sample_values)} = {ratio:.1%} numeric, threshold: {threshold:.1%})")
                                
                    except Exception as e:
                        logger.error(f"Error checking column '{col}': {e}")
                        continue
        except Exception as e:
            logger.error(f"Error in numeric detection: {e}")
            # Fallback: leave numeric_columns empty on failure
            pass
        
        logger.info(
            f"SimpleFilterPanel: Set {len(self.columns)} filterable columns | "
            f"Detected {len(self.numeric_columns)} numeric columns: {self.numeric_columns}"
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