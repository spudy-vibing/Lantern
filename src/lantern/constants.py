"""Application-wide constants."""

import sys
from pathlib import Path
from typing import Final

APP_NAME: Final[str] = "lantern"

# Config paths
if sys.platform == "win32":
    CONFIG_DIR: Final[Path] = Path.home() / "AppData" / "Local" / APP_NAME
else:
    CONFIG_DIR: Final[Path] = Path.home() / ".config" / APP_NAME

CONFIG_FILE: Final[Path] = CONFIG_DIR / "config.toml"
DEVICES_FILE: Final[Path] = CONFIG_DIR / "devices.toml"
SCHEDULES_FILE: Final[Path] = CONFIG_DIR / "schedules.toml"

# Network defaults
DEFAULT_PING_COUNT: Final[int] = 5
DEFAULT_PING_TIMEOUT: Final[float] = 2.0
DEFAULT_SCAN_TIMEOUT: Final[float] = 2.0
DEFAULT_SCAN_PORTS: Final[list[int]] = [22, 80, 443, 5000, 8080, 8443]

# Platform detection
PLATFORM: Final[str] = sys.platform
IS_MACOS: Final[bool] = PLATFORM == "darwin"
IS_LINUX: Final[bool] = PLATFORM.startswith("linux")
IS_WINDOWS: Final[bool] = PLATFORM == "win32"

# Timeouts
COMMAND_TIMEOUT_MS: Final[int] = 30_000
HTTP_TIMEOUT_MS: Final[int] = 10_000
