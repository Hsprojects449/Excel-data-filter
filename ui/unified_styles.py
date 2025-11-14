"""
Unified UI Styles Module
Provides consistent styling across all UI components in the Excel Data Filter application.
"""

class UnifiedStyles:
    """Centralized styling for consistent UI appearance."""
    
    # Color palette
    PRIMARY_COLOR = "#4CAF50"
    PRIMARY_HOVER = "#45a049"
    PRIMARY_ACTIVE = "#3d8b40"
    
    BACKGROUND_WHITE = "#ffffff"
    BACKGROUND_LIGHT = "#f8f9fa"
    BACKGROUND_SUBTLE = "#f5f7fa"
    
    BORDER_DEFAULT = "#e9ecef"
    BORDER_HOVER = "#4CAF50"
    BORDER_FOCUS = "#4CAF50"
    
    TEXT_PRIMARY = "#495057"
    TEXT_SECONDARY = "#6c757d"
    TEXT_WHITE = "#ffffff"
    
    # Shadow and gradients
    DROPDOWN_GRADIENT = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d4d4d4, stop:1 #bbb)"
    DROPDOWN_HOVER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #45a049)"
    HEADER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #45a049)"
    
    @classmethod
    def get_combobox_style(cls, font_size=12, min_height=20, min_width=120):
        """Get standardized QComboBox styling with reliable arrow indicators."""
        return f"""
            QComboBox {{
                padding: 8px 35px 8px 12px;
                border: 2px solid {cls.BORDER_DEFAULT};
                border-radius: 8px;
                background-color: {cls.BACKGROUND_WHITE};
                font-family: 'Segoe UI';
                font-size: {font_size}px;
                font-weight: 500;
                color: {cls.TEXT_PRIMARY};
                min-height: {min_height}px;
                min-width: {min_width}px;
                selection-background-color: transparent;
            }}
            QComboBox:hover {{
                border: 2px solid {cls.BORDER_HOVER};
                background-color: {cls.BACKGROUND_LIGHT};
            }}
            QComboBox:focus {{
                border: 2px solid {cls.BORDER_FOCUS};
                background-color: {cls.BACKGROUND_WHITE};
                outline: none;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border-left: 2px solid {cls.BORDER_DEFAULT};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background: {cls.DROPDOWN_GRADIENT};
            }}
            QComboBox::drop-down:hover {{
                background: {cls.DROPDOWN_HOVER_GRADIENT};
                border-left-color: {cls.PRIMARY_COLOR};
            }}
            QComboBox::down-arrow {{
                width: 0px;
                height: 0px;
                border: none;
                background: none;
            }}
            QComboBox QAbstractItemView {{
                font-family: 'Segoe UI';
                font-size: {font_size}px;
                padding: 4px;
                background-color: {cls.BACKGROUND_WHITE};
                border: 2px solid {cls.BORDER_DEFAULT};
                border-radius: 8px;
                outline: none;
                alternate-background-color: transparent;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border: none;
                margin: 1px;
                border-radius: 4px;
                background-color: transparent;
                color: {cls.TEXT_PRIMARY};
            }}
        """
    
    @classmethod
    def get_spinbox_style(cls, font_size=12, min_height=20, min_width=100):
        """Get standardized QSpinBox styling."""
        return f"""
            QSpinBox {{
                padding: 8px 30px 8px 12px;
                border: 2px solid {cls.BORDER_DEFAULT};
                border-radius: 8px;
                background-color: {cls.BACKGROUND_WHITE};
                font-family: 'Segoe UI';
                font-size: {font_size}px;
                font-weight: 500;
                color: {cls.TEXT_PRIMARY};
                min-height: {min_height}px;
                min-width: {min_width}px;
                selection-background-color: {cls.PRIMARY_COLOR};
            }}
            QSpinBox:hover {{
                border: 2px solid {cls.BORDER_HOVER};
                background-color: {cls.BACKGROUND_LIGHT};
            }}
            QSpinBox:focus {{
                border: 2px solid {cls.BORDER_FOCUS};
                background-color: {cls.BACKGROUND_WHITE};
                outline: none;
            }}
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 25px;
                border-left: 2px solid {cls.BORDER_DEFAULT};
                border-top-right-radius: 6px;
                background: {cls.DROPDOWN_GRADIENT};
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 25px;
                border-left: 2px solid {cls.BORDER_DEFAULT};
                border-bottom-right-radius: 6px;
                background: {cls.DROPDOWN_GRADIENT};
            }}
            QSpinBox::up-button:hover {{
                background: {cls.DROPDOWN_HOVER_GRADIENT};
                border-left-color: {cls.PRIMARY_COLOR};
            }}
            QSpinBox::down-button:hover {{
                background: {cls.DROPDOWN_HOVER_GRADIENT};
                border-left-color: {cls.PRIMARY_COLOR};
            }}
            QSpinBox::up-arrow {{
                width: 0;
                height: 0;
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid #333333;
            }}
            QSpinBox::down-arrow {{
                width: 0;
                height: 0;
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
            }}
            QSpinBox::up-arrow:hover {{
                border-bottom-color: {cls.PRIMARY_COLOR};
            }}
            QSpinBox::down-arrow:hover {{
                border-top-color: {cls.PRIMARY_COLOR};
            }}
        """
    
    @classmethod
    def get_button_style(cls, font_size=12, padding="8px 16px"):
        """Get standardized button styling."""
        return f"""
            QPushButton {{
                background: {cls.HEADER_GRADIENT};
                color: {cls.TEXT_WHITE};
                border: none;
                border-radius: 8px;
                padding: {padding};
                font-family: 'Segoe UI';
                font-size: {font_size}px;
                font-weight: 600;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.PRIMARY_HOVER}, stop:1 {cls.PRIMARY_ACTIVE});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {cls.PRIMARY_ACTIVE}, stop:1 #2e7d32);
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
        """
    
    @classmethod
    def get_lineedit_style(cls, font_size=12, min_height=20):
        """Get standardized QLineEdit styling."""
        return f"""
            QLineEdit {{
                padding: 8px 12px;
                border: 2px solid {cls.BORDER_DEFAULT};
                border-radius: 8px;
                background-color: {cls.BACKGROUND_WHITE};
                font-family: 'Segoe UI';
                font-size: {font_size}px;
                color: {cls.TEXT_PRIMARY};
                min-height: {min_height}px;
                selection-background-color: {cls.PRIMARY_COLOR};
            }}
            QLineEdit:hover {{
                border: 2px solid {cls.BORDER_HOVER};
                background-color: {cls.BACKGROUND_LIGHT};
            }}
            QLineEdit:focus {{
                border: 2px solid {cls.BORDER_FOCUS};
                background-color: {cls.BACKGROUND_WHITE};
                outline: none;
            }}
        """
    
    @classmethod 
    def get_scrollbar_style(cls):
        """Get standardized scrollbar styling."""
        return f"""
            QScrollBar:vertical {{
                background-color: {cls.BACKGROUND_LIGHT};
                width: 16px;
                border-radius: 8px;
                border: 1px solid {cls.BORDER_DEFAULT};
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 30px;
                border: 1px solid #b0b0b0;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #a0a0a0;
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: #808080;
            }}
            QScrollBar:horizontal {{
                background-color: {cls.BACKGROUND_LIGHT};
                height: 16px;
                border-radius: 8px;
                border: 1px solid {cls.BORDER_DEFAULT};
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background-color: #c0c0c0;
                border-radius: 6px;
                min-width: 30px;
                border: 1px solid #b0b0b0;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: #a0a0a0;
            }}
            QScrollBar::handle:horizontal:pressed {{
                background-color: #808080;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: transparent;
                height: 0px;
                width: 0px;
            }}
        """