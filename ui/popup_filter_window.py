"""
Popup Filter Window - Separate window for all filtering functionality
This keeps the main window clean and provides dedicated space for filter management
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QDialog,
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
    QScrollArea,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from typing import List, Dict, Any
from loguru import logger
from ui.unified_styles import UnifiedStyles
from ui.simple_dropdown_styler import apply_green_dropdown_style


class PopupFilterRule(QFrame):
    """Individual filter rule widget for popup window."""

    removed = pyqtSignal()

    def __init__(self, columns: List[str], rule_id: int = 0):
        super().__init__()
        self.rule_id = rule_id
        self.columns = [col for col in columns if not col.lower().endswith(("_v1", "_uni"))]
        
        # Ensure proper size for visibility
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet(
            """
            QFrame {
                border: 2px solid #e9ecef;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                padding: 12px;
                margin: 4px 0px;
                min-height: 60px;
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
        """Initialize the popup filter rule UI."""
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(8)

        # Column selector
        column_label = QLabel("Column:")
        column_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        column_label.setStyleSheet("color: #2c3e50; padding: 2px;")
        layout.addWidget(column_label)

        self.column_combo = QComboBox()
        self.column_combo.addItems(self.columns)
        self.column_combo.setMinimumWidth(120)
        self.column_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.column_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        # Apply simple green dropdown style directly
        apply_green_dropdown_style(self.column_combo)
        layout.addWidget(self.column_combo, 2)  # Give more space

        # Operator selector
        operator_label = QLabel("Operator:")
        operator_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        operator_label.setStyleSheet("color: #2c3e50; padding: 2px;")
        layout.addWidget(operator_label)

        self.operator_combo = QComboBox()
        operators = [
            "contains",
            "is",
            "not contains",
            "starts with",
            "ends with",
            "equals",
            "not equals",
            ">",
            "<",
            ">=",
            "<=",
            "between",
        ]
        self.operator_combo.addItems(operators)
        self.operator_combo.setMinimumWidth(100)
        self.operator_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.operator_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        # Apply simple green dropdown style directly
        apply_green_dropdown_style(self.operator_combo)
        layout.addWidget(self.operator_combo, 2)  # Give more space

        # Value input
        value_label = QLabel("Value:")
        value_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2c3e50; padding: 2px;")
        layout.addWidget(value_label)

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter filter value...")
        self.value_input.setMinimumWidth(140)
        self.value_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.value_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                min-height: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
            QLineEdit::placeholder {
                color: #adb5bd;
                font-style: italic;
            }
        """)
        layout.addWidget(self.value_input, 3)  # Give most space to value input

        # Remove button
        self.remove_btn = QPushButton("🗑️")
        self.remove_btn.setMaximumWidth(40)
        self.remove_btn.setMinimumHeight(28)
        self.remove_btn.setMaximumHeight(28)
        self.remove_btn.setToolTip("Remove this filter rule")
        self.remove_btn.setStyleSheet(
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
                font-size: 10px;
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
        layout.addWidget(self.remove_btn)

        self.setLayout(layout)

    def get_filter_data(self) -> Dict[str, Any]:
        """Get the filter rule data."""
        return {
            "column": self.column_combo.currentText(),
            "operator": self.operator_combo.currentText(),
            "value": self.value_input.text(),
        }


class PopupFilterWindow(QDialog):
    """Popup window for filter management."""

    filters_applied = pyqtSignal(list, str)  # filters, logic (AND/OR)

    def __init__(self, parent=None, columns: List[str] = None, current_filters: List[Dict] = None, current_logic: str = "AND"):
        super().__init__(parent)
        self.columns = columns or []
        self.filter_rules: List[PopupFilterRule] = []
        
        # Store existing filters for editing
        self.current_filters = current_filters or []
        self.current_logic = current_logic
        
        self.setWindowTitle("🔍 Advanced Filter Manager")
        self.setModal(True)
        self.resize(900, 600)
        self.setMinimumSize(800, 500)
        
        # Center on parent
        if parent:
            parent_geo = parent.geometry()
            self.move(
                parent_geo.x() + (parent_geo.width() - 900) // 2,
                parent_geo.y() + (parent_geo.height() - 600) // 2
            )
        
        self._init_ui()
        
        # Load existing filters if provided
        self._load_existing_filters()

    def _init_ui(self):
        """Initialize the popup filter window UI."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel("🔍 Advanced Filter Manager")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        # Add filter section
        add_section = QHBoxLayout()
        add_section.setSpacing(15)
        
        add_label = QLabel("Add New Filter:")
        add_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        add_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        add_section.addWidget(add_label)

        add_filter_btn = QPushButton("➕ Add Filter Rule")
        add_filter_btn.setMinimumHeight(36)
        add_filter_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #4CAF50);
            }
        """
        )
        add_filter_btn.clicked.connect(self._add_filter_rule)
        add_section.addWidget(add_filter_btn)

        add_section.addStretch()
        main_layout.addLayout(add_section)

        # Logic section
        logic_section = QHBoxLayout()
        logic_section.setSpacing(15)

        logic_label = QLabel("Filter Logic:")
        logic_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        logic_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        logic_section.addWidget(logic_label)

        self.logic_group = QButtonGroup()

        self.and_radio = QRadioButton("AND (All conditions must match)")
        self.and_radio.setChecked(True)
        self.and_radio.setStyleSheet("""
            QRadioButton {
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 600;
                color: #495057;
                spacing: 8px;
                padding: 5px;
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
        """)
        self.logic_group.addButton(self.and_radio, 0)
        logic_section.addWidget(self.and_radio)

        self.or_radio = QRadioButton("OR (Any condition can match)")
        self.or_radio.setStyleSheet("""
            QRadioButton {
                font-family: 'Segoe UI';
                font-size: 11px;
                font-weight: 600;
                color: #495057;
                spacing: 8px;
                padding: 5px;
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
        """)
        self.logic_group.addButton(self.or_radio, 1)
        logic_section.addWidget(self.or_radio)

        logic_section.addStretch()
        main_layout.addLayout(logic_section)

        # Filter rules scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMinimumHeight(300)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                background-color: #ffffff;
            }
        """)

        # Rules container
        rules_widget = QWidget()
        self.rules_layout = QVBoxLayout()
        self.rules_layout.setContentsMargins(10, 10, 10, 10)
        self.rules_layout.setSpacing(10)
        self.rules_layout.addStretch()  # Add stretch at the end
        rules_widget.setLayout(self.rules_layout)
        scroll_area.setWidget(rules_widget)
        main_layout.addWidget(scroll_area)

        # Action buttons
        button_section = QHBoxLayout()
        button_section.setSpacing(10)

        apply_btn = QPushButton("🔍 Apply Filters")
        apply_btn.setMinimumHeight(40)
        apply_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #007bff);
            }
        """
        )
        apply_btn.clicked.connect(self._apply_filters)
        button_section.addWidget(apply_btn)

        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setMinimumHeight(40)
        clear_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc3545, stop:1 #c82333);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c82333, stop:1 #dc3545);
            }
        """
        )
        clear_btn.clicked.connect(self._clear_all_filters)
        button_section.addWidget(clear_btn)

        close_btn = QPushButton("❌ Close")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c757d, stop:1 #545b62);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #545b62, stop:1 #6c757d);
            }
        """
        )
        close_btn.clicked.connect(self.close)
        button_section.addWidget(close_btn)

        main_layout.addLayout(button_section)
        self.setLayout(main_layout)

    def set_columns(self, columns: List[str]):
        """Set available columns for filtering."""
        self.columns = [col for col in columns if not col.lower().endswith(("_v1", "_uni"))]
        # Update existing rules
        for rule in self.filter_rules:
            rule.columns = self.columns
            rule.column_combo.clear()
            rule.column_combo.addItems(self.columns)

    def _add_filter_rule(self):
        """Add a new filter rule."""
        if not self.columns:
            QMessageBox.warning(self, "No Data", "No columns available for filtering")
            return

        try:
            rule = PopupFilterRule(self.columns, len(self.filter_rules))
            rule.removed.connect(lambda: self._remove_filter_rule(rule))
            self.filter_rules.append(rule)
            
            # Insert before the stretch
            self.rules_layout.insertWidget(self.rules_layout.count() - 1, rule)
            
            logger.info(f"Added popup filter rule. Total rules: {len(self.filter_rules)}")
            
        except Exception as e:
            logger.error(f"Failed to add popup filter rule: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add filter: {str(e)}")

    def _remove_filter_rule(self, rule: PopupFilterRule):
        """Remove a filter rule."""
        if rule in self.filter_rules:
            self.filter_rules.remove(rule)
            self.rules_layout.removeWidget(rule)
            rule.deleteLater()
            logger.info(f"Removed popup filter rule. Remaining: {len(self.filter_rules)}")

    def _apply_filters(self):
        """Apply all filters and emit signal."""
        if not self.filter_rules:
            QMessageBox.warning(self, "No Filters", "Please add at least one filter rule")
            return

        filters = []
        for rule in self.filter_rules:
            filter_data = rule.get_filter_data()
            if not filter_data["value"].strip():
                QMessageBox.warning(self, "Empty Value", f"Please enter a value for {filter_data['column']}")
                return
            filters.append(filter_data)

        logic = "AND" if self.and_radio.isChecked() else "OR"
        
        logger.info(f"Applying {len(filters)} filters with logic: {logic}")
        self.filters_applied.emit(filters, logic)
        
        # Show success message and close
        QMessageBox.information(self, "Filters Applied", f"Successfully applied {len(filters)} filters with {logic} logic")
        self.close()

    def _clear_all_filters(self):
        """Clear all filter rules."""
        for rule in self.filter_rules[:]:
            self._remove_filter_rule(rule)
        
        logger.info("All popup filters cleared")
        # Emit empty filters to reset data
        self.filters_applied.emit([], "AND")
    
    def _load_existing_filters(self):
        """Load existing filters into the popup for editing."""
        if not self.current_filters:
            return
        
        try:
            # Set the logic radio button
            if self.current_logic == "OR":
                self.or_radio.setChecked(True)
            else:
                self.and_radio.setChecked(True)
            
            # Load each filter rule
            for filter_data in self.current_filters:
                self._add_filter_rule()
                
                # Get the last added rule (most recently created)
                if self.filter_rules:
                    rule = self.filter_rules[-1]
                    
                    # Set the values from saved filter
                    column = filter_data.get("column", "")
                    operator = filter_data.get("operator", "")
                    value = filter_data.get("value", "")
                    
                    # Set column
                    if column and rule.column_combo.findText(column) != -1:
                        rule.column_combo.setCurrentText(column)
                    
                    # Set operator
                    if operator and rule.operator_combo.findText(operator) != -1:
                        rule.operator_combo.setCurrentText(operator)
                    
                    # Set value
                    rule.value_input.setText(value)
            
            logger.info(f"Loaded {len(self.current_filters)} existing filters with {self.current_logic} logic")
            
        except Exception as e:
            logger.error(f"Error loading existing filters: {e}")
            # If loading fails, just start with empty filters