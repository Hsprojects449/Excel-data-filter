"""
Preview table widget for displaying filtered data with enhanced UI.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QComboBox,
    QAbstractScrollArea,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QCursor
import polars as pl
import re
import unicodedata
from ui.unified_styles import UnifiedStyles



class PreviewTable(QWidget):
    """Table widget for previewing filtered data."""

    def __init__(self):
        super().__init__()
        self.dataframe: pl.DataFrame = None
        self.current_page = 0
        self.rows_per_page = 100
        self.sort_column = None
        self.sort_ascending = True

        self._init_ui()

    def _init_ui(self):
        """Initialize the table UI."""
        layout = QVBoxLayout()
        # Reduce top margin to pull the pagination block closer to the filter panel
        layout.setContentsMargins(15, 8, 15, 12)
        layout.setSpacing(8)

        # Pagination controls (flexible height)
        pagination_widget = QWidget()
        pagination_widget.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 6px;
            }
        """
        )

        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(16)
        pagination_layout.setContentsMargins(12, 8, 12, 8)
        pagination_widget.setLayout(pagination_layout)

        # Rows per page section
        rows_section = QHBoxLayout()
        rows_section.setSpacing(8)
        
        rows_label = QLabel("📄 Rows per page:")
        rows_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        rows_label.setStyleSheet("color: #2c3e50; padding: 3px 0px;")
        rows_section.addWidget(rows_label)
        
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setValue(self.rows_per_page)
        self.rows_spinbox.setMinimum(10)
        self.rows_spinbox.setMaximum(1000)
        self.rows_spinbox.setFixedHeight(26)
        self.rows_spinbox.setMinimumWidth(75)
        self.rows_spinbox.valueChanged.connect(self._on_rows_per_page_changed)
        self.rows_spinbox.setStyleSheet(UnifiedStyles.get_spinbox_style(font_size=11, min_height=18, min_width=75))
        
        # Add Unicode arrows for better visibility
        # Remove the arrow fixer that's not needed
        # self.rows_spinbox already has native arrows
        rows_section.addWidget(self.rows_spinbox)
        
        pagination_layout.addLayout(rows_section)
        pagination_layout.addSpacing(30)

        # Navigation section
        nav_section = QHBoxLayout()
        nav_section.setSpacing(10)
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.prev_btn.clicked.connect(self._previous_page)
        self.prev_btn.setFixedHeight(30)  # Compact pagination height
        self.prev_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5d6d7e, stop:1 #515a5a);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 4px 12px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #515a5a, stop:1 #424949);
                cursor: pointer;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #424949, stop:1 #34495e);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        nav_section.addWidget(self.prev_btn)

        # Page selection section
        page_section = QHBoxLayout()
        page_section.setSpacing(8)
        
        page_select_label = QLabel("Page:")
        page_select_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        page_select_label.setStyleSheet("color: #2c3e50; padding: 3px 0px;")
        page_section.addWidget(page_select_label)
        
        self.page_dropdown = QComboBox()
        self.page_dropdown.setFixedHeight(26)
        self.page_dropdown.setMinimumWidth(70)
        self.page_dropdown.currentIndexChanged.connect(self._on_page_selected)
        self.page_dropdown.setStyleSheet(UnifiedStyles.get_combobox_style(font_size=11, min_height=18, min_width=70))
        UnifiedStyles.apply_combobox_popup_style(self.page_dropdown)
        page_section.addWidget(self.page_dropdown)
        
        nav_section.addLayout(page_section)

        self.page_label = QLabel("Page 0")
        self.page_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.page_label.setStyleSheet(
            """
            QLabel {
                color: #495057; 
                min-width: 230px; 
                padding: 4px 10px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """
        )
        nav_section.addWidget(self.page_label)

        self.next_btn = QPushButton("Next →")
        self.next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_btn.clicked.connect(self._next_page)
        self.next_btn.setFixedHeight(30)  # Compact pagination height
        self.next_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5d6d7e, stop:1 #515a5a);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 4px 12px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #515a5a, stop:1 #424949);
                cursor: pointer;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #424949, stop:1 #34495e);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        nav_section.addWidget(self.next_btn)
        
        pagination_layout.addLayout(nav_section)
        pagination_layout.addStretch()

        # Add pagination widget to main layout
        layout.addWidget(pagination_widget)

        # Table with enhanced scrolling
        self.table_widget = QTableWidget()
        # Prefer a font that supports Indic scripts so Telugu renders correctly
        try:
            self.table_widget.setFont(QFont("Nirmala UI", 11))
        except Exception:
            # Fallback to default if font not available
            self.table_widget.setFont(QFont("Segoe UI", 11))
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.table_widget.setSortingEnabled(False)  # We'll handle sorting manually
        self.table_widget.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        
        # Configure vertical header (row numbers) to be visible and properly styled
        self.table_widget.verticalHeader().setVisible(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(30)
        self.table_widget.verticalHeader().setMinimumSectionSize(25)
        
        # Configure optimal scrolling behavior
        self._setup_table_scrolling()
        
        # Table styling with unified scrollbars and proper headers
        table_style = """
            QTableWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
                selection-background-color: #c8e6c9;
                alternate-background-color: #f8f9fa;
                background-color: #ffffff;
                outline: none;
            }
            QTableWidget:focus {
                border: 2px solid #e0e0e0;
                outline: none;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border: none;
                font-size: 12px;
                font-family: 'Nirmala UI', 'Segoe UI', sans-serif;
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: #c8e6c9;
                color: #2e7d32;
                font-weight: 500;
                border: none;
                outline: none;
            }
            QTableWidget::item:focus {
                border: none;
                outline: none;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Nirmala UI', 'Segoe UI', sans-serif;
                border-right: 1px solid #3d8b40;
                border-bottom: 2px solid #3d8b40;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QHeaderView::section:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
            QHeaderView::section:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                padding: 8px 6px;
                font-size: 11px;
                font-weight: bold;
                text-align: center;
                border-right: 2px solid #3d8b40;
                border-bottom: 1px solid #3d8b40;
                min-width: 40px;
            }
        """
        self.table_widget.setStyleSheet(table_style + UnifiedStyles.get_scrollbar_style())
        layout.addWidget(self.table_widget, 1)

        self.setLayout(layout)

    def _setup_table_scrolling(self):
        """Configure enhanced table scrolling for both desktop and touch."""
        # Enable scroll bars for both directions
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Enable smooth pixel-based scrolling (crucial for touch)
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        # Configure scroll steps for optimal finger scrolling
        self.table_widget.verticalScrollBar().setSingleStep(8)  # Smooth finger movements
        self.table_widget.horizontalScrollBar().setSingleStep(8)
        self.table_widget.verticalScrollBar().setPageStep(120)  # Good page scrolling
        self.table_widget.horizontalScrollBar().setPageStep(120)
        
        # Enable focus for keyboard navigation
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Apply kinetic scrolling with enhanced configuration
        try:
            from PyQt6.QtWidgets import QScroller, QScrollerProperties
            from loguru import logger
            
            # Apply to table widget
            scroller = QScroller.scroller(self.table_widget)
            properties = scroller.scrollerProperties()
            
            # Fine-tune for table scrolling
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.DragStartDistance, 0.005)
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.DragVelocitySmoothingFactor, 0.02)
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.AxisLockThreshold, 0.7)
            
            scroller.setScrollerProperties(properties)
            QScroller.grabGesture(self.table_widget, QScroller.ScrollerGestureType.TouchGesture)
            
            # Also apply to viewport for better coverage
            viewport_scroller = QScroller.scroller(self.table_widget.viewport())
            viewport_scroller.setScrollerProperties(properties)
            QScroller.grabGesture(self.table_widget.viewport(), 
                                QScroller.ScrollerGestureType.TouchGesture)
            
            logger.info("Table kinetic scrolling enabled")
        except Exception as e:
            logger.debug(f"QScroller not available for table: {e}")
            # Fallback: Ensure at least basic smooth scrolling
            pass

    def set_data(self, dataframe: pl.DataFrame):
        """Load data into the preview table."""
        # Check if dataframe is None or empty
        if dataframe is None:
            self.table_widget.setColumnCount(0)
            self.table_widget.setRowCount(0)
            self.page_label.setText("No data")
            self.page_dropdown.clear()
            self.dataframe = None
            return
            
        # Store current scroll position before updating
        h_scroll = self.table_widget.horizontalScrollBar().value()
        v_scroll = self.table_widget.verticalScrollBar().value()
        
        # Show all columns exactly as in the Excel source (no exclusions here)
        self.dataframe = dataframe
        self.current_page = 0
        self.sort_column = None  # Reset sorting when new data is loaded
        self.sort_ascending = True
        self._update_table()
        
        # Restore scroll position after a brief delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self._restore_scroll_position(h_scroll, v_scroll))
    
    def _restore_scroll_position(self, h_pos: int, v_pos: int):
        """Restore horizontal and vertical scroll positions."""
        try:
            h_bar = self.table_widget.horizontalScrollBar()
            v_bar = self.table_widget.verticalScrollBar()
            
            # Only restore if the scroll bars still exist and have valid ranges
            if h_bar.maximum() > 0:
                h_bar.setValue(min(h_pos, h_bar.maximum()))
            if v_bar.maximum() > 0:
                v_bar.setValue(min(v_pos, v_bar.maximum()))
        except Exception:
            # Ignore any errors in scroll restoration
            pass

    def _get_display_data(self):
        """Get the data to display (with sorting applied)."""
        if self.dataframe is None:
            return None
        
        display_data = self.dataframe
        
        # Apply sorting if a column is selected
        if self.sort_column and self.sort_column in display_data.columns:
            try:
                display_data = display_data.sort(self.sort_column, descending=not self.sort_ascending)
            except Exception as e:
                # If sorting fails, use original data
                print(f"Sorting failed for column {self.sort_column}: {e}")
                display_data = self.dataframe
        
        return display_data

    def _update_table(self):
        """Update the table with current page data."""
        display_data = self._get_display_data()
        
        if display_data is None or len(display_data) == 0:
            self.table_widget.setColumnCount(0)
            self.table_widget.setRowCount(0)
            self.page_label.setText("No data")
            self.page_dropdown.clear()
            return

        # Calculate pagination
        total_rows = len(display_data)
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page
        self.current_page = min(self.current_page, max(0, total_pages - 1))

        # Update page dropdown
        self._update_page_dropdown(total_pages)

        start_row = self.current_page * self.rows_per_page
        end_row = min(start_row + self.rows_per_page, total_rows)

        # Get page data
        page_data = display_data[start_row:end_row]

        # Set table dimensions
        self.table_widget.setColumnCount(len(display_data.columns))
        self.table_widget.setRowCount(len(page_data))

        # Set column headers with sorting indicators
        headers = []
        for col in display_data.columns:
            if col == self.sort_column:
                arrow = "↑" if self.sort_ascending else "↓"
                headers.append(f"{col} {arrow}")
            else:
                headers.append(col)
        
        self.table_widget.setHorizontalHeaderLabels(headers)

        # Set row numbers for vertical header (global row numbers, not just page numbers)
        row_labels = []
        for i in range(len(page_data)):
            row_labels.append(str(start_row + i + 1))  # 1-based indexing
        self.table_widget.setVerticalHeaderLabels(row_labels)

        # Populate table
        for row_idx, row in enumerate(page_data.iter_rows()):
            for col_idx, value in enumerate(row):
                # Sanitize value to remove carriage returns and trailing spaces
                text = self._sanitize_cell_value(value)
                
                item = QTableWidgetItem(text)
                # Explicitly set font per item to ensure complex-script shaping is used
                try:
                    item.setFont(QFont("Nirmala UI", 10))
                except Exception:
                    item.setFont(QFont("Segoe UI", 10))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Alternate row colors
                if row_idx % 2 == 0:
                    item.setBackground(QColor("#ffffff"))
                else:
                    item.setBackground(QColor("#f9f9f9"))

                self.table_widget.setItem(row_idx, col_idx, item)

        # Update pagination info
        sort_info = ""
        if self.sort_column:
            sort_info = f" | Sorted by {self.sort_column} {'↑' if self.sort_ascending else '↓'}"
            
        self.page_label.setText(
            f"Page {self.current_page + 1} of {total_pages} | "
            f"Rows {start_row + 1}-{end_row} of {total_rows:,}{sort_info}"
        )

        # Update button states
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

        # Auto-adjust column widths
        self.table_widget.resizeColumnsToContents()

    def _on_header_clicked(self, logical_index: int):
        """Handle column header clicks for sorting."""
        if self.dataframe is None or len(self.dataframe.columns) == 0:
            return
        
        column_name = self.dataframe.columns[logical_index]
        
        # Toggle sorting direction if clicking the same column
        if self.sort_column == column_name:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column_name
            self.sort_ascending = True
        
        # Reset to first page when sorting
        self.current_page = 0
        self._update_table()

    def _update_page_dropdown(self, total_pages: int):
        """Update the page dropdown with available pages."""
        self.page_dropdown.blockSignals(True)  # Prevent triggering selection during update
        self.page_dropdown.clear()
        
        if total_pages > 0:
            for i in range(total_pages):
                self.page_dropdown.addItem(f"{i + 1}")
            self.page_dropdown.setCurrentIndex(self.current_page)
        
        self.page_dropdown.blockSignals(False)

    def _on_page_selected(self, index: int):
        """Handle page selection from dropdown."""
        if index >= 0:
            self.current_page = index
            self._update_table()

    def _next_page(self):
        """Go to next page."""
        self.current_page += 1
        self._update_table()

    def _previous_page(self):
        """Go to previous page."""
        self.current_page = max(0, self.current_page - 1)
        self._update_table()

    def _on_rows_per_page_changed(self, value: int):
        """Handle change in rows per page."""
        self.rows_per_page = value
        self.current_page = 0
        self._update_table()

    def _sanitize_cell_value(self, value):
        """Sanitize cell values for display to prevent artifacts like _x000D_.
        
        Removes carriage returns, control characters, and trailing spaces
        that can cause display issues, especially with Telugu and other Indic scripts.
        """
        # Handle None
        if value is None:
            return ""
        
        # Convert to string
        try:
            if isinstance(value, (bytes, bytearray)):
                text = value.decode("utf-8", errors="replace")
            else:
                text = str(value)
        except Exception:
            text = str(value)
        
        # Remove carriage return characters (which display as _x000D_ in some contexts)
        text = text.replace('\r', '')
        
        # Remove other control characters except newline and tab
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', text)
        
        # Strip trailing spaces and non-breaking spaces
        text = re.sub(r'[ \t\u00A0]+$', '', text)
        
        # Normalize Unicode to NFC for better rendering of complex scripts
        try:
            text = unicodedata.normalize("NFC", text)
        except Exception:
            pass
        
        return text
