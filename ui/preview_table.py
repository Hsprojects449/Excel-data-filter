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

        self._init_ui()

    def _init_ui(self):
        """Initialize the table UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(15)

        pagination_layout.addWidget(QLabel("📄 Rows per page:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setValue(self.rows_per_page)
        self.rows_spinbox.setMinimum(10)
        self.rows_spinbox.setMaximum(1000)
        self.rows_spinbox.valueChanged.connect(self._on_rows_per_page_changed)
        self.rows_spinbox.setStyleSheet(
            """
            QSpinBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                width: 80px;
            }
        """
        )
        pagination_layout.addWidget(self.rows_spinbox)

        pagination_layout.addSpacing(20)

        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._previous_page)
        self.prev_btn.setMinimumHeight(32)
        self.prev_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """
        )
        pagination_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("Page 0")
        self.page_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.page_label.setStyleSheet("color: #333; min-width: 200px;")
        pagination_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._next_page)
        self.next_btn.setMinimumHeight(32)
        self.next_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #999;
            }
        """
        )
        pagination_layout.addWidget(self.next_btn)

        pagination_layout.addStretch()

        layout.addLayout(pagination_layout)

        # Table
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.table_widget.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
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
        self._update_table()

    def _update_table(self):
        """Update the table with current page data."""
        if self.dataframe is None or len(self.dataframe) == 0:
            self.table_widget.setColumnCount(0)
            self.table_widget.setRowCount(0)
            self.page_label.setText("No data")
            return

        # Calculate pagination
        total_rows = len(self.dataframe)
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page
        self.current_page = min(self.current_page, max(0, total_pages - 1))

        start_row = self.current_page * self.rows_per_page
        end_row = min(start_row + self.rows_per_page, total_rows)

        # Get page data
        page_data = self.dataframe[start_row:end_row]

        # Set table dimensions
        self.table_widget.setColumnCount(len(self.dataframe.columns))
        self.table_widget.setRowCount(len(page_data))

        # Set column headers
        self.table_widget.setHorizontalHeaderLabels(self.dataframe.columns)

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
        self.page_label.setText(
            f"Page {self.current_page + 1} of {total_pages} | "
            f"Rows {start_row + 1}-{end_row} of {total_rows:,}"
        )

        # Update button states
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)

        # Auto-adjust column widths
        self.table_widget.resizeColumnsToContents()

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
