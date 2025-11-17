"""
Main application window using PyQt6.
Orchestrates the UI components and business logic.
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QDialog,
    QComboBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QCursor
from pathlib import Path
import polars as pl
import os

from loguru import logger
from services.config_manager import config_manager
from core.excel_reader import ExcelReader
from core.filter_engine import FilterEngine, FilterRule as EngineFilterRule
from core.exporter import ExcelExporter
from ui.preview_table import PreviewTable
from ui.unified_styles import UnifiedStyles

from ui.filter_panel import FilterPanel
from ui.simple_filter_panel import SimpleFilterPanel
from ui.sheet_selector import SheetSelectionDialog


class LoadDataThread(QThread):
    """Worker thread for loading Excel data asynchronously."""

    finished = pyqtSignal(pl.DataFrame)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)  # percentage, status message

    def __init__(self, filepath: str, sheet_name: str = None):
        super().__init__()
        self.filepath = filepath
        self.sheet_name = sheet_name

    def run(self):
        try:
            self.progress.emit(10, "Opening file...")
            reader = ExcelReader(self.filepath)
            
            self.progress.emit(30, "Reading sheet names...")
            sheet_names = reader.get_sheet_names()
            
            # Use specified sheet or first sheet as fallback
            target_sheet = self.sheet_name if self.sheet_name else (sheet_names[0] if sheet_names else None)
            
            self.progress.emit(50, f"Loading sheet '{target_sheet}'...")
            df = reader.read_sheet(target_sheet)
            
            self.progress.emit(80, "Processing data...")
            # Simulate processing time for user feedback
            self.msleep(200)
            
            self.progress.emit(100, "Complete!")
            self.finished.emit(df)
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            self.error.emit(str(e))


class ExportThread(QThread):
    """Worker thread for exporting data asynchronously."""

    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(int, str)   # percentage, status message

    def __init__(self, exporter, output_path: str, export_format: str = "excel"):
        super().__init__()
        self.exporter = exporter
        self.output_path = output_path
        self.export_format = export_format

    def run(self):
        try:
            if self.export_format == "csv":
                success = self.exporter.export_to_csv(
                    self.output_path, 
                    progress_callback=self.progress.emit
                )
            else:  # excel
                success = self.exporter.export(
                    self.output_path,
                    progress_callback=self.progress.emit
                )
            
            if success:
                self.finished.emit(True, f"Successfully exported to {Path(self.output_path).name}")
            else:
                self.finished.emit(False, "Export failed")
                
        except Exception as e:
            logger.error(f"Export thread error: {e}")
            self.finished.emit(False, f"Export error: {str(e)}")


class SheetSelectionThread(QThread):
    """Worker thread for getting sheet names from Excel file."""

    sheets_loaded = pyqtSignal(list)  # List of sheet names
    error = pyqtSignal(str)

    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath

    def run(self):
        try:
            reader = ExcelReader(self.filepath)
            sheet_names = reader.get_sheet_names()
            self.sheets_loaded.emit(sheet_names)
        except Exception as e:
            logger.error(f"Failed to get sheet names: {e}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("XLS Filter Pro")
        # Set minimum size but show maximized by default
        self.setMinimumSize(1200, 700)
        # Show maximized on startup
        self.showMaximized()
        #self.setWindowIcon(QIcon("assets/vsn_logo.jpg"))

        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "assets", "vsn_logo.jpg")

        self.setWindowIcon(QIcon(icon_path))
        
        self.current_dataframe: pl.DataFrame = None
        self.filter_engine: FilterEngine = None
        self.current_filepath: str = None
        self.available_sheets: list = []  # Store available sheet names
        self.current_sheet: str = None    # Track current sheet name
        self.excel_reader: ExcelReader = None  # Store excel reader for sheet operations
        self.sheet_cache: dict = {}  # Cache for loaded sheets data

        # Initialize UI
        self._init_ui()
        self._connect_signals()

        logger.info("Application started")

    def _init_ui(self):
        """Initialize the UI layout with sticky header and scrollable content."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - vertical: header at top, scrollable content below
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === STICKY HEADER SECTION ===
        header_widget = self._create_header_widget()
        main_layout.addWidget(header_widget)

        # Progress bar (part of header section)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                text-align: center;
                height: 15px;
                font-size: 12px;
                font-weight: bold;
                background-color: #f8f9fa;
                color: #495057;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 5px;
            }
        """
        )
        main_layout.addWidget(self.progress_bar)

        # === SCROLLABLE CONTENT SECTION ===
        scrollable_content = self._create_scrollable_content()
        main_layout.addWidget(scrollable_content, 1)  # Takes remaining space

        central_widget.setLayout(main_layout)

    def _create_header_widget(self):
        """Create the sticky header widget with toolbar."""
        # Header container
        header_widget = QWidget()
        header_widget.setFixedHeight(55)  # Fixed height for sticky header
        header_widget.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-bottom: 3px solid #2e7d32;
            }
        """
        )

        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 8, 15, 8)
        header_layout.setSpacing(15)
        header_widget.setLayout(header_layout)

        # # App Title with icon
        # title = QLabel("📊 Excel Data Filter Pro")
        # title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        # title.setFont(title_font)
        # title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # title.setStyleSheet(
        #     """
        #     QLabel {
        #         color: #ffffff;
        #         background: transparent;
        #         padding: 5px 0px;
        #         margin: 0px;
        #         font-weight: bold;
        #     }
        # """
        # )
        # header_layout.addWidget(title)

        # header_layout.addSpacing(20)

        # Open file button
        open_btn = QPushButton("📁 Open Excel File")
        open_btn.setFixedHeight(40)
        open_btn.setMinimumWidth(140)
        open_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        open_btn.clicked.connect(self._open_file)
        open_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34495e, stop:1 #2c3e50);
                border: 2px solid rgba(255, 255, 255, 0.3);
            }PushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e2833, stop:1 #2c3e50);
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """
        )
        header_layout.addWidget(open_btn)

        # Export button
        export_btn = QPushButton("💾 Export Filtered Data")
        export_btn.setFixedHeight(40)
        export_btn.setMinimumWidth(170)
        export_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        export_btn.clicked.connect(self._export_data)
        export_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #3498db);
                border: 2px solid rgba(255, 255, 255, 0.3);
                cursor: pointer;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #21618c, stop:1 #2980b9);
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
        """
        )
        header_layout.addWidget(export_btn)

        # Sheet switcher (initially hidden)
        self.sheet_label = QLabel("📄 Sheet:")
        self.sheet_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.sheet_label.setStyleSheet(
            """
            QLabel {
                color: #ffffff;
                background: transparent;
                padding: 5px 0px;
                margin: 0px;
                font-weight: bold;
            }
        """
        )
        
        self.sheet_switcher = QComboBox()
        self.sheet_switcher.setFixedHeight(32)
        self.sheet_switcher.setMinimumWidth(150)
        self.sheet_switcher.setMaximumWidth(200)
        self.sheet_switcher.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.sheet_switcher.setStyleSheet(UnifiedStyles.get_combobox_style(font_size=11, min_height=28, min_width=150))
        UnifiedStyles.apply_combobox_popup_style(self.sheet_switcher)
        self.sheet_switcher.currentTextChanged.connect(self._on_sheet_changed)
        
        # Initially hide sheet switcher (will be shown when multiple sheets are available)
        self.sheet_label.setVisible(False)
        self.sheet_switcher.setVisible(False)
        
        header_layout.addSpacing(15)
        header_layout.addWidget(self.sheet_label)
        header_layout.addWidget(self.sheet_switcher)

        header_layout.addStretch()

        # Status label
        self.status_label = QLabel("Ready to load Excel files")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #ffffff;
                padding: 8px 12px;
                margin: 0px;
                border-radius: 6px;
                font-weight: 600;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.2), stop:1 rgba(255, 255, 255, 0.1));
                border: 1px solid rgba(255, 255, 255, 0.3);
                min-width: 200px;
                text-align: center;
            }
        """
        )
        header_layout.addWidget(self.status_label)

        return header_widget

    def _create_scrollable_content(self):
        """Create the scrollable content area containing filters and preview table."""
        # Create scrollable content area for filters and table
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Enable smooth scrolling with better touch support
        scroll_area.verticalScrollBar().setSingleStep(15)  # Increased for better finger scrolling
        scroll_area.verticalScrollBar().setPageStep(200)
        scroll_area.horizontalScrollBar().setSingleStep(15)
        scroll_area.horizontalScrollBar().setPageStep(200)
        
        # Configure scroll area for optimal touch interaction
        scroll_area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Enhanced kinetic scrolling support with multiple methods
        self._enable_kinetic_scrolling(scroll_area)
        
        # Add mouse wheel support for better desktop experience
        scroll_area.wheelEvent = self._custom_wheel_event
        
        # Apply unified styling with enhanced scroll area configuration
        unified_scroll_style = """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget {
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """
        scroll_area.setStyleSheet(unified_scroll_style + UnifiedStyles.get_scrollbar_style())

        # Content widget for scroll area
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        content_widget.setMinimumWidth(800)  # Set minimum width to trigger horizontal scroll if needed
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Simple Filter Panel (just a button to open popup filter manager)
        self.filter_panel = SimpleFilterPanel()
        self.filter_panel.filters_applied.connect(self._on_filters_applied)
        self.filter_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # Start hidden until a file is loaded
        self.filter_panel.setVisible(False)
        content_layout.addWidget(self.filter_panel)

        # Initial placeholder message (shown before any file is loaded)
        self.initial_message = QLabel("📁 Select an Excel file to begin filtering.")
        self.initial_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.initial_message.setStyleSheet("""
            QLabel {
                color: #555;
                font-family: 'Segoe UI';
                font-size: 16px;
                font-weight: 600;
                padding: 40px 20px;
                border: 2px dashed #d0d0d0;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
        """)
        content_layout.addWidget(self.initial_message)

        # Preview table (below filters)
        self.preview_table = PreviewTable()
        self.preview_table.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        self.preview_table.setMinimumWidth(800)  # Ensure minimum width for horizontal scroll
        self.preview_table.setStyleSheet("""PreviewTable { background-color: #ffffff; }""")
        # Start hidden until data loaded
        self.preview_table.setVisible(False)
        content_layout.addWidget(self.preview_table, 1)
        
        # Connect edit controls from filter panel to preview table
        self.preview_table.edit_counter_label = self.filter_panel.edit_counter_label
        self.preview_table.undo_all_btn = self.filter_panel.undo_all_btn
        self.filter_panel.undo_all_btn.clicked.connect(self.preview_table.clear_edits)

        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        return scroll_area

    def _enable_kinetic_scrolling(self, scroll_area):
        """Enable kinetic scrolling with enhanced settings for smooth performance."""
        try:
            # Try QScroller first (best option for touch/trackpad)
            from PyQt6.QtWidgets import QScroller, QScrollerProperties
            scroller = QScroller.scroller(scroll_area)
            properties = scroller.scrollerProperties()
            
            # Enhanced scroll properties for better performance
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.DragStartDistance, 0.002)  
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.DragVelocitySmoothingFactor, 0.02)  
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.AxisLockThreshold, 0.5)  
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.DecelerationFactor, 0.95)
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.MinimumVelocity, 0.1)
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.MaximumVelocity, 10.0)
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.MaximumClickThroughVelocity, 0.8)
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.AcceleratingFlickMaximumTime, 0.5)
            properties.setScrollMetric(QScrollerProperties.ScrollMetric.AcceleratingFlickSpeedupFactor, 1.2)
            
            scroller.setScrollerProperties(properties)
            QScroller.grabGesture(scroll_area, QScroller.ScrollerGestureType.TouchGesture)
            QScroller.grabGesture(scroll_area, QScroller.ScrollerGestureType.LeftMouseButtonGesture)
            logger.info("Enhanced kinetic scrolling enabled with improved settings")
            
        except Exception as e:
            logger.debug(f"QScroller not available: {e}, using enhanced fallback")
            # Enhanced fallback: Improved manual scrolling support
            scroll_area.setProperty("smoothScrolling", True)
            
    def _custom_wheel_event(self, event):
        """Enhanced custom wheel event for ultra-smooth desktop scrolling."""
        # Get the scroll area reference
        scroll_area = event.widget() if hasattr(event, 'widget') else self.sender()
        if not scroll_area:
            return
            
        # Enhanced smooth scroll calculation with momentum
        base_pixels_per_step = 25  # Base scrolling sensitivity
        delta = event.angleDelta().y()
        steps = abs(delta) // 120  # Number of scroll steps
        
        # Progressive acceleration for faster scrolling
        if steps == 0:
            steps = 1
        acceleration = min(steps * 1.5, 8)  # Max 8x acceleration
        
        # Calculate smooth scroll amount with acceleration
        smooth_delta = (delta / 120) * base_pixels_per_step * acceleration
        
        # Apply smooth scrolling with bounds checking
        scrollbar = scroll_area.verticalScrollBar()
        current_value = scrollbar.value()
        new_value = max(scrollbar.minimum(), 
                       min(scrollbar.maximum(), current_value - smooth_delta))
        
        # Animate the scrolling for extra smoothness
        scrollbar.setValue(int(new_value))
        
        event.accept()

    def _on_sheet_changed(self, sheet_name: str):
        """Handle sheet selection change with caching."""
        if not sheet_name or not self.current_filepath or sheet_name == self.current_sheet:
            return
            
        # Check if we have cached data
        if sheet_name in self.sheet_cache:
            # Use cached data for instant switching
            self.status_label.setText(f"Switching to sheet '{sheet_name}'...")
            self.current_sheet = sheet_name
            self._display_sheet_data(self.sheet_cache[sheet_name], sheet_name)
            self.status_label.setText(f"✅ Sheet '{sheet_name}' loaded from cache")
        else:
            # Load the selected sheet from file and cache it
            self.status_label.setText(f"Loading sheet '{sheet_name}'...")
            self.current_sheet = sheet_name
            self._load_excel_file(self.current_filepath, sheet_name)

    def _display_sheet_data(self, dataframe, sheet_name: str):
        """Display data from a specific sheet."""
        # Set the current data
        self.current_dataframe = dataframe
        
        # Update preview table
        self.preview_table.set_data(dataframe)
        
        # Update filters for new sheet columns
        columns = dataframe.columns if hasattr(dataframe.columns, 'tolist') else dataframe.columns
        if hasattr(columns, 'tolist'):
            columns = columns.tolist()
        # Pass dataframe for numeric column detection
        self.filter_panel.set_columns(columns, dataframe)
        
        # Log success
        from loguru import logger
        logger.info(f"Displayed sheet '{sheet_name}' with {len(dataframe)} rows, {len(dataframe.columns)} columns")

    def _connect_signals(self):
        """Connect signals for threading."""
        pass

    def _open_file(self):
        """Open file dialog to select Excel file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Excel File",
            config_manager.get("default_export_dir", str(Path.home())),
            "Excel Files (*.xlsx);;All Files (*)",
        )

        if filepath:
            # Reset sheet information for new file
            self.available_sheets = []
            self.current_sheet = None
            self.sheet_switcher.clear()
            self.sheet_switcher.setVisible(False)
            self.sheet_label.setVisible(False)
            # Hide interactive panels until data loads
            self.filter_panel.setVisible(False)
            self.preview_table.setVisible(False)
            if self.initial_message:
                self.initial_message.setText("📁 Loading file... Please wait")
                self.initial_message.setVisible(True)
            
            self.current_filepath = filepath
            config_manager.update_recent_files(filepath)
            self._check_sheets_and_load(filepath)

    def _check_sheets_and_load(self, filepath: str):
        """Check sheets in file and load with sheet selection if needed."""
        self.status_label.setText("Checking available sheets...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(50)

        # Create ExcelReader for this file
        self.excel_reader = ExcelReader(filepath)

        # Start thread to get sheet names
        self.sheet_thread = SheetSelectionThread(filepath)
        self.sheet_thread.sheets_loaded.connect(self._on_sheets_loaded)
        self.sheet_thread.error.connect(self._on_sheet_load_error)
        self.sheet_thread.start()

    def _on_sheets_loaded(self, sheet_names: list):
        """Handle sheet names loaded from file."""
        self.progress_bar.setVisible(False)
        
        if not sheet_names:
            QMessageBox.warning(self, "No Sheets", "No sheets found in the Excel file.")
            self.status_label.setText("❌ No sheets found")
            return

        # Store available sheets for the switcher
        self.available_sheets = sheet_names

        # If only one sheet, load it directly
        if len(sheet_names) == 1:
            self.current_sheet = sheet_names[0]
            self.status_label.setText(f"Loading sheet '{sheet_names[0]}'...")
            self._load_excel_file(self.current_filepath, sheet_names[0])
            return

        # Multiple sheets: show selection dialog
        dialog = SheetSelectionDialog(sheet_names, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_sheet = dialog.get_selected_sheet()
            if selected_sheet:
                self.current_sheet = selected_sheet
                self.status_label.setText(f"Loading sheet '{selected_sheet}'...")
                self._load_excel_file(self.current_filepath, selected_sheet)
            else:
                self.status_label.setText("Ready to load Excel files")
        else:
            self.status_label.setText("Ready to load Excel files")

    def _auto_cache_sheets(self, sheet_names: list):
        """Automatically cache all sheets in background for fast switching."""
        # Skip if only one sheet or already cached
        if len(sheet_names) <= 1:
            return
            
        # Start caching in background
        from PyQt6.QtCore import QTimer
        
        def cache_next_sheet():
            # Find next uncached sheet
            for sheet_name in sheet_names:
                if sheet_name not in self.sheet_cache and sheet_name != self.current_sheet:
                    try:
                        # Load sheet data
                        df = self.excel_reader.read_sheet(sheet_name)
                        self.sheet_cache[sheet_name] = df
                        
                        from loguru import logger
                        logger.info(f"Cached sheet '{sheet_name}' ({len(df)} rows)")
                        
                        # Schedule next sheet
                        QTimer.singleShot(100, cache_next_sheet)
                        return
                    except Exception as e:
                        from loguru import logger
                        logger.error(f"Failed to cache sheet '{sheet_name}': {e}")
                        continue
            
            # All sheets cached, update UI
            self._setup_sheet_switcher(sheet_names)
        
        # Start caching after current sheet loads
        QTimer.singleShot(1000, cache_next_sheet)
    
    def _setup_sheet_switcher(self, sheet_names: list):
        """Setup the sheet switcher with all available sheets."""
        if len(sheet_names) > 1:
            self.sheet_switcher.clear()
            self.sheet_switcher.addItems(sheet_names)
            self.sheet_switcher.setCurrentText(self.current_sheet)
            
            # Show sheet switcher
            self.sheet_label.setVisible(True)
            self.sheet_switcher.setVisible(True)
            
            from loguru import logger
            logger.info(f"Sheet switcher setup with {len(sheet_names)} sheets")

    def _on_sheet_load_error(self, error: str):
        """Handle error loading sheet names."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Error reading file")
        QMessageBox.critical(self, "Error", f"Failed to read Excel file:\n{error}")

    def _load_excel_file(self, filepath: str, sheet_name: str = None):
        """Load Excel file in background thread."""
        sheet_display = sheet_name if sheet_name else "default sheet"
        self.status_label.setText(f"Loading {Path(filepath).name} - {sheet_display}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Update placeholder during loading
        if self.initial_message and self.initial_message.isVisible():
            self.initial_message.setText(f"⏳ Loading {Path(filepath).name}...")

        self.load_thread = LoadDataThread(filepath, sheet_name)
        self.load_thread.finished.connect(self._on_data_loaded)
        self.load_thread.error.connect(self._on_load_error)
        self.load_thread.progress.connect(self._on_load_progress)
        self.load_thread.start()

    def _on_load_progress(self, percentage: int, message: str):
        """Handle load progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(f"{message} ({percentage}%)")

    def _on_data_loaded(self, df: pl.DataFrame):
        """Handle successful data load."""
        self.current_dataframe = df
        self.filter_engine = FilterEngine(df)

        # Cache the loaded sheet data
        if self.current_sheet:
            self.sheet_cache[self.current_sheet] = df

        # Reveal interactive panels now that data exists
        if self.initial_message and self.initial_message.isVisible():
            self.initial_message.setVisible(False)
        self.filter_panel.setVisible(True)
        self.preview_table.setVisible(True)

        # Update filter panel with columns (pass dataframe so numeric detection works)
        try:
            self.filter_panel.set_columns(df.columns, dataframe=df)
        except Exception as e:
            logger.error(f"Failed to set columns with numeric detection: {e}")
            # Fallback without numeric detection if something unexpected occurs
            self.filter_panel.set_columns(df.columns)

        # Update preview table
        self.preview_table.set_data(df)

        # Setup sheet switcher and auto-cache for multi-sheet files
        if len(self.available_sheets) > 1:
            self._setup_sheet_switcher(self.available_sheets)
            # Start auto-caching other sheets
            self._auto_cache_sheets(self.available_sheets)

        stats = {
            "rows": len(df),
            "columns": len(df.columns),
        }
        self.status_label.setText(
            f"✅ Loaded {stats['rows']:,} rows × {stats['columns']} columns"
        )
        self.progress_bar.setVisible(False)

        logger.info(f"Data loaded successfully: {stats}")

    def _on_load_error(self, error: str):
        """Handle data load error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Error loading file")
        QMessageBox.critical(self, "Error", f"Failed to load file:\n{error}")
        logger.error(f"Load error: {error}")

    def _on_filters_applied(self, filters: list, logic: str):
        """Handle filters applied from filter panel."""
        # If no filters (clear was clicked), show original data
        if not filters:
            # Check if data is loaded before trying to display
            if self.current_dataframe is None:
                QMessageBox.warning(self, "No Data", "Please load data first before clearing filters")
                self.status_label.setText("❌ No data loaded")
                return
            
            self.preview_table.set_data(self.current_dataframe)
            self.status_label.setText(
                f"✅ Showing original data: {len(self.current_dataframe):,} rows"
            )
            logger.info("Filters cleared - showing original data")
            return

        if not self.filter_engine:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        try:
            self.status_label.setText("Filtering data...")
            self.progress_bar.setVisible(True)

            # Clear previous filters
            self.filter_engine.clear_filters()

            # Apply new filters
            for filter_data in filters:
                column = filter_data["column"]
                operator = filter_data["operator"]
                value = filter_data["value"]

                if not value:
                    QMessageBox.warning(
                        self, "Empty Value", f"Please enter a value for {column}"
                    )
                    return

                # Map UI operators to engine operators
                operator_map = {
                    "contains": "contains",
                    # "is": "equals",  # removed deprecated UI operator
                    "not contains": "not_contains",
                    "starts with": "starts_with",
                    "ends with": "ends_with",
                    "equals": "equals",
                    "not equals": "not_equals",
                    ">": "gt",
                    "<": "lt",
                    ">=": "gte",
                    "<=": "lte",
                    "between": "between",
                }

                engine_operator = operator_map.get(operator, "contains")
                rule = EngineFilterRule(column, engine_operator, value)
                self.filter_engine.add_filter(rule)

            # Apply all filters with specified logic
            filtered_df = self.filter_engine.apply_filters(logic=logic)

            # Update preview with filtered data
            self.preview_table.set_data(filtered_df)

            # Update statistics
            stats = self.filter_engine.get_statistics()
            self.status_label.setText(
                f"✅ Filtered: {stats['filtered_rows']:,} rows "
                f"(removed {stats['rows_removed']:,} rows) | Logic: {logic}"
            )

            logger.info(f"Filters applied: {len(filters)} rules, Logic: {logic}")

        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            QMessageBox.critical(self, "Filter Error", str(e))
            self.status_label.setText("❌ Error applying filters")
        finally:
            self.progress_bar.setVisible(False)

    def _export_data(self):
        """Export filtered data to Excel with enhanced progress feedback."""
        if self.filter_engine is None or self.current_dataframe is None:
            QMessageBox.warning(self, "Warning", "No data loaded to export")
            return

        # Get filtered data with any edits applied from preview table
        filtered_data = self.filter_engine.get_filtered_data()
        
        # Apply any edits from the preview table
        edited_data = self.preview_table.get_edited_dataframe()
        if edited_data is not None:
            # If edits exist, use edited dataframe
            # Filter it to match current filter state if filters are applied
            if self.filter_engine.applied_filters:
                # Rebuild filter on edited data
                from core.filter_engine import FilterEngine
                temp_engine = FilterEngine(edited_data)
                for rule in self.filter_engine.applied_filters:
                    temp_engine.add_filter(rule)
                filtered_data = temp_engine.apply_filters(logic=self.filter_engine.filter_logic)
            else:
                # No filters, use edited data as-is
                filtered_data = edited_data
        
        exporter = ExcelExporter(filtered_data)
        export_info = exporter.get_export_info()

        # Show export information dialog first
        info_message = (
            f"📊 Export Information:\n\n"
            f"• Rows: {export_info['rows']:,}\n"
            f"• Columns: {export_info['columns']}\n"
            f"• Estimated file size: {export_info['estimated_file_size_mb']} MB\n"
            f"• Estimated time: {export_info['estimated_export_time']}\n"
        )
        
        if export_info['is_large_dataset']:
            info_message += f"\n⚠️ This is a large dataset. Export may take some time."

        reply = QMessageBox.question(
            self,
            "Export Confirmation",
            info_message + "\n\nDo you want to proceed with the export?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Choose export format with custom buttons
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Export Format")
        msg_box.setText("Choose export format:")
        msg_box.setInformativeText("📊 Excel (.xlsx) - Full formatting\n📄 CSV - Faster export")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        # Create custom buttons
        excel_button = msg_box.addButton("📊 Excel", QMessageBox.ButtonRole.YesRole)
        csv_button = msg_box.addButton("📄 CSV", QMessageBox.ButtonRole.NoRole)
        cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.setDefaultButton(excel_button)
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == cancel_button:
            return
        
        export_format = "excel" if clicked_button == excel_button else "csv"
        file_extension = "xlsx" if export_format == "excel" else "csv"
        file_filter = f"{file_extension.upper()} Files (*.{file_extension})"

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Save {file_extension.upper()} File",
            config_manager.get("default_export_dir", str(Path.home())),
            file_filter,
        )

        if output_path:
            # Ensure correct extension
            if not output_path.lower().endswith(f".{file_extension}"):
                output_path += f".{file_extension}"

            try:
                self.status_label.setText("Starting export...")
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)

                # Start threaded export
                self.export_thread = ExportThread(exporter, output_path, export_format)
                self.export_thread.finished.connect(self._on_export_finished)
                self.export_thread.progress.connect(self._on_export_progress)
                self.export_thread.start()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export error: {str(e)}")
                logger.error(f"Export error: {e}")
                self.status_label.setText("❌ Export error")
                self.progress_bar.setVisible(False)

    def _on_export_progress(self, percentage: int, message: str):
        """Handle export progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(f"Exporting... {message}")

    def _on_export_finished(self, success: bool, message: str):
        """Handle export completion."""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(f"✅ {message}")
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"{message}\n\nFile saved successfully!"
            )
            logger.info(f"Export successful: {message}")
        else:
            self.status_label.setText(f"❌ {message}")
            QMessageBox.critical(self, "Export Failed", message)
            logger.error(f"Export failed: {message}")

    # Using default event handling; custom touch event override removed to simplify behavior.
