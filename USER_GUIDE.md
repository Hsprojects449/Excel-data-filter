# Excel Data Filter – User Functionality Guide

This guide explains what the application does, how to use it end‑to‑end, every filter option, and the internal behaviors (numeric detection, text sanitization, export). It consolidates information from existing docs plus recent feature changes.

---
## 1. Purpose
Interactively load large Excel workbooks, inspect all columns (including multilingual Telugu text), build flexible filter rules using AND / OR logic, preview results instantly, and export cleaned data to Excel or CSV without needing Python installed (standalone `.exe`).

---
## 2. High‑Level Workflow
1. Launch the app (`python main.py` or run the built `.exe`).
2. Click “Open Excel File” and select a workbook (`.xlsx`).
3. If multiple sheets exist, choose the target sheet; background caching loads others for fast switching.
4. Scroll or horizontally pan the preview table (all original columns are shown; nothing is hidden here).
5. Click “Open Filter Manager” to add filter rules.
6. Choose columns, operators, and enter values; select **AND** (all must match) or **OR** (any may match).
7. Apply filters; preview updates and statistics display removed row count.
8. Export to Excel or CSV via “Export Filtered Data”; review size/time estimate; confirm.
9. Share the exported file (UTF‑8 and sanitized of stray control characters like `_x000D_`).

---
## 3. GUI Components
| Component | File | Description |
|----------|------|-------------|
| Main Window | `ui/main_window.py` | Orchestrates loading, sheet switching, preview, filtering, exporting. |
| Preview Table | `ui/preview_table.py` | Displays all columns; applies Telugu font fallback; sanitizes visible cell text. |
| Simple Filter Panel | `ui/simple_filter_panel.py` | Hosts buttons to open/clear filters; detects numeric columns. |
| Popup Filter Manager | `ui/popup_filter_window.py` | Add/edit multiple filter rules; choose AND/OR logic; dynamic operator list. |
| Sheet Selector | `ui/sheet_selector.py` | Modal dialog when multiple sheets exist. |

---
## 4. Loading & Sheet Handling
| Feature | Behavior |
|---------|----------|
| Async load | Uses `QThread` (`LoadDataThread`) to avoid UI freezing. |
| Multi-sheet | First selected sheet loads; others are cached in background for instant switching. |
| Sanitization | After reading, textual columns are cleaned (remove `\r`, literal `_x000D_`, control chars, trailing spaces). |
| Preview | Shows every column exactly as in source (including ones ending `_v1` / `_uni`). |

---
## 5. Column Filtering Logic
Columns ending with `_v1` or `_uni` are **excluded from being selectable for filters** (design decision). They still appear in the preview and export. (A future toggle can allow inclusion.)

### Numeric Column Detection
Implemented in `SimpleFilterPanel.set_columns()`:
1. If Polars dtype is numeric (`Int*`, `UInt*`, `Float*`) → numeric.
2. For `Utf8` columns, sample up to 200 non-empty values.
3. If ≥ 80% match regex `^-?\d+\.?\d*$` → treated as numeric.
4. Numeric columns gain extra operators: `> < >= <= between`.

### Operator Sets
| Type | Operators |
|------|-----------|
| Text (all columns) | `contains`, `not contains`, `starts with`, `ends with`, `equals`, `not equals` |
| Numeric only | `>`, `<`, `>=`, `<=`, `between` (plus all text ops) |

### Operator Semantics
| Operator | Meaning | Notes |
|----------|---------|-------|
| contains | Case-insensitive substring match | Regex style (literal=False) |
| not contains | Negated substring |  |
| starts with | Case-insensitive prefix |  |
| ends with | Case-insensitive suffix |  |
| equals | Case-insensitive exact match | Text normalized to lowercase |
| not equals | Inverse of equals |  |
| >, <, >=, <= | Numeric comparison | Column must be detected numeric |
| between | Inclusive range | Input: `min,max` (e.g., `10,25`) |

### Between Input Format
Enter two numbers separated by a comma: `start,end`
Examples: `18,30`, `3.5,7.25`, `-10,5`.
No auto-swap; order must be ascending for matches.

### AND vs OR Logic
| Logic | Effect |
|-------|-------|
| AND | Row must satisfy every rule | Intersection |
| OR | Row may satisfy any rule | Union |
The selection is read from radio buttons; `main_window._on_filters_applied()` passes the chosen logic to `FilterEngine.apply_filters(logic=...)`.

---
## 6. Filter Engine Internals
Located in `core/filter_engine.py`:
1. Each UI rule → `FilterRule` (column, operator, value).
2. Rules converted to Polars expressions (string ops cast to lowercase for case-insensitivity).
3. Numeric comparisons attempt `float()` then `int()` fallback.
4. Combined with bitwise AND (`&`) or OR (`|`) based on selected logic.
5. Statistics computed: original rows, filtered rows, removed rows, reduction percent.

