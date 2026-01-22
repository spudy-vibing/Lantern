# Technical Implementation Plan - Lantern

## Executive Summary

This document provides a step-by-step technical implementation plan for building Lantern, a network toolkit CLI. The plan is organized into 5 phases, each broken into detailed steps with specific deliverables, code patterns, and acceptance criteria.

**Estimated Scope**: ~50-60 commands across 5 phases
**Architecture**: Async-first Python CLI with plugin-ready design
**Target**: macOS primary, Linux secondary, Windows stubbed

---

## Progress Tracker

### Overall Progress

| Phase | Status | Progress | Started | Completed |
|-------|--------|----------|---------|-----------|
| Phase 1: Foundation | In Progress | 4/7 steps | 2025-01-22 | - |
| Phase 2: Delight & Virality | Not Started | 0/5 steps | - | - |
| Phase 3: LAN Mastery | Not Started | 0/6 steps | - | - |
| Phase 4: Observability | Not Started | 0/4 steps | - | - |
| Phase 5: Pro Tools | Not Started | 0/3 steps | - | - |

### Phase 1: Foundation (V1.0)

| Step | Description | Status | Notes |
|------|-------------|--------|-------|
| 1.1 | Project Bootstrap | [x] Complete | Completed 2025-01-22 |
| 1.2 | Core Infrastructure | [x] Complete | Completed 2025-01-22 |
| 1.3 | Platform Abstraction | [x] Complete | Completed 2025-01-22 |
| 1.4 | Core Commands | [x] Complete | Completed 2025-01-22 |
| 1.5 | Wi-Fi Commands | [ ] Not Started | |
| 1.6 | Testing Infrastructure | [ ] Not Started | |
| 1.7 | Documentation & Polish | [ ] Not Started | |

### Phase 2: Delight & Virality (V1.1)

| Step | Description | Status | Notes |
|------|-------------|--------|-------|
| 2.1 | QR Code Infrastructure | [ ] Not Started | |
| 2.2 | File Transfer | [ ] Not Started | |
| 2.3 | Network Utilities | [ ] Not Started | |
| 2.4 | Visual Ping | [ ] Not Started | |
| 2.5 | Network Scan | [ ] Not Started | |

### Phase 3: LAN Mastery (V2.0)

| Step | Description | Status | Notes |
|------|-------------|--------|-------|
| 3.1 | Configuration System | [ ] Not Started | |
| 3.2 | Device Registry | [ ] Not Started | |
| 3.3 | SSH Tools | [ ] Not Started | |
| 3.4 | Power Management | [ ] Not Started | |
| 3.5 | Smart Plug Integration | [ ] Not Started | |
| 3.6 | Web & Service Tools | [ ] Not Started | |

### Phase 4: Observability (V2.1)

| Step | Description | Status | Notes |
|------|-------------|--------|-------|
| 4.1 | Network Watcher | [ ] Not Started | |
| 4.2 | Bandwidth Monitor | [ ] Not Started | |
| 4.3 | TUI Dashboard | [ ] Not Started | |
| 4.4 | Power Scheduling | [ ] Not Started | |

### Phase 5: Pro Tools (V3.0)

| Step | Description | Status | Notes |
|------|-------------|--------|-------|
| 5.1 | Advanced Diagnostics | [ ] Not Started | |
| 5.2 | Developer Tools | [ ] Not Started | |
| 5.3 | Plugin SDK | [ ] Not Started | |

---

## Changelog

Track significant updates to this implementation plan and the codebase.

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2024-XX-XX | 0.0.0 | Initial plan created | - |
| 2025-01-22 | 0.1.0 | Step 1.1 Project Bootstrap complete | Claude |
| 2025-01-22 | 0.1.0 | Step 1.2 Core Infrastructure complete | Claude |
| 2025-01-22 | 0.1.0 | Step 1.3 Platform Abstraction complete | Claude |
| 2025-01-22 | 0.1.0 | Step 1.4 Core Commands complete | Claude |

---

## Build Log

Use this section to track daily/weekly progress notes.

### Week 1
```
Date:
Focus:
Completed:
-
Blockers:
-
Next:
-
```

### Week 2
```
Date:
Focus:
Completed:
-
Blockers:
-
Next:
-
```

### Week 3
```
Date:
Focus:
Completed:
-
Blockers:
-
Next:
-
```

---

## Technical Stack (Final Decisions)

