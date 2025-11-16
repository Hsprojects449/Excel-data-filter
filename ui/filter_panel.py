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
    QFrame,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QCursor
from typing import List, Dict, Any
from loguru import logger
from ui.unified_styles import UnifiedStyles



class FilterRule(QFrame):
    """Individual filter rule widget."""

    removed = pyqtSignal()

    def __init__(self, columns: List[str], selected_column: str, rule_id: int = 0):
        super().__init__()
        self.rule_id = rule_id
        self.columns = [col for col in columns if not col.lower().endswith(("_v1", "_uni"))]
        self.selected_column = selected_column  # Fixed column name
        
        # Ensure proper size for visibility
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet(
            """
            QFrame {
                border: 2px solid #e9ecef;
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                padding: 8px;
                margin: 2px 0px;
                min-height: 50px;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 2px solid #4CAF50;
            }
        """
        )
        self._init_ui()

    def _init_ui(self):
        """Initialize the filter rule UI - single row layout."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # Fixed column display (not editable) - adjusts to column name length
        column_label = QLabel(f"<b>{self.selected_column}</b>")
        column_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        column_label.setStyleSheet(
            """
            QLabel {
                color: #2c3e50; 
                background: transparent; 
                padding: 6px 10px;
                border-radius: 6px;
                border: 1px solid #e9ecef;
                background-color: #f8f9fa;
            }
        """
        )
        column_label.setWordWrap(False)
        layout.addWidget(column_label, 0)

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
        self.operator_combo.setMinimumWidth(130)
        self.operator_combo.setMaximumWidth(160)
        self.operator_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.operator_combo.setStyleSheet(UnifiedStyles.get_combobox_style(font_size=12, min_height=16, min_width=130))
        UnifiedStyles.apply_combobox_popup_style(self.operator_combo)
        layout.addWidget(self.operator_combo, 0)

        # Value input with unified styling
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value...")
        self.value_input.setMinimumWidth(160)
        self.value_input.setStyleSheet(UnifiedStyles.get_lineedit_style(font_size=12, min_height=16) + 
                                       """
            QLineEdit::placeholder {
                color: #adb5bd;
                font-style: italic;
            }
        """)
        layout.addWidget(self.value_input, 1)

        # Remove button
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.remove_btn.setMaximumWidth(40)
        self.remove_btn.setMinimumHeight(36)
        self.remove_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a93226, stop:1 #922b21);
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
        
        # Set size constraints - allow expansion but with reasonable limits
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(120)  # Minimum for basic functionality
        # Remove maximum height to allow filter rules to be visible
        
        self._init_ui()

    def _init_ui(self):
        """Initialize the filter panel UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Top section: Add filter + Logic + Search/Clear buttons (no fixed height)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)

        add_filter_label = QLabel("🔍 Add Filter:")
        add_filter_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        add_filter_label.setStyleSheet("color: #2c3e50; padding: 3px 0px;")
        top_layout.addWidget(add_filter_label)

        self.column_selector = QComboBox()
        self.column_selector.setMinimumWidth(160)
        self.column_selector.setMaximumWidth(200)
        self.column_selector.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.column_selector.setStyleSheet(UnifiedStyles.get_combobox_style(font_size=12, min_height=18, min_width=160))
        UnifiedStyles.apply_combobox_popup_style(self.column_selector)

        add_filter_btn = QPushButton("➕ Add Filter")
        add_filter_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        add_filter_btn.setMaximumWidth(120)
        add_filter_btn.setFixedHeight(32)  # Match header button height
        add_filter_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #1e8449);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e8449, stop:1 #196f3d);
            }
        """
        )
        add_filter_btn.clicked.connect(self._add_filter_rule)

        top_layout.addWidget(self.column_selector)
        top_layout.addWidget(add_filter_btn)
        top_layout.addSpacing(20)

        # Logic selector (AND / OR)
        logic_label = QLabel("Logic:")
        logic_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        logic_label.setStyleSheet("color: #2c3e50; padding: 3px 0px;")
        top_layout.addWidget(logic_label)

        self.logic_group = QButtonGroup()

        self.and_radio = QRadioButton("AND")
        self.and_radio.setChecked(True)
        self.and_radio.setStyleSheet(
            """
            QRadioButton {
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                color: #495057;
                spacing: 8px;
                padding: 3px 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #6c757d;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #4CAF50;
            }
        """
        )
        self.logic_group.addButton(self.and_radio, 0)

        self.or_radio = QRadioButton("OR")
        self.or_radio.setStyleSheet(
            """
            QRadioButton {
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                color: #495057;
                spacing: 8px;
                padding: 3px 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #6c757d;
            }
            QRadioButton::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #4CAF50;
            }
        """
        )
        self.logic_group.addButton(self.or_radio, 1)

        top_layout.addWidget(self.and_radio)
        top_layout.addWidget(self.or_radio)
        top_layout.addSpacing(20)

        # Action buttons
        search_btn = QPushButton("🔎 Apply Filters")
        search_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        search_btn.setMaximumWidth(140)
        search_btn.setFixedHeight(32)  # Match header button height
        search_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #21618c, stop:1 #1b4f72);
            }
        """
        )
        search_btn.clicked.connect(self._apply_filters)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clear_btn.setMaximumWidth(120)
        clear_btn.setFixedHeight(32)  # Match header button height
        clear_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a93226, stop:1 #922b21);
            }
        """
        )
        clear_btn.clicked.connect(self._clear_all_filters)

        top_layout.addWidget(search_btn)
        top_layout.addWidget(clear_btn)
        top_layout.addStretch()

        # Add top layout directly to main layout
        main_layout.addLayout(top_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(
            """
            QFrame {
                color: #e9ecef;
                border: 1px solid #e9ecef;
                margin: 8px 0px;
            }
        """
        )
        main_layout.addWidget(separator)

        # Filter rules container (expandable to show added filters)
        self.rules_layout = QVBoxLayout()
        self.rules_layout.setContentsMargins(0, 5, 0, 8)
        self.rules_layout.setSpacing(8)  # Increased spacing for better visibility
        main_layout.addLayout(self.rules_layout, 1)  # Give it stretch factor 1 to expand

        self.setLayout(main_layout)

    def set_columns(self, columns: List[str]):
        """Set available columns for filtering."""
        # Filter out _v1 and _uni columns (case-insensitive)
        self.columns = [col for col in columns if not col.lower().endswith(("_v1", "_uni"))]
        self.column_selector.clear()
        self.column_selector.addItems(self.columns)

    def _add_filter_rule(self):
        """Add a new filter rule with the selected column."""
        logger.info("🔍 Add Filter button clicked - starting to add filter rule")
        
        if not self.columns:
            logger.warning("No columns available for filtering")
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        selected_column = self.column_selector.currentText()
        logger.info(f"Selected column for filter: '{selected_column}'")
        
        if not selected_column:
            logger.warning("No column selected")
            QMessageBox.warning(self, "No Selection", "Please select a column")
            return

        try:
            # Create rule with the selected column as fixed parameter
            rule = FilterRule(self.columns, selected_column)
            rule.removed.connect(lambda: self._remove_filter_rule(rule))
            self.filter_rules.append(rule)
            
            # Ensure the rule is visible
            rule.show()
            rule.setVisible(True)
            
            # Add rule to layout
            self.rules_layout.addWidget(rule)
            
            # Force layout update
            self.rules_layout.update()
            self.updateGeometry()

            logger.info(f"✅ Successfully added filter rule for column: {selected_column}")
            logger.info(f"Total filter rules now: {len(self.filter_rules)}")
            logger.info(f"FilterRule size: {rule.size()}, visible: {rule.isVisible()}")
            
        except Exception as e:
            logger.error(f"❌ Failed to add filter rule: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add filter: {str(e)}")

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