---
## 7. Data Sanitization & Unicode Handling
| Stage | File | Actions |
|-------|------|---------|
| Ingestion | `core/excel_reader.py` | Removes `\r`, literal `_x000D_`, control characters; trims whitespace; normalizes line endings. |
| Preview | `ui/preview_table.py` | Calls `_sanitize_cell_value()`, applies NFC normalization, sets Telugu-friendly fonts (`Nirmala UI`, fallback). |
| Export | `core/exporter.py` | `_sanitize_value()` cleans text before writing. |
| CSV BOM | Added for Excel UTF-8 compatibility. |

Telugu script rendering: Font fallback ensures glyphs display even if default system font lacks coverage.

---
## 8. Export Process
| Feature | Behavior |
|---------|----------|
| Formats | Excel (`.xlsx` via `xlsxwriter`), CSV (`.csv`). |
| Progress | Chunked writing updates progress bar (rows processed). |
| Size Estimate | Approx = rows × cols × 7 bytes (compressed XML heuristic). |
| Large Data Optimization | Switch to `constant_memory` mode when >10k rows; reduce cell formatting for performance. |
| Column Widths | Sample up to 1000 values to infer width (capped). |
| Freeze Panes | Header row frozen for navigation. |

CSV specifics: UTF‑8 BOM added to ensure Excel opens with correct encoding for Telugu.

---
## 9. Executable Distribution
Built with PyInstaller (`excel_data_filter.spec`). Generated folder in `dist/` contains bundled Python interpreter, libraries, and assets. Target machines do **not** need Python installed. For a single-file executable, adapt the spec or use `--onefile` (trade-off: slower startup due to extraction).

---
## 10. Running From Source
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
Linux/macOS equivalent: activate venv then `python main.py`.

---
## 11. Common Usage Examples
| Goal | Steps |
|------|-------|
| Show all data again | Click “Clear All Filters” or open popup and clear. |
| Filter age between 25–40 | Add rule: column `AGE`, operator `between`, value `25,40`. |
| Find names starting with `RA` | Operator `starts with`, value `RA`. |
| Combine two possible mandal names | Two rules on `MANDAL NAME`: values `KURNOOL`, `ADONI`, select **OR**. |
| Remove blank mobile numbers | Filter `MOBILE NO` with `not equals` and leave value blank? (Instead use `contains` with digit pattern or implement future `not_null`). |

---
## 12. Logging & Diagnostics
`loguru` writes structured logs to `logs/`. Useful entries:
- Numeric detection summary (lists detected numeric columns).
- Filter application counts and logic used.
- Export progress milestones.

Enable deeper diagnostics by adjusting log level in `services/logger.py` if needed.

---
## 13. Limitations & Notes
| Area | Current Behavior | Potential Enhancement |
|------|------------------|-----------------------|
| `_v1` / `_uni` columns | Excluded from filter selection | Add user toggle in settings/UI |
| Hybrid numeric strings (`4-107B`) | Treated as text | Add parsing/normalization layer |
| Date filtering | Not specialized yet | Implement auto date operator set |
| Regex input | Uses `contains` with regex; no dedicated UI validation | Add pattern test + error surfacing |
| Size estimate | Heuristic only | Refine with sampling compression ratio |

---
## 14. Troubleshooting Quick Reference
| Symptom | Cause | Fix |
|---------|-------|-----|
| Numeric operators missing | Dataframe wasn’t passed or <80% numeric ratio | Ensure load path calls `set_columns(..., dataframe=df)` / verify column values. |
| Telugu characters boxes/garbled | Font fallback missing | Confirm Windows has `Nirmala UI`; restart app. |
| `_x000D_` still visible | Sanitization missed variant | Re-run file load; confirm source file doesn’t contain literal text. |
| OR logic acting like AND | (Fixed) missing `logic` parameter | Update to patched version. |
| Export huge estimated size | Old 50 bytes/cell heuristic | Use updated code (7 bytes per cell). |

---
## 15. Future Roadmap (Suggested)
- User toggle to include `_v1` / `_uni` columns in filtering.
- Date auto-detection with calendar picker.
- Preset save/load (JSON) for frequent filter sets.
- Dark mode & adaptive layout for small screens.
- Column statistics panel (distinct counts, min/max). 
- Advanced numeric parsing for mixed alphanumeric codes.

---
## 16. Quick Command Summary
```powershell
# Run app from source
python main.py

# Build executable (spec-based)
pyinstaller excel_data_filter.spec --clean

# Build one-file variant (optional)
pyinstaller --onefile --windowed --name ExcelDataFilter main.py
```

---
## 17. Glossary
| Term | Meaning |
|------|---------|
| AND logic | Intersection of all filter expressions. |
| OR logic | Union of filter expressions (any match). |
| Sanitization | Removal of control characters / artifacts before display/export. |
| Numeric detection | Heuristic rules that classify a column as numeric for extra operators. |

---
## 18. Getting Help
1. Review logs in `logs/` after an action.
2. Confirm environment (Python version / executable build date).
3. Reproduce with a small test file to isolate filter logic issues.

---
**End of Guide**