| Component | Choice | Version | Rationale |
|-----------|--------|---------|-----------|
| Python | 3.11+ | ^3.11 | Built-in `tomllib`, faster async, better errors |
| CLI Framework | Typer | ^0.9.0 | Type hints, auto-help, modern DX |
| Output | Rich | ^13.0.0 | Tables, colors, progress, TUI components |
| Async HTTP | httpx | ^0.27.0 | Modern, async-native, connection pooling |
| Smart Plugs | python-kasa | ^0.6.0 | Best maintained, fully async |
| Config Read | tomllib | stdlib | Built into Python 3.11+ |
| Config Write | tomli-w | ^1.0.0 | Minimal, TOML spec compliant |
| QR Codes | qrcode | ^7.4.0 | Mature, terminal output support |
| Testing | pytest | ^8.0.0 | Standard, extensible |
| Async Testing | pytest-asyncio | ^0.23.0 | Native async test support |
| HTTP Mocking | respx | ^0.20.0 | httpx-native mocking |
| Linting | ruff | ^0.3.0 | Fast, comprehensive |
| Type Checking | mypy | ^1.8.0 | Strict mode |

---

## Project Structure

```
lantern/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint, test, type check
│       └── release.yml               # PyPI publishing
├── src/
│   └── lantern/
│       ├── __init__.py               # Version, public API
│       ├── __main__.py               # python -m lantern
│       ├── cli.py                    # Main Typer app
│       ├── config.py                 # Configuration management
│       ├── constants.py              # App-wide constants
│       ├── exceptions.py             # Custom exceptions
│       ├── models/
│       │   ├── __init__.py
│       │   ├── device.py             # Device, PowerConfig models
│       │   ├── network.py            # Interface, WifiInfo, etc.
│       │   └── results.py            # Command result models
│       ├── core/
│       │   ├── __init__.py
│       │   ├── context.py            # Runtime context
│       │   ├── executor.py           # Async subprocess runner
│       │   ├── output.py             # Output formatters
│       │   └── registry.py           # Device registry
│       ├── platforms/
│       │   ├── __init__.py
│       │   ├── base.py               # PlatformAdapter ABC
│       │   ├── factory.py            # Platform detection
│       │   ├── macos.py              # macOS implementation
│       │   ├── linux.py              # Linux implementation
│       │   └── windows.py            # Windows stub
│       ├── tools/                    # CLI commands
│       │   ├── __init__.py
│       │   ├── diagnose.py
│       │   ├── interfaces.py
│       │   ├── wifi/
│       │   ├── router.py
│       │   ├── dns.py
│       │   ├── power/
│       │   └── ...
│       ├── services/                 # Reusable services
│       │   ├── __init__.py
│       │   ├── ping.py
│       │   ├── arp.py
│       │   ├── mdns.py
│       │   ├── wol.py
│       │   └── smart_plugs/
│       └── utils/
│           ├── __init__.py
│           ├── network.py
│           └── formatting.py
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── macos/
│   │   └── linux/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── README.md
```

---

# PHASE 1: Foundation (V1.0)

**Goal**: Working CLI skeleton with core network diagnostics on macOS.
**Deliverables**: 8 commands, platform abstraction, testing infrastructure

---

## Step 1.1: Project Bootstrap

**Deliverables**: Empty project with all tooling configured

### 1.1.1 Initialize Project Structure

Create the directory structure:

```bash
mkdir -p lantern
cd lantern
mkdir -p src/lantern/{models,core,platforms,tools,services,utils}
mkdir -p src/lantern/tools/wifi
mkdir -p src/lantern/services/smart_plugs
mkdir -p tests/{unit,integration,fixtures/{macos,linux}}
mkdir -p .github/workflows
```

### 1.1.2 Create pyproject.toml

```toml
[project]
name = "lantern-cli"
version = "0.1.0"
description = "A powerful network toolkit for developers"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
keywords = ["network", "cli", "diagnostics", "wifi", "toolkit"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: System :: Networking",
]

dependencies = [
    "typer>=0.9.0,<1.0.0",
    "rich>=13.0.0,<14.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "respx>=0.20.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]
power = [
    "python-kasa>=0.6.0",
    "httpx>=0.27.0",
]
all = [
    "lantern-cli[dev,power]",
]

[project.scripts]
lantern = "lantern.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/lantern"]

[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["lantern"]

[tool.mypy]
python_version = "3.11"
strict = true
files = ["src/lantern"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-ra -q --cov=lantern --cov-report=term-missing"

[tool.coverage.run]
source = ["src/lantern"]
branch = true
```

### 1.1.3 Create Initial Module Files

**src/lantern/__init__.py**:
```python
"""Lantern - A powerful network toolkit for developers."""
__version__ = "0.1.0"
__app_name__ = "lantern"
```

**src/lantern/__main__.py**:
```python
"""Allow running as python -m lantern."""
from lantern.cli import app
if __name__ == "__main__":
    app()
```

### 1.1.4 Create CI Workflow

**.github/workflows/ci.yml**:
```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: ruff check src tests
      - run: ruff format --check src tests
      - run: mypy src/lantern

  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, ubuntu-latest]
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov-report=xml
```

