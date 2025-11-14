"""
Temporary file cleanup utilities.
Ensures temporary files are properly cleaned up after use.
"""

import shutil
import tempfile
from pathlib import Path
from loguru import logger


def cleanup_temp_dir(temp_dir: Path) -> None:
    """Remove temporary directory and all contents."""
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temp directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")


def get_temp_dir() -> Path:
    """Get a temporary directory for this session."""
    temp_dir = Path(tempfile.gettempdir()) / "excel_filter_app"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir
