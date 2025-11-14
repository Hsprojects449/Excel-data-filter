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
from PyQt6.QtGui import QFont, QColor
import polars as pl


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
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Pagination controls (flexible height)
        pagination_widget = QWidget()
        pagination_widget.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
            }
        """
        )

        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(20)
        pagination_layout.setContentsMargins(15, 10, 15, 10)
        pagination_widget.setLayout(pagination_layout)

        # Rows per page section
        rows_section = QHBoxLayout()
        rows_section.setSpacing(8)
        
        rows_label = QLabel("📄 Rows per page:")
        rows_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        rows_label.setStyleSheet("color: #2c3e50; padding: 3px 0px;")
        rows_section.addWidget(rows_label)
        
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setValue(self.rows_per_page)
        self.rows_spinbox.setMinimum(10)
        self.rows_spinbox.setMaximum(1000)
        self.rows_spinbox.valueChanged.connect(self._on_rows_per_page_changed)
        self.rows_spinbox.setStyleSheet(
            """
            QSpinBox {
                padding: 6px 10px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 500;
                color: #495057;
                width: 80px;
                min-height: 20px;
            }
            QSpinBox:hover {
                border: 2px solid #4CAF50;
                background-color: #f8f9fa;
            }
            QSpinBox:focus {
                border: 2px solid #4CAF50;
                background-color: #ffffff;
            }
        """
        )
        rows_section.addWidget(self.rows_spinbox)
        
        pagination_layout.addLayout(rows_section)
        pagination_layout.addSpacing(30)

        # Navigation section
        nav_section = QHBoxLayout()
        nav_section.setSpacing(12)
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._previous_page)
        self.prev_btn.setFixedHeight(32)  # Match header button height
        self.prev_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5d6d7e, stop:1 #515a5a);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 15px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #515a5a, stop:1 #424949);
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
        page_select_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        page_select_label.setStyleSheet("color: #2c3e50; padding: 3px 0px;")
        page_section.addWidget(page_select_label)
        
        self.page_dropdown = QComboBox()
        self.page_dropdown.setMinimumWidth(80)
        self.page_dropdown.currentIndexChanged.connect(self._on_page_selected)
        self.page_dropdown.setStyleSheet(
            """
            QComboBox {
                padding: 8px 10px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 500;
                color: #495057;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 2px solid #4CAF50;
                background-color: #f8f9fa;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50;
                background-color: #ffffff;
            }
            QComboBox QAbstractItemView {
                font-family: 'Segoe UI';
                font-size: 12px;
                padding: 4px;
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                selection-background-color: #4CAF50;
                selection-color: white;
            }
        """
        )
        page_section.addWidget(self.page_dropdown)
        
        nav_section.addLayout(page_section)

        self.page_label = QLabel("Page 0")
        self.page_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.page_label.setStyleSheet(
            """
            QLabel {
                color: #495057; 
                min-width: 250px; 
                padding: 6px 12px;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """
        )
        nav_section.addWidget(self.page_label)

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._next_page)
        self.next_btn.setFixedHeight(32)  # Match header button height
        self.next_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5d6d7e, stop:1 #515a5a);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 15px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #515a5a, stop:1 #424949);
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

        # Table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.table_widget.setSortingEnabled(False)  # We'll handle sorting manually
        self.table_widget.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        
        # Enable scroll bars for both directions
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Enable smooth finger/touch scrolling with QScroller
        self.table_widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        # Enhanced kinetic scrolling for touch devices
        self.table_widget.verticalScrollBar().setSingleStep(3)
        self.table_widget.horizontalScrollBar().setSingleStep(3)
        self.table_widget.verticalScrollBar().setPageStep(80)
        self.table_widget.horizontalScrollBar().setPageStep(80)
        
        # Enable comprehensive touch support
        self.table_widget.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.table_widget.setAttribute(Qt.WidgetAttribute.WA_TouchPadAcceptSingleTouchEvents, True)
        self.table_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Try to enable momentum scrolling with QScroller
        try:
            from PyQt6.QtWidgets import QScroller
            scroller = QScroller.scroller(self.table_widget)
            if scroller:
                QScroller.grabGesture(self.table_widget, QScroller.ScrollerGestureType.TouchGesture)
                # Fine-tune scrolling properties
                properties = scroller.scrollerProperties()
                properties.setScrollMetric(QScroller.ScrollMetric.VerticalOvershootPolicy, 
                                         QScroller.OvershootPolicy.OvershootAlwaysOff)
                properties.setScrollMetric(QScroller.ScrollMetric.HorizontalOvershootPolicy, 
                                         QScroller.OvershootPolicy.OvershootAlwaysOff)
                scroller.setScrollerProperties(properties)
        except (ImportError, AttributeError):
            pass  # QScroller not available or method not available
        
        self.table_widget.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 10px 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
                border-right: 1px solid #45a049;
            }
            QHeaderView::section:hover {
                background-color: #45a049;
            }
            QHeaderView::section:pressed {
                background-color: #3d8b40;
            }
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 16px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 7px;
                min-height: 30px;
                border: 1px solid #b0b0b0;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
            QScrollBar:horizontal {
                background-color: #f5f5f5;
                height: 16px;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c0c0c0;
                border-radius: 7px;
                min-width: 30px;
                border: 1px solid #b0b0b0;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::handle:horizontal:pressed {
                background-color: #808080;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: transparent;
                width: 0px;
                height: 0px;
            }
        """
        )
        layout.addWidget(self.table_widget, 1)

        self.setLayout(layout)

    def set_data(self, dataframe: pl.DataFrame):
        """Load data into the preview table."""
        # Filter out columns ending with _v1, _uni (case-insensitive)
        columns_to_show = [
            col for col in dataframe.columns 
            if not col.lower().endswith(("_v1", "_uni"))
        ]
        self.dataframe = dataframe.select(columns_to_show) if columns_to_show else dataframe
        self.current_page = 0
        self.sort_column = None  # Reset sorting when new data is loaded
        self.sort_ascending = True
        self._update_table()

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

        # Populate table
        for row_idx, row in enumerate(page_data.iter_rows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
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