### 1.1.5 Acceptance Criteria
- [ ] Virtual environment created with Python 3.11+
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `lantern --version` outputs version
- [ ] `ruff check src tests` passes
- [ ] `mypy src/lantern` passes

---

## Step 1.2: Core Infrastructure

**Deliverables**: Exceptions, constants, context, executor, output utilities

### 1.2.1 Exceptions Module

**src/lantern/exceptions.py**:
```python
"""Custom exceptions for Lantern."""

class LanternError(Exception):
    """Base exception for all Lantern errors."""
    def __init__(self, message: str, hint: str | None = None) -> None:
        self.message = message
        self.hint = hint
        super().__init__(message)

class CommandNotFoundError(LanternError):
    """Raised when a required system command is not found."""
    def __init__(self, command: str, install_hint: str | None = None) -> None:
        self.command = command
        super().__init__(
            f"Command not found: {command}",
            hint=install_hint or f"Please install '{command}' to use this feature.",
        )

class CommandExecutionError(LanternError):
    """Raised when a command execution fails."""
    def __init__(self, command: str, return_code: int, stderr: str | None = None) -> None:
        self.command = command
        self.return_code = return_code
        self.stderr = stderr
        super().__init__(f"Command failed with exit code {return_code}: {command}", hint=stderr)

class PlatformNotSupportedError(LanternError):
    """Raised when the current platform is not supported."""
    def __init__(self, platform: str, feature: str | None = None) -> None:
        msg = f"Platform not supported: {platform}"
        if feature:
            msg = f"Feature '{feature}' not supported on {platform}"
        super().__init__(msg)

class DeviceNotFoundError(LanternError):
    """Raised when a device is not found in the registry."""
    def __init__(self, device_name: str) -> None:
        super().__init__(
            f"Device not found: {device_name}",
            hint="Use 'lantern devices' to see available devices.",
        )

class ConfigurationError(LanternError):
    """Raised when there's a configuration issue."""
    pass

class NetworkError(LanternError):
    """Raised for network-related errors."""
    pass
```

### 1.2.2 Constants Module

**src/lantern/constants.py**:
```python
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
```

### 1.2.3 Context Module

**src/lantern/core/context.py**:
```python
"""Runtime context for Lantern commands."""
from dataclasses import dataclass, field
from typing import Any
from rich.console import Console

@dataclass
class Context:
    """Runtime context passed to all commands."""
    console: Console = field(default_factory=Console)
    verbose: bool = False
    quiet: bool = False
    json_output: bool = False
    no_color: bool = False

    def debug(self, message: str) -> None:
        if self.verbose and not self.quiet:
            self.console.print(f"[dim]DEBUG: {message}[/dim]")

    def info(self, message: str) -> None:
        if not self.quiet and not self.json_output:
            self.console.print(message)

    def success(self, message: str) -> None:
        if not self.quiet and not self.json_output:
            self.console.print(f"[green]✓[/green] {message}")

    def warning(self, message: str) -> None:
        if not self.quiet and not self.json_output:
            self.console.print(f"[yellow]⚠[/yellow] {message}")

    def error(self, message: str, hint: str | None = None) -> None:
        if not self.json_output:
            self.console.print(f"[red]✗[/red] {message}")
            if hint:
                self.console.print(f"[dim]  Hint: {hint}[/dim]")

    def output(self, data: Any) -> None:
        if self.json_output:
            import json
            self.console.print_json(json.dumps(data, default=str))
        else:
            self.console.print(data)

_context: Context | None = None

def get_context() -> Context:
    global _context
    if _context is None:
        _context = Context()
    return _context

def set_context(ctx: Context) -> None:
    global _context
    _context = ctx
```

### 1.2.4 Command Executor

