"""
Unified UI Styles Module
Provides consistent styling across all UI components in the Excel Data Filter application.
"""

from PyQt6.QtWidgets import QComboBox, QListView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os

class UnifiedStyles:
    """Centralized styling for consistent UI appearance."""
    
    # Color palette
    PRIMARY_COLOR = "#4CAF50"
    PRIMARY_HOVER = "#45a049"
    PRIMARY_ACTIVE = "#3d8b40"

    BACKGROUND_WHITE = "#ffffff"
    BACKGROUND_LIGHT = "#f8f9fa"

    # Border and text colors
    BORDER_DEFAULT = "#888"
    BORDER_HOVER = "#4CAF50"
    BORDER_FOCUS = "#388E3C"
    TEXT_PRIMARY = "#222"
    TEXT_WHITE = "#fff"

    # Gradients
    DROPDOWN_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e8e8e8, stop:1 #d0d0d0)"
    DROPDOWN_HOVER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f0f0f0, stop:1 #e0e0e0)"
    HEADER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #45a049)"

    @staticmethod
    def _asset_path(filename: str) -> str:
        """Return absolute normalized path to an asset inside ui/assets.

        Uses the directory of this file so it works both in dev and when frozen
        by PyInstaller (assets are bundled alongside this module under ui/assets).
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, 'assets', filename)
        return path.replace('\\', '/')
    @classmethod
    def get_combobox_style(cls, font_size=12, min_height=20, min_width=120):
        """Get standardized QComboBox styling with proper triangular arrow indicators."""
        # Calculate padding based on size - tighter for smaller controls
        v_padding = 2 if min_height < 20 else 4
        h_padding = 6 if min_width < 80 else 8
        down_arrow = cls._asset_path('arrow_down.svg')
        return f"""
        QComboBox {{
            padding: {v_padding}px 18px {v_padding}px {h_padding}px;
            border: 1px solid {cls.BORDER_DEFAULT};
            border-radius: 6px;
            background-color: {cls.BACKGROUND_WHITE};
            font-family: 'Segoe UI';
            font-size: {font_size}px;
            font-weight: 500;
            color: {cls.TEXT_PRIMARY};
            height: {min_height}px;
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
            subcontrol-position: right center;
            width: 18px;
            border: 1px solid #c0c0c0;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #e8e8e8, stop:1 #d0d0d0);
            margin-right: 2px;
            border-radius: 2px;
            padding: 0;
        }}
        QComboBox::drop-down:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f0f0f0, stop:1 #e0e0e0);
            border-color: #4CAF50;
            padding: 0;
        }}
        QComboBox::drop-down:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #c0c0c0, stop:1 #a0a0a0);
        }}
        QComboBox::down-arrow {{
            image: url("{down_arrow}");
            width: 12px;
            height: 8px;
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
            background-color: white;
            color: {cls.TEXT_PRIMARY};
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {cls.PRIMARY_COLOR} !important;
            color: white !important;
            border-radius: 4px;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: {cls.PRIMARY_COLOR} !important;
            color: white !important;
        }}
        QComboBox QAbstractItemView::item:!hover:!selected {{
            background-color: white !important;
            color: {cls.TEXT_PRIMARY} !important;
        }}
        """
    
    @classmethod
    def apply_combobox_popup_style(cls, combo_box: QComboBox):
        """Apply hover/selection styling directly to a combobox's popup view.

        This avoids hierarchy/focus issues where `QComboBox QAbstractItemView`
        selectors may not apply to the separate popup window.
        Only the popup is styled; the combobox itself is untouched.
        """
        popup_style = f"""
        QListView {{
            background-color: {cls.BACKGROUND_WHITE};
            border: 2px solid {cls.BORDER_HOVER};
            outline: none;
        }}
        QListView::item {{
            padding: 6px 10px;
            border: none;
            background-color: {cls.BACKGROUND_WHITE};
            color: {cls.TEXT_PRIMARY};
        }}
        QListView::item:hover {{
            background-color: {cls.PRIMARY_COLOR};
            color: {cls.TEXT_WHITE};
        }}
        QListView::item:selected {{
            background-color: {cls.PRIMARY_COLOR};
            color: {cls.TEXT_WHITE};
        }}
        QTreeView {{
            background-color: {cls.BACKGROUND_WHITE};
            border: 2px solid {cls.BORDER_HOVER};
            outline: none;
        }}
        QTreeView::item {{
            padding: 6px 10px;
            border: none;
            background-color: {cls.BACKGROUND_WHITE};
            color: {cls.TEXT_PRIMARY};
        }}
        QTreeView::item:hover {{
            background-color: {cls.PRIMARY_COLOR};
            color: {cls.TEXT_WHITE};
        }}
        QTreeView::item:selected {{
            background-color: {cls.PRIMARY_COLOR};
            color: {cls.TEXT_WHITE};
        }}
        """
        try:
            list_view = QListView(combo_box)
            list_view.setUniformItemSizes(True)
            list_view.setStyleSheet(popup_style)
            combo_box.setView(list_view)
        except Exception:
            # Fallback to styling existing view if setView fails
            combo_box.view().setStyleSheet(popup_style)
    
    @classmethod
    def get_spinbox_style(cls, font_size=12, min_height=20, min_width=100):
        """Get standardized QSpinBox styling with SVG arrows."""
        # Calculate padding based on size - tighter for smaller controls
        v_padding = 2 if min_height < 20 else 8
        h_padding = 6 if min_width < 80 else 12
        button_width = 20 if min_width < 80 else 30
        up_arrow = cls._asset_path('arrow_up.svg')
        down_arrow = cls._asset_path('arrow_down.svg')
        return f"""
            QSpinBox {{
                padding: {v_padding}px {button_width}px {v_padding}px {h_padding}px;
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
                width: {button_width}px;
                border-left: 2px solid {cls.BORDER_DEFAULT};
                border-top-right-radius: 6px;
                background: {cls.DROPDOWN_GRADIENT};
                padding: 0;
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: {button_width}px;
                border-left: 2px solid {cls.BORDER_DEFAULT};
                border-bottom-right-radius: 6px;
                background: {cls.DROPDOWN_GRADIENT};
                padding: 0;
            }}
            QSpinBox::up-button:hover {{
                background: {cls.DROPDOWN_HOVER_GRADIENT};
                border-left-color: {cls.PRIMARY_COLOR};
                padding: 0;
            }}
            QSpinBox::down-button:hover {{
                background: {cls.DROPDOWN_HOVER_GRADIENT};
                border-left-color: {cls.PRIMARY_COLOR};
                padding: 0;
            }}
            QSpinBox::up-arrow {{
                image: url("{up_arrow}");
                width: 12px;
                height: 8px;
            }}
            QSpinBox::down-arrow {{
                image: url("{down_arrow}");
                width: 12px;
                height: 8px;
            }}
            QSpinBox::up-arrow:hover {{
                filter: brightness(1.2);
            }}
            QSpinBox::down-arrow:hover {{
                filter: brightness(1.2);
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
    
    @staticmethod
    def apply_arrow_to_combobox(combo_box: QComboBox):
        """Add a visible down arrow indicator to combobox using QPushButton overlay trick."""
        # PyQt6's CSS arrow rendering is broken, so we'll make the drop-down area
        # visually obvious by modifying the combobox stylesheet with explicit styling
        current_sheet = combo_box.styleSheet()
        
        # Add a clear down arrow indicator using stylesheet with explicit content positioning
        arrow_sheet = current_sheet + """
        QComboBox::down-arrow {
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid black;
            background: transparent;
        }
        """
        combo_box.setStyleSheet(arrow_sheet)
    
    @staticmethod
    def style_combobox_with_arrow(combo_box: QComboBox):
        """Add visual arrow indicator to combobox by setting specific stylesheet."""
        # Since ::down-arrow doesn't work in PyQt6, use a different approach
        # Style the entire drop-down area to be obviously clickable
        style = """
            QComboBox {
                background: white;
                padding-right: 16px;
            }
            QComboBox::drop-down {
                background: #f0f0f0;
                border-left: 1px solid #ddd;
            }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #000;
            }
        """
        combo_box.setStyleSheet(style)
    
    @staticmethod
    def add_arrow_label_to_combobox(combo_box: QComboBox):
        """Add a visual arrow indicator label to combobox (alternative approach)."""
        # This method can be called after creation to add a visible arrow
        pass