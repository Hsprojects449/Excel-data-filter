"""
Advanced filtering panel with dynamic column selection and multiple filter rules.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QLabel,
    QScrollArea,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import polars as pl
from typing import List, Dict, Any
from loguru import logger


class FilterRule(QFrame):
    """Individual filter rule widget."""

    removed = pyqtSignal()

    def __init__(self, columns: List[str], selected_column: str, rule_id: int = 0):
        super().__init__()
        self.rule_id = rule_id
        self.columns = [col for col in columns if not col.lower().endswith(("_v1", "_uni"))]
        self.selected_column = selected_column  # Fixed column name
        self.setStyleSheet(
            """
            QFrame {
                border: 1px solid #4CAF50;
                border-radius: 5px;
                background-color: #f0f8f0;
                padding: 6px;
                margin: 3px 0px;
            }
            QFrame:hover {
                background-color: #e8f5e9;
                border: 1px solid #2e7d32;
            }
        """
        )
        self._init_ui()

    def _init_ui(self):
        """Initialize the filter rule UI - single row layout."""
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        # Fixed column display (not editable) - adjusts to column name length
        column_label = QLabel(f"<b>{self.selected_column}</b>")
        column_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        column_label.setStyleSheet("color: #1b5e20; background: transparent; padding: 2px;")
        column_label.setWordWrap(False)
        layout.addWidget(column_label, 0)  # No max width - adjusts to content

        # Detect if column is numeric
        is_numeric = self._is_numeric_column()

        # Operator selector - conditional based on column type
        self.operator_combo = QComboBox()
        if is_numeric:
            operators = [
                "equals",
                "not equals",
                ">",
                "<",
                ">=",
                "<=",
                "between",
                "contains",
            ]
        else:
            operators = [
                "contains",
                "is",
                "not contains",
                "starts with",
                "ends with",
                "equals",
                "not equals",
            ]
        self.operator_combo.addItems(operators)
        self.operator_combo.setMinimumWidth(120)
        self.operator_combo.setMaximumWidth(150)
        self.operator_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.operator_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                background-color: white;
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: bold;
                color: #1b5e20;
            }
            QComboBox:hover {
                border: 2px solid #2e7d32;
            }
            QComboBox QAbstractItemView {
                font-family: 'Segoe UI';
                font-size: 11px;
                padding: 4px;
                selection-background-color: #4CAF50;
            }
        """
        )
        layout.addWidget(self.operator_combo, 0)

        # Value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Value...")
        self.value_input.setMinimumWidth(150)
        self.value_input.setStyleSheet(
            """
            QLineEdit {
                padding: 7px;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                background-color: white;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #2e7d32;
                background-color: #fffef0;
            }
        """
        )
        layout.addWidget(self.value_input, 1)

        # Remove button
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setMaximumWidth(36)
        self.remove_btn.setMinimumHeight(30)
        self.remove_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QPushButton:pressed {
                background-color: #ff3838;
            }
        """
        )
        self.remove_btn.clicked.connect(self.removed.emit)
        layout.addWidget(self.remove_btn, 0)

        self.setLayout(layout)

    def _is_numeric_column(self) -> bool:
        """Check if the selected column contains numeric data based on column name."""
        try:
            # Keywords that suggest numeric columns
            numeric_keywords = ['id', 'count', 'amount', 'price', 'qty', 'rate', 'value', 'number', 'total']
            col_lower = self.selected_column.lower()
            
            # If column name contains numeric keywords
            if any(keyword in col_lower for keyword in numeric_keywords):
                return True
            
            # Check if column ends with numeric patterns
            if col_lower.endswith(('_id', '_count', '_amount', '_price', '_qty', '_no', '_num')):
                return True
            
            return False
        except Exception:
            return False

    def get_filter_data(self) -> Dict[str, Any]:
        """Get the filter rule data."""
        return {
            "column": self.selected_column,  # Use fixed column
            "operator": self.operator_combo.currentText(),
            "value": self.value_input.text(),
        }


class FilterPanel(QWidget):
    """Advanced filtering panel with multiple rules."""

    filters_applied = pyqtSignal(list, str)  # filters, logic (AND/OR)

    def __init__(self):
        super().__init__()
        self.filter_rules: List[FilterRule] = []
        self.columns: List[str] = []
        self._init_ui()

    def _init_ui(self):
        """Initialize the filter panel UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(6)

        # Top section: Add filter + Logic + Search/Clear buttons
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        add_filter_label = QLabel("🔍 Add Filter:")
        add_filter_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        add_filter_label.setStyleSheet("color: #1b5e20;")
        top_layout.addWidget(add_filter_label)

        self.column_selector = QComboBox()
        self.column_selector.setMinimumWidth(140)
        self.column_selector.setMaximumWidth(180)
        self.column_selector.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.column_selector.setStyleSheet(
            """
            QComboBox {
                padding: 7px;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                background-color: white;
                font-family: 'Segoe UI';
                font-size: 10px;
                font-weight: bold;
                color: #1b5e20;
            }
            QComboBox:hover {
                border: 2px solid #2e7d32;
            }
            QComboBox QAbstractItemView {
                font-family: 'Segoe UI';
                font-size: 10px;
                padding: 4px;
                selection-background-color: #4CAF50;
            }
        """
        )

        add_filter_btn = QPushButton("➕ Add")
        add_filter_btn.setMaximumWidth(80)
        add_filter_btn.setMinimumHeight(32)
        add_filter_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        add_filter_btn.clicked.connect(self._add_filter_rule)

        top_layout.addWidget(self.column_selector)
        top_layout.addWidget(add_filter_btn)
        top_layout.addSpacing(12)

        # Logic selector (AND / OR)
        logic_label = QLabel("Logic:")
        logic_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        logic_label.setStyleSheet("color: #1b5e20;")
        top_layout.addWidget(logic_label)

        self.logic_group = QButtonGroup()

        self.and_radio = QRadioButton("AND")
        self.and_radio.setChecked(True)
        self.and_radio.setStyleSheet(
            """
            QRadioButton {
                font-family: 'Segoe UI';
                font-size: 10px;
                font-weight: bold;
                color: #1b5e20;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
        """
        )
        self.logic_group.addButton(self.and_radio, 0)

        self.or_radio = QRadioButton("OR")
        self.or_radio.setStyleSheet(
            """
            QRadioButton {
                font-family: 'Segoe UI';
                font-size: 10px;
                font-weight: bold;
                color: #1b5e20;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
        """
        )
        self.logic_group.addButton(self.or_radio, 1)

        top_layout.addWidget(self.and_radio)
        top_layout.addWidget(self.or_radio)
        top_layout.addSpacing(12)

        # Action buttons
        search_btn = QPushButton("🔎 Search")
        search_btn.setMaximumWidth(120)
        search_btn.setMinimumHeight(32)
        search_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """
        )
        search_btn.clicked.connect(self._apply_filters)

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setMaximumWidth(95)
        clear_btn.setMinimumHeight(32)
        clear_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #cc7700;
            }
        """
        )
        clear_btn.clicked.connect(self._clear_all_filters)

        top_layout.addWidget(search_btn)
        top_layout.addWidget(clear_btn)
        top_layout.addStretch()

        main_layout.addLayout(top_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #e0e0e0;")
        main_layout.addWidget(separator)

        # Filter rules layout (will hold added filters dynamically and expand the panel)
        # No container widget - directly add to main layout to save space
        self.rules_layout = QVBoxLayout()
        self.rules_layout.setContentsMargins(0, 0, 0, 0)
        self.rules_layout.setSpacing(4)
        main_layout.addLayout(self.rules_layout, 0)

        self.setLayout(main_layout)

    def set_columns(self, columns: List[str]):
        """Set available columns for filtering."""
        # Filter out _v1 and _uni columns (case-insensitive)
        self.columns = [col for col in columns if not col.lower().endswith(("_v1", "_uni"))]
        self.column_selector.clear()
        self.column_selector.addItems(self.columns)

    def _add_filter_rule(self):
        """Add a new filter rule with the selected column."""
        if not self.columns:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        selected_column = self.column_selector.currentText()
        if not selected_column:
            QMessageBox.warning(self, "No Selection", "Please select a column")
            return

        # Create rule with the selected column as fixed parameter
        rule = FilterRule(self.columns, selected_column)
        rule.removed.connect(lambda: self._remove_filter_rule(rule))
        self.filter_rules.append(rule)
        self.rules_layout.addWidget(rule)

        logger.debug(f"Added filter rule for column: {selected_column}")

    def _remove_filter_rule(self, rule: FilterRule):
        """Remove a filter rule."""
        if rule in self.filter_rules:
            self.filter_rules.remove(rule)
            self.rules_layout.removeWidget(rule)
            rule.deleteLater()
            logger.debug(f"Removed filter rule. Remaining: {len(self.filter_rules)}")

    def _apply_filters(self):
        """Apply all filters and emit signal."""
        if not self.filter_rules:
            QMessageBox.warning(self, "No Filters", "Please add at least one filter")
            return

        filters = [rule.get_filter_data() for rule in self.filter_rules]
        logic = "AND" if self.and_radio.isChecked() else "OR"

        logger.info(f"Applying {len(filters)} filters with logic: {logic}")
        self.filters_applied.emit(filters, logic)

    def _clear_all_filters(self):
        """Clear all filter rules."""
        for rule in self.filter_rules[:]:
            self._remove_filter_rule(rule)

        logger.info("All filters cleared")
        
        # Emit a special signal to reset data to original state
        self.filters_applied.emit([], "AND")