**src/lantern/core/executor.py**:
```python
"""Async subprocess execution with safety measures."""
import asyncio
import shutil
from dataclasses import dataclass
from lantern.constants import COMMAND_TIMEOUT_MS
from lantern.exceptions import CommandExecutionError, CommandNotFoundError

@dataclass
class CommandResult:
    """Result of a command execution."""
    command: str
    args: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.return_code == 0

    @property
    def output(self) -> str:
        return self.stdout.strip()

class CommandExecutor:
    """Async command executor with safety features."""

    # Allowlist of commands that can be executed
    ALLOWED_COMMANDS: set[str] = {
        # macOS
        "networksetup", "scutil", "ipconfig", "system_profiler",
        "airport", "arp", "netstat", "route", "ping", "traceroute",
        "host", "nslookup", "dig", "dscacheutil", "sw_vers",
        "sysctl", "lsof", "defaults", "security",
        # Linux
        "nmcli", "ip", "iw", "iwconfig", "iwlist", "ss",
        "resolvectl", "systemd-resolve", "hostnamectl", "uname",
        "cat", "hostname",
        # Cross-platform
        "ssh", "ssh-copy-id", "curl", "wget",
    }

    def __init__(self, timeout_ms: int = COMMAND_TIMEOUT_MS) -> None:
        self.timeout_ms = timeout_ms

    @staticmethod
    def find_command(name: str) -> str | None:
        return shutil.which(name)

    @staticmethod
    def command_exists(name: str) -> bool:
        return shutil.which(name) is not None

    async def run(
        self,
        command: str,
        *args: str,
        timeout_ms: int | None = None,
        check: bool = True,
    ) -> CommandResult:
        """Execute a command asynchronously."""
        base_command = command.split("/")[-1]
        if base_command not in self.ALLOWED_COMMANDS:
            raise CommandNotFoundError(command, f"Command '{base_command}' is not allowed.")

        full_path = self.find_command(command)
        if full_path is None:
            raise CommandNotFoundError(command)

        timeout = (timeout_ms or self.timeout_ms) / 1000.0

        try:
            process = await asyncio.create_subprocess_exec(
                full_path, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            result = CommandResult(
                command=command,
                args=args,
                return_code=process.returncode or 0,
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else "",
            )

            if check and not result.success:
                raise CommandExecutionError(
                    f"{command} {' '.join(args)}",
                    result.return_code,
                    result.stderr or result.stdout,
                )
            return result

        except asyncio.TimeoutError:
            raise CommandExecutionError(
                f"{command} {' '.join(args)}", -1, f"Command timed out after {timeout}s"
            )

# Default executor instance
executor = CommandExecutor()
```

### 1.2.5 Output Utilities

**src/lantern/core/output.py**:
```python
"""Output formatting utilities."""
import json
from typing import Any, Sequence
from rich.console import Console
from rich.table import Table

def print_table(
    console: Console,
    columns: Sequence[str],
    rows: Sequence[Sequence[Any]],
    title: str | None = None,
) -> None:
    """Print a formatted table."""
    table = Table(title=title, show_header=True, header_style="bold")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)

def format_bytes(num_bytes: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes //= 1024
    return f"{num_bytes:.1f} PB"

def format_latency(ms: float) -> str:
    """Format latency with color coding."""
    if ms < 20:
        return f"[green]{ms:.1f}ms[/green]"
    elif ms < 100:
        return f"[yellow]{ms:.1f}ms[/yellow]"
    return f"[red]{ms:.1f}ms[/red]"

def format_status(online: bool) -> str:
    """Format online/offline status."""
    return "[green]● Online[/green]" if online else "[red]○ Offline[/red]"
```

### 1.2.6 Acceptance Criteria
- [ ] All core modules import without errors
- [ ] CommandExecutor runs basic commands (ping, etc.)
- [ ] Context properly manages state
- [ ] Output utilities format data correctly

---

## Step 1.3: Platform Abstraction Layer

**Deliverables**: Network models, platform base class, macOS adapter

### 1.3.1 Network Models

**src/lantern/models/network.py**:
```python
"""Network-related data models."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class InterfaceType(str, Enum):
    ETHERNET = "ethernet"
    WIFI = "wifi"
    LOOPBACK = "loopback"
    BRIDGE = "bridge"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"

class InterfaceStatus(str, Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class NetworkInterface:
    """Represents a network interface."""
    name: str
    type: InterfaceType
    status: InterfaceStatus
    mac_address: Optional[str] = None
    ipv4_address: Optional[str] = None
    ipv4_netmask: Optional[str] = None
    ipv6_address: Optional[str] = None
    mtu: Optional[int] = None
    is_default: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "status": self.status.value,
            "mac_address": self.mac_address,
            "ipv4_address": self.ipv4_address,
            "ipv4_netmask": self.ipv4_netmask,
            "ipv6_address": self.ipv6_address,
            "mtu": self.mtu,
            "is_default": self.is_default,
        }

@dataclass
class WifiInfo:
    """Current Wi-Fi connection information."""
    ssid: str
    bssid: Optional[str] = None
    channel: Optional[int] = None
    frequency: Optional[int] = None
    rssi: Optional[int] = None
    noise: Optional[int] = None
    tx_rate: Optional[float] = None
    security: Optional[str] = None
    interface: Optional[str] = None

    @property
    def signal_quality(self) -> Optional[int]:
        """Convert RSSI to quality percentage (0-100)."""
        if self.rssi is None:
            return None
        return int(min(max(2 * (self.rssi + 100), 0), 100))

    def to_dict(self) -> dict:
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "channel": self.channel,
            "rssi": self.rssi,
            "signal_quality": self.signal_quality,
            "tx_rate": self.tx_rate,
            "security": self.security,
        }

@dataclass
class WifiNetwork:
    """A Wi-Fi network found during scanning."""
    ssid: str
    bssid: str
    channel: int
    rssi: int
    security: str
    is_current: bool = False

    def to_dict(self) -> dict:
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "channel": self.channel,
            "rssi": self.rssi,
            "security": self.security,
            "is_current": self.is_current,
        }

@dataclass
class RouterInfo:
    """Router/gateway information."""
    ip_address: str
    interface: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "ip_address": self.ip_address,
            "interface": self.interface,
            "mac_address": self.mac_address,
            "hostname": self.hostname,
        }

@dataclass
class DnsServer:
    """DNS server information."""
    address: str
    interface: Optional[str] = None
    is_default: bool = False

    def to_dict(self) -> dict:
        return {"address": self.address, "is_default": self.is_default}

@dataclass
class DnsInfo:
    """DNS configuration information."""
    servers: list[DnsServer] = field(default_factory=list)
    search_domains: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "servers": [s.to_dict() for s in self.servers],
            "search_domains": self.search_domains,
        }

@dataclass
class PingResult:
    """Result of a ping operation."""
    host: str
    ip_address: Optional[str] = None
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss_percent: float = 0.0
    min_ms: Optional[float] = None
    avg_ms: Optional[float] = None
    max_ms: Optional[float] = None

    @property
    def success(self) -> bool:
        return self.packets_received > 0

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "ip_address": self.ip_address,
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "packet_loss_percent": self.packet_loss_percent,
            "min_ms": self.min_ms,
            "avg_ms": self.avg_ms,
            "max_ms": self.max_ms,
            "success": self.success,
        }
```

