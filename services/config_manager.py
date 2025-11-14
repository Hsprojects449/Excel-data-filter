"""
Configuration manager for application settings.
Handles reading/writing config files and environment variables.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_FILE = Path(__file__).parent.parent / "config.json"

DEFAULT_CONFIG = {
    "theme": "light",
    "recent_files": [],
    "max_preview_rows": 1000,
    "chunk_size": 50000,
    "auto_format_export": True,
    "default_export_dir": str(Path.home() / "Downloads"),
}


class ConfigManager:
    """Manages application configuration."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load config from file or return defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save_config(self) -> None:
        """Save current config to file."""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get config value by key."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value and auto-save."""
        self.config[key] = value
        self.save_config()

    def update_recent_files(self, filepath: str, max_recent: int = 10) -> None:
        """Update recent files list."""
        recent = self.config.get("recent_files", [])
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        self.config["recent_files"] = recent[:max_recent]
        self.save_config()


# Global instance
config_manager = ConfigManager()
