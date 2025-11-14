"""
Simple Universal Dropdown Styling - Based on working header dropdown
No complex event filtering, just clean CSS styling that works
"""

from PyQt6.QtWidgets import QComboBox
from loguru import logger

class SimpleDropdownStyler:
    """Simple dropdown styling that just works - no complexity."""
    
    @classmethod
    def apply_green_dropdown_style(cls, combo_box: QComboBox, is_header: bool = False):
        """Apply simple green dropdown styling that works reliably."""
        
        if is_header:
            # Header style - light gray/white
            style = """
                QComboBox {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                    color: #2c3e50;
                    border: 2px solid rgba(255, 255, 255, 0.8);
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    min-height: 16px;
                }
                QComboBox:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                    border: 2px solid rgba(255, 255, 255, 1.0);
                }
                QComboBox:focus {
                    border: 2px solid #4CAF50;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid rgba(255, 255, 255, 0.8);
                    border-top-right-radius: 3px;
                    border-bottom-right-radius: 3px;
                }
                QComboBox::down-arrow {
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid #333333;
                }
                QComboBox::down-arrow:hover {
                    border-top-color: white;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    border: 2px solid #4CAF50;
                    selection-background-color: #4CAF50;
                    selection-color: white;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 6px 8px;
                    border: none;
                    outline: none;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #4CAF50;
                    color: white;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #4CAF50;
                    color: white;
                }
            """
        else:
            # Regular dropdown style - green theme
            style = """
                QComboBox {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                    color: #2c3e50;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 10px;
                    min-height: 16px;
                }
                QComboBox:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                    border: 1px solid #4CAF50;
                }
                QComboBox:focus {
                    border: 2px solid #4CAF50;
                }
                QComboBox:on {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e9ecef, stop:1 #dee2e6);
                    border: 2px solid #4CAF50;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #ddd;
                    border-top-right-radius: 3px;
                    border-bottom-right-radius: 3px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f8f9fa);
                }
                QComboBox::drop-down:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                }
                QComboBox::down-arrow {
                    width: 0;
                    height: 0;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 6px solid #333333;
                }
                QComboBox::down-arrow:hover {
                    border-top-color: #4CAF50;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    border: 2px solid #4CAF50;
                    selection-background-color: #4CAF50;
                    selection-color: white;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 6px 10px;
                    border: none;
                    outline: none;
                    min-height: 20px;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #4CAF50;
                    color: white;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #4CAF50;
                    color: white;
                }
            """
        
        try:
            combo_box.setStyleSheet(style)
            logger.info(f"✅ Applied simple dropdown style to {combo_box}")
        except Exception as e:
            logger.error(f"Failed to apply dropdown style: {e}")

# Convenience functions
def apply_header_dropdown_style(combo_box: QComboBox):
    """Apply header dropdown style (gray/white)."""
    SimpleDropdownStyler.apply_green_dropdown_style(combo_box, is_header=True)

def apply_green_dropdown_style(combo_box: QComboBox):
    """Apply regular green dropdown style."""
    SimpleDropdownStyler.apply_green_dropdown_style(combo_box, is_header=False)