### 1.3.2 Platform Base Class

**src/lantern/platforms/base.py**:
```python
"""Abstract base class for platform adapters."""
from abc import ABC, abstractmethod
from typing import Optional
from lantern.models.network import (
    DnsInfo, NetworkInterface, PingResult, RouterInfo, WifiInfo, WifiNetwork
)

class PlatformAdapter(ABC):
    """Abstract base class for platform-specific implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the platform name."""
        ...

    @abstractmethod
    async def get_interfaces(self) -> list[NetworkInterface]:
        """Get all network interfaces."""
        ...

    @abstractmethod
    async def get_default_interface(self) -> Optional[NetworkInterface]:
        """Get the default network interface."""
        ...

    @abstractmethod
    async def get_wifi_info(self) -> Optional[WifiInfo]:
        """Get current Wi-Fi connection info."""
        ...

    @abstractmethod
    async def get_wifi_interface(self) -> Optional[str]:
        """Get the name of the Wi-Fi interface."""
        ...

    @abstractmethod
    async def scan_wifi(self) -> list[WifiNetwork]:
        """Scan for available Wi-Fi networks."""
        ...

    @abstractmethod
    async def get_router_info(self) -> Optional[RouterInfo]:
        """Get default gateway/router info."""
        ...

    @abstractmethod
    async def get_dns_info(self) -> DnsInfo:
        """Get DNS configuration."""
        ...

    @abstractmethod
    async def ping(self, host: str, count: int = 5, timeout: float = 2.0) -> PingResult:
        """Ping a host."""
        ...

    @abstractmethod
    async def get_arp_table(self) -> list[tuple[str, str]]:
        """Get ARP table as list of (IP, MAC) tuples."""
        ...

    @abstractmethod
    async def flush_dns_cache(self) -> bool:
        """Flush the DNS cache."""
        ...

    async def get_wifi_password(self, ssid: str) -> Optional[str]:
        """Get saved Wi-Fi password for an SSID."""
        return None
```

### 1.3.3 Platform Factory

**src/lantern/platforms/factory.py**:
```python
"""Platform adapter factory."""
from lantern.constants import IS_LINUX, IS_MACOS, IS_WINDOWS, PLATFORM
from lantern.exceptions import PlatformNotSupportedError
from lantern.platforms.base import PlatformAdapter

def get_platform_adapter() -> PlatformAdapter:
    """Get the appropriate platform adapter for the current OS."""
    if IS_MACOS:
        from lantern.platforms.macos import MacOSAdapter
        return MacOSAdapter()
    elif IS_LINUX:
        from lantern.platforms.linux import LinuxAdapter
        return LinuxAdapter()
    elif IS_WINDOWS:
        from lantern.platforms.windows import WindowsAdapter
        return WindowsAdapter()
    else:
        raise PlatformNotSupportedError(PLATFORM)

_adapter: PlatformAdapter | None = None

def get_adapter() -> PlatformAdapter:
    """Get the cached platform adapter."""
    global _adapter
    if _adapter is None:
        _adapter = get_platform_adapter()
    return _adapter
```

### 1.3.4 macOS Adapter

**src/lantern/platforms/macos.py** - Full implementation with parsing for:
- `networksetup -listallhardwareports` for interfaces
- `airport -I` for Wi-Fi info
- `airport -s` for Wi-Fi scan
- `route -n get default` for gateway
- `scutil --dns` for DNS
- `ping` for connectivity
- `arp -a` for ARP table

