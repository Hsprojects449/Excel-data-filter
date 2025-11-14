"""
Logging configuration using loguru.
Provides structured, colorized logging for the application.
"""

import sys
from pathlib import Path
from loguru import logger

# Configure log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Add console handler with color only if stdout is available
if sys.stdout is not None:
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        colorize=True,
    )
else:
    # For windowed applications without console, add a null handler or stderr fallback
    try:
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",  # Only log errors when no console available
            colorize=False,
        )
    except:
        # If stderr is also not available, just use file logging
        pass

# Add file handler for persistence
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="500 MB",
    retention="7 days",
)

# Export logger instance
__all__ = ["logger"]
