# Implementation Plan - Lantern - Network Toolkit

## Goal Description
Build a production-quality, cross-platform Python CLI package named `lantern` (Project: Lantern - Network Toolkit) for local network diagnostics, device management, and connectivity. The tool is designed to be extensible, safe by default, and provide developer-friendly visibility into network status without requiring root privileges for basic operations.

## User Review Required
> [!IMPORTANT]
> **Framework Decision**: We are proceeding with **Typer** for the CLI framework due to its modern type hint support and excellent developer experience.
> **packaging Decision**: We will use **Poetry** for dependency management and packaging as it offers robust handling of dependencies and virtual environments.
> **Safety**: Active scanning commands (like Wi-Fi scan) will **strictly require** a `--scan` or `--active` flag and will default to non-intrusive operations.

## 1. Assumptions
- **Python Version**: Target Python 3.9+ to leverage modern typing features.
- **OS Focus**: Primary implementation and verification on **macOS**. Linux support will be best-effort using standard tools (`nmcli`, `ip`, `iw`). Windows is strictly best-effort/stubbed for v1.
- **Root Privileges**: The tool primarily runs as a standard user. If a specific sub-feature needs root (e.g., some raw socket operations, though excluded from v1), it will fail gracefully with a clear message.
- **Dependencies**: External system commands (like `airport` on Mac, `nmcli` on Linux) are expected to be present for full functionality. We will check for their existence and degrade gracefully if missing.

## 2. CLI UX Specification
The CLI will use `lantern` as the entry point.

### Global Flags
- `--json`: Output results in JSON format.
- `--verbose / -v`: Enable debug logging.
- `--quiet / -q`: Suppress non-essential output.

### Core Commands
| Command | Description | Example Output |
| :--- | :--- | :--- |
| `lantern --version` | Show version | `lantern v0.1.0` |
| `lantern --help` | Show help message | (Standard Typer help) |
| `lantern tools list` | List available tools | `wifi: Inspect Wi-Fi...` |
| `lantern diagnose` | Summary of network state | IP, Gateway, DNS, SSID check |
| `lantern interfaces` | List network interfaces | Table of IFACE, STATUS, IP |

### Wi-Fi Commands
| Command | Description | Flags |
| :--- | :--- | :--- |
| `lantern wifi info` | Current connection info | None |
| `lantern wifi signal` | Live signal sampling | `--count N`, `--interval S` |
| `lantern wifi scan` | Scan nearby networks | **Required:** `--scan` or `--active` |

### Router & Utility Commands
| Command | Description | Flags |
| :--- | :--- | :--- |
| `lantern router info` | Gateway IP & details | None |
| `lantern dns info` | DNS resolvers | None |
| `lantern speed ping` | Latency check | `--target <host>`, `--count N` |

## 3. Architecture Design

### Module Layout
```
src/lantern/
├── __init__.py
├── __main__.py       # Entry point
├── cli.py            # Typer application setup
├── config.py         # Configuration & Constants
├── core/
│   ├── __init__.py
│   ├── context.py    # Global context (verbose, json mode)
│   ├── executor.py   # Safe subprocess wrapper (CommandRunner)
│   ├── factory.py    # Platform adapter factory
│   └── output.py     # Printers (Table vs JSON)
├── platforms/
│   ├── __init__.py
│   ├── base.py       # Abstract Base Classes (PlatformAdapter)
│   ├── macos.py      # macOS implementation
│   ├── linux.py      # Linux implementation
│   └── windows.py    # Windows stub
└── tools/
    ├── __init__.py   # Tool registry
    ├── diagnose.py
    ├── interfaces.py
    ├── wifi.py
    ├── router.py
    └── utils.py
```

### Tool Interface
Each tool module will define a `register(app: Typer)` function to attach its commands.
Dynamic discovery can be achieved by importing modules in `tools/__init__.py` or using `importlib` to scan the `tools` directory (simple plugin system).

### OS Abstraction (Adapter Pattern)
We will define a `PlatformAdapter` abstract base class:
```python
class PlatformAdapter(ABC):
    @abstractmethod
    def get_interfaces(self) -> List[Interface]: ...
    @abstractmethod
    def get_wifi_info(self) -> WifiInfo: ...
    @abstractmethod
    def scan_wifi(self) -> List[WifiNetwork]: ...
    # ... other methods
```

## 4. Packaging & Safety
- **Build System**: Poetry (`pyproject.toml`).
- **Entry Point**: `lantern = "lantern.cli:app"`.
- **Safety Measures**:
    - `CommandRunner` will mask sensitive args if any (though none expected in v1).
    - `scan_wifi` implementations will explicitly check for the "confirmed" boolean flag before execution.
    - No data collection/telemetry code.

## 5. Verification Plan
See `test_plan.md` for detailed testing strategies, including fixture-based unit tests and mocked integration tests.