(Full implementation ~400 lines - see separate file)

### 1.3.5 Linux/Windows Stubs

Minimal stubs that raise `PlatformNotSupportedError` for all methods.

### 1.3.6 Acceptance Criteria
- [ ] Platform detection works on macOS, Linux, Windows
- [ ] macOS adapter returns real interface data
- [ ] macOS Wi-Fi parsing handles edge cases
- [ ] Stubs raise appropriate errors

---

## Step 1.4: Core Commands

**Deliverables**: `interfaces`, `router info`, `dns info`, `diagnose`

### 1.4.1 Tool Registration Pattern

**src/lantern/tools/__init__.py**:
```python
"""Tool registration and discovery."""
from typing import Callable
import typer

_tool_registrations: list[Callable[[typer.Typer], None]] = []

def register_tool(func: Callable[[typer.Typer], None]) -> Callable[[typer.Typer], None]:
    """Decorator to register a tool's setup function."""
    _tool_registrations.append(func)
    return func

def register_all_tools(app: typer.Typer) -> None:
    """Register all discovered tools with the main app."""
    from lantern.tools import diagnose, dns, interfaces, router
    for register_func in _tool_registrations:
        register_func(app)
```

### 1.4.2 Command Implementation Pattern

Each command follows this pattern:

```python
"""Command module."""
import asyncio
import typer
from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.tools import register_tool

def _run_command() -> None:
    """Sync wrapper for async command."""
    asyncio.run(_command_async())

async def _command_async() -> None:
    """Async command implementation."""
    ctx = get_context()
    adapter = get_adapter()

    # Get data
    data = await adapter.some_method()

    # Output based on format
    if ctx.json_output:
        ctx.output(data.to_dict())
    else:
        # Rich formatting
        ctx.console.print(...)

@register_tool
def register(app: typer.Typer) -> None:
    @app.command("command-name")
    def command_name() -> None:
        """Command description."""
        _run_command()
```

### 1.4.3 Implement Commands

- **interfaces.py**: List network interfaces
- **router.py**: Show gateway info (`lantern router info`)
- **dns.py**: Show DNS servers and flush cache (`lantern dns info`, `lantern dns flush`)
- **diagnose.py**: Comprehensive network summary

### 1.4.4 Acceptance Criteria
- [ ] `lantern interfaces` lists all interfaces
- [ ] `lantern router info` shows gateway
- [ ] `lantern dns info` shows DNS servers
- [ ] `lantern diagnose` shows comprehensive summary
- [ ] All commands support `--json` flag

---

## Step 1.5: Wi-Fi Commands

**Deliverables**: `wifi info`, `wifi signal`, `wifi scan`

### 1.5.1 Wi-Fi Subcommand Group

**src/lantern/tools/wifi/__init__.py**:
```python
"""Wi-Fi commands."""
import typer
from lantern.tools import register_tool
from lantern.tools.wifi import info, signal, scan

wifi_app = typer.Typer(help="Wi-Fi commands.")

@register_tool
def register(app: typer.Typer) -> None:
    info.register(wifi_app)
    signal.register(wifi_app)
    scan.register(wifi_app)
    app.add_typer(wifi_app, name="wifi")
```

### 1.5.2 Wi-Fi Info

Shows current connection: SSID, signal strength, channel, security.

### 1.5.3 Wi-Fi Signal

Live sampling loop with sparkline visualization:
```
Signal: ▂▃▅▇█▇▅▃▂▃▅  -52 dBm (Good)
```

### 1.5.4 Wi-Fi Scan

**Safety**: Requires explicit `--scan` flag to perform active scanning.

### 1.5.5 Acceptance Criteria
- [ ] `lantern wifi info` shows current connection
- [ ] `lantern wifi signal` shows live signal
- [ ] `lantern wifi scan` requires `--scan` flag
- [ ] `lantern wifi scan --scan` lists networks

---

## Step 1.6: Testing Infrastructure

**Deliverables**: Test fixtures, unit tests, integration tests

### 1.6.1 Capture Test Fixtures

Create files in `tests/fixtures/macos/`:
- `airport_info.txt` - Output of `airport -I`
- `airport_scan.txt` - Output of `airport -s`
- `networksetup_ports.txt` - Output of `networksetup -listallhardwareports`
- `scutil_dns.txt` - Output of `scutil --dns`
- `route_default.txt` - Output of `route -n get default`
- `ping_output.txt` - Output of `ping -c 5 8.8.8.8`

### 1.6.2 Conftest with Fixtures

**tests/conftest.py**:
```python
"""Shared test fixtures."""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from lantern.core.executor import CommandExecutor, CommandResult

FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def macos_fixtures() -> dict[str, str]:
    """Load macOS fixture files."""
    fixtures = {}
    macos_dir = FIXTURES_DIR / "macos"
    for f in macos_dir.glob("*.txt"):
        fixtures[f.stem] = f.read_text()
    return fixtures

@pytest.fixture
def mock_executor(macos_fixtures: dict[str, str]) -> CommandExecutor:
    """Create executor with mocked responses."""
    executor = CommandExecutor()
    original_run = executor.run

    async def mock_run(command: str, *args: str, **kwargs) -> CommandResult:
        # Map commands to fixtures
        fixture_map = {
            ("airport", "-I"): "airport_info",
            ("airport", "-s"): "airport_scan",
            ("networksetup", "-listallhardwareports"): "networksetup_ports",
            ("scutil", "--dns"): "scutil_dns",
        }
        key = (command.split("/")[-1], args[0] if args else "")
        fixture_name = fixture_map.get(key)

        if fixture_name and fixture_name in macos_fixtures:
            return CommandResult(
                command=command,
                args=args,
                return_code=0,
                stdout=macos_fixtures[fixture_name],
                stderr="",
            )
        return await original_run(command, *args, **kwargs)

    executor.run = mock_run
    return executor
```

### 1.6.3 Unit Tests

**tests/unit/test_parsers.py** - Test parsing logic with fixtures
**tests/unit/test_models.py** - Test model methods
**tests/unit/test_executor.py** - Test command execution

### 1.6.4 Integration Tests

**tests/integration/test_cli.py** - Test CLI commands with mocked adapters

### 1.6.5 Acceptance Criteria
- [ ] 80%+ code coverage
- [ ] All parsers tested with fixtures
- [ ] CLI commands tested with mocked data
- [ ] Tests pass on macOS and Linux CI

---

## Step 1.7: Documentation & Polish

**Deliverables**: README, help text, error messages

### 1.7.1 README.md

Include:
- Installation instructions
- Quick start examples
- Command reference
- Platform support matrix

### 1.7.2 Help Text

Every command has:
- Clear description
- Usage examples
- Flag documentation

### 1.7.3 Error Messages

- User-friendly messages
- Actionable hints
- Platform-specific suggestions

### 1.7.4 Acceptance Criteria
- [ ] README has installation and usage
- [ ] All commands have help text
- [ ] Errors include hints
- [ ] `lantern --help` is comprehensive

---

# PHASE 2: Delight & Virality (V1.1)

## Step 2.1: QR Code Infrastructure
- Add `qrcode` dependency
- `lantern qr "text"` - General QR generator
- `lantern share` - Wi-Fi QR code

## Step 2.2: File Transfer
- `lantern drop <file>` - One-shot HTTP server with QR
- `lantern serve <dir>` - Persistent HTTP server

## Step 2.3: Network Utilities
- `lantern whoami` - Public IP and geo
- `lantern port <port>` - Port checker

## Step 2.4: Visual Ping
- `lantern sonar <host>` - Sparkline ping visualization

## Step 2.5: Network Scan
- `lantern scan` - ARP + mDNS discovery
- OUI database for vendor lookup

---

# PHASE 3: LAN Mastery (V2.0)

## Step 3.1: Configuration System
- Config file loading/saving
- `~/.config/lantern/config.toml`

## Step 3.2: Device Registry
- `devices.toml` schema
- `lantern devices` commands
- Device CRUD operations

## Step 3.3: SSH Tools
- `lantern ssh list/add/connect`
- `lantern tunnel`

## Step 3.4: Power Management
- `lantern wake` - Wake-on-LAN
- `lantern shutdown` - Remote shutdown
- `lantern power on/off`

## Step 3.5: Smart Plug Integration
- Kasa adapter
- Shelly adapter
- `lantern plug` commands

## Step 3.6: Web & Service Tools
- `lantern web` commands
- `lantern services` - mDNS browser

---

# PHASE 4: Observability (V2.1)

## Step 4.1: Network Watcher
- `lantern watch` - Event monitoring

## Step 4.2: Bandwidth Monitor
- `lantern bw` - Interface bandwidth

## Step 4.3: TUI Dashboard
- Add `textual` dependency
- `lantern dashboard`

## Step 4.4: Power Scheduling
- `lantern daemon` - Background service
- `lantern power schedule`

---

# PHASE 5: Pro Tools (V3.0)

## Step 5.1: Advanced Diagnostics
- `lantern trace` - Traceroute
- `lantern ssl` - Cert checker
- `lantern probe` - HTTP healthcheck

## Step 5.2: Developer Tools
- `lantern catch` - Request bin
- `lantern hosts` - Hosts file manager

## Step 5.3: Plugin SDK
- Plugin interface design
- `lantern init` - Plugin scaffold

---

# Appendix A: Testing Patterns

## Fixture-Based Testing
All platform-specific parsing is tested with captured output fixtures.

## Mocking Strategy
- `CommandExecutor.run()` - Mock for unit tests
- `respx` - Mock HTTP for API tests
- `pytest-asyncio` - Async test support

## Coverage Targets
- Unit tests: 90%+
- Integration tests: 80%+
- Overall: 85%+

---

# Appendix B: Error Handling

## Exception Hierarchy
```
LanternError
├── CommandNotFoundError
├── CommandExecutionError
├── PlatformNotSupportedError
├── DeviceNotFoundError
├── ConfigurationError
└── NetworkError
```

## User-Facing Errors
- Always include actionable hints
- Suggest platform-specific solutions
- Never expose raw stack traces

---

# Appendix C: Async Patterns

## Command Pattern
```python
def sync_wrapper() -> None:
    asyncio.run(async_implementation())

async def async_implementation() -> None:
    # Actual work here
    pass
```

## Concurrent Operations
```python
results = await asyncio.gather(
    adapter.get_interfaces(),
    adapter.get_router_info(),
    adapter.get_dns_info(),
)
```

---

# Appendix D: Release Checklist

## Pre-Release
- [ ] All tests pass
- [ ] Coverage meets targets
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] README updated

## Release
- [ ] Tag created
- [ ] GitHub release published
- [ ] PyPI package uploaded

## Post-Release
- [ ] Homebrew formula updated (if applicable)
- [ ] Documentation site updated (if applicable)

---

# Appendix E: Quick Reference - Status Markers

Use these markers when updating the progress tracker:

## Status Values

| Marker | Meaning |
|--------|---------|
| `[ ] Not Started` | Work has not begun |
| `[~] In Progress` | Currently being worked on |
| `[x] Complete` | Finished and tested |
| `[!] Blocked` | Cannot proceed - see notes |
| `[-] Skipped` | Intentionally skipped |

## Progress Update Template

When completing a step, update the tracker table:

```markdown
| 1.1 | Project Bootstrap | [x] Complete | Completed 2024-XX-XX |
```

## Milestone Checklist

Before marking a phase complete:

- [ ] All steps marked complete
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Version bumped (if releasing)

---

# Appendix F: File Checklist

Track which files have been created:

## Phase 1 Files

### Core Structure
- [ ] `pyproject.toml`
- [ ] `src/lantern/__init__.py`
- [ ] `src/lantern/__main__.py`
- [ ] `src/lantern/cli.py`
- [ ] `src/lantern/constants.py`
- [ ] `src/lantern/exceptions.py`

### Core Modules
- [ ] `src/lantern/core/__init__.py`
- [ ] `src/lantern/core/context.py`
- [ ] `src/lantern/core/executor.py`
- [ ] `src/lantern/core/output.py`

### Models
- [ ] `src/lantern/models/__init__.py`
- [ ] `src/lantern/models/network.py`

### Platforms
- [ ] `src/lantern/platforms/__init__.py`
- [ ] `src/lantern/platforms/base.py`
- [ ] `src/lantern/platforms/factory.py`
- [ ] `src/lantern/platforms/macos.py`
- [ ] `src/lantern/platforms/linux.py`
- [ ] `src/lantern/platforms/windows.py`

### Tools (Commands)
- [ ] `src/lantern/tools/__init__.py`
- [ ] `src/lantern/tools/interfaces.py`
- [ ] `src/lantern/tools/router.py`
- [ ] `src/lantern/tools/dns.py`
- [ ] `src/lantern/tools/diagnose.py`
- [ ] `src/lantern/tools/wifi/__init__.py`
- [ ] `src/lantern/tools/wifi/info.py`
- [ ] `src/lantern/tools/wifi/signal.py`
- [ ] `src/lantern/tools/wifi/scan.py`

### Tests
- [ ] `tests/__init__.py`
- [ ] `tests/conftest.py`
- [ ] `tests/unit/test_models.py`
- [ ] `tests/unit/test_parsers.py`
- [ ] `tests/unit/test_executor.py`
- [ ] `tests/integration/test_cli.py`

### Fixtures
- [ ] `tests/fixtures/macos/airport_info.txt`
- [ ] `tests/fixtures/macos/airport_scan.txt`
- [ ] `tests/fixtures/macos/networksetup_ports.txt`
- [ ] `tests/fixtures/macos/scutil_dns.txt`
- [ ] `tests/fixtures/macos/route_default.txt`
- [ ] `tests/fixtures/macos/ping_output.txt`

### CI/CD
- [ ] `.github/workflows/ci.yml`
- [ ] `.github/workflows/release.yml`

### Documentation
- [ ] `README.md`
- [ ] `CHANGELOG.md`
- [ ] `LICENSE`
- [ ] `.gitignore`
