# Excel Data Filter Pro - Standalone Application

## 📋 Overview
**Excel Data Filter Pro** is a powerful, user-friendly desktop application for filtering and analyzing Excel data. This standalone executable runs on any Windows system without requiring Python or other dependencies to be installed.

## ✅ **Latest Update - November 14, 2025**
- **Fixed**: Logger initialization issue for windowed applications
- **Enhanced**: Status text visibility in header with improved styling
- **Improved**: Dropdown arrow visibility across all components
- **File Size**: 137 MB (optimized with UPX compression)

## 🎯 Key Features
- **📂 Excel File Support**: Open and process .xlsx, .xls files with multiple sheets
- **🔍 Advanced Filtering**: Create complex filters with multiple conditions (AND/OR logic)
- **💾 Export Options**: Save filtered data as Excel (.xlsx) or CSV files
- **🖥️ User-Friendly Interface**: Clean, modern GUI with intuitive controls
- **⚡ High Performance**: Efficiently handles large datasets
- **📊 Data Preview**: Real-time preview of filtered results with pagination
- **🎨 Professional Design**: Polished interface with proper styling and feedback

## 📁 File Information
- **Executable Name**: `Excel_Data_Filter_Pro.exe`
- **File Size**: ~137 MB
- **Platform**: Windows (64-bit)
- **Dependencies**: None (all required libraries are included)

## 🚀 How to Use

### 1. Installation
- **No installation required!** 
- Simply download the `Excel_Data_Filter_Pro.exe` file
- Place it in any folder on your computer

### 2. Running the Application
- Double-click `Excel_Data_Filter_Pro.exe` to launch
- The application window will open in maximized view
- No additional setup or configuration needed

### 3. Basic Workflow
1. **Open File**: Click "📁 Open Excel File" to select your Excel file
2. **Choose Sheet**: Select the sheet you want to work with (if multiple sheets exist)
3. **Add Filters**: Click "🔧 Open Filter Manager" to create filtering rules
4. **Preview Results**: View filtered data in the main table
5. **Export Data**: Click "💾 Export Filtered Data" to save results

### 4. Creating Filters
1. In the Filter Manager popup:
   - Select **Column** from dropdown
   - Choose **Operator** (contains, equals, >, <, etc.)
   - Enter **Value** to filter by
   - Click **Add Filter** for additional rules
2. Use **AND/OR** logic to combine multiple filters
3. Click **Apply Filters** to see results
4. Use **View/Edit Filters** to modify existing filters

## 🔧 Filter Operators Available
- **contains**: Cell contains the specified text
- **is/equals**: Exact match
- **not contains**: Cell does not contain the text
- **starts with**: Cell begins with the text
- **ends with**: Cell ends with the text
- **>**, **<**, **>=**, **<=**: Numerical comparisons
- **not equals**: Everything except the specified value
- **between**: Value within a range

## 📊 Export Options
- **Excel Format (.xlsx)**: Maintains formatting and data types
- **CSV Format (.csv)**: Plain text, comma-separated values
- Choose format in the export dialog when saving

## 🖥️ System Requirements
- **Operating System**: Windows 10 or later (64-bit)
- **Memory**: 4GB RAM minimum (8GB recommended for large files)
- **Storage**: 200MB free space (for the application and temporary files)
- **Display**: 1024x768 minimum resolution (1920x1080 recommended)

## ⚠️ Important Notes
- **First Launch**: The application may take a few seconds to start on first run
- **Antivirus**: Some antivirus software may flag the executable - this is normal for PyInstaller-built applications
- **Large Files**: Processing very large Excel files (>100MB) may take some time
- **Temporary Files**: The application creates temporary files during processing - these are automatically cleaned up

## 🔒 Security & Privacy
- **No Internet Required**: Application works completely offline
- **No Data Collection**: Your data stays on your computer
- **File Safety**: Original files are never modified
- **Temporary Files**: Automatically cleaned up after use

## 🐛 Troubleshooting

### Application Won't Start
- Check that you have administrator rights
- Try running as administrator (right-click → "Run as administrator")
- Ensure Windows Defender or antivirus isn't blocking the file

### "File Not Found" Errors
- Ensure the Excel file path doesn't contain special characters
- Try copying the Excel file to a simpler folder path
- Check that the Excel file isn't open in another application

### Performance Issues
- Close other applications to free up memory
- Try processing smaller subsets of data
- Restart the application if it becomes unresponsive

## 📝 Usage Tips
- **Save Filters**: Create and save filter combinations for repeated use
- **Pagination**: Use the navigation controls to browse through large result sets
- **Preview Before Export**: Always preview filtered results before exporting
- **Backup Data**: Keep backups of your original Excel files before processing

## 💡 Version Information
- **Application**: Excel Data Filter Pro v1.0.0
- **Build Date**: November 2025
- **Technology**: Python 3.14 + PyQt6 (compiled to executable)

---
**Note**: This is a standalone application that includes all necessary components. No additional software installation is required.