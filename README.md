# Lantern

A powerful network toolkit CLI for developers. Get instant insights into your network configuration, diagnose connectivity issues, and manage network settings - all from the command line.

## Features

- **Network Interfaces** - List all network interfaces with IP addresses, MAC addresses, and status
- **Router Info** - View default gateway details
- **DNS Management** - View DNS servers and flush DNS cache
- **Network Diagnostics** - Comprehensive network summary with connectivity testing
- **Wi-Fi Information** - View current Wi-Fi connection details (SSID, signal strength, channel)
- **JSON Output** - All commands support `--json` for scripting and automation

## Installation

### From PyPI (coming soon)

```bash
pip install lantern-net
```

### From Source

```bash
git clone https://github.com/yourusername/lantern.git
cd lantern
pip install -e .
```

## Quick Start

```bash
# Show version
lantern --version

# List all network interfaces
lantern interfaces

# Show router/gateway information
lantern router info

# Show DNS configuration
lantern dns info

# Run comprehensive network diagnostics
lantern diagnose

# Quick diagnostics (skip connectivity test)
lantern diagnose --quick
```

## Commands

### `lantern interfaces`

List all network interfaces with their configuration.

```bash
$ lantern interfaces
                             Network Interfaces
┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Name    ┃ Type     ┃ Status ┃ IPv4 Address  ┃ MAC Address       ┃ Default ┃
┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ en0     │ wifi     │ up     │ 192.168.1.174 │ 80:a9:97:33:cb:ed │    ✓    │
│ en1     │ ethernet │ down   │ -             │ 36:c2:f0:66:c2:40 │         │
└─────────┴──────────┴────────┴───────────────┴───────────────────┴─────────┘
```

**Options:**
- `--json, -j` - Output in JSON format

### `lantern router info`

Show default gateway/router information.

```bash
$ lantern router info
╭────────────────────────────── Default Gateway ───────────────────────────────╮
│   IP Address     192.168.1.1                                                 │
│   Interface      en0                                                         │
│   MAC Address    58:96:71:f2:8f:6c                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**Options:**
- `--json, -j` - Output in JSON format

### `lantern dns info`

Show DNS configuration including servers and search domains.

```bash
$ lantern dns info
                  DNS Servers
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Address                ┃ Interface ┃ Default ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ 192.168.1.1            │ -         │    ✓    │
│ 8.8.8.8                │ -         │         │
└────────────────────────┴───────────┴─────────┘

Search Domains: local, home
```

**Options:**
- `--json, -j` - Output in JSON format

### `lantern dns flush`

Flush the local DNS cache.

```bash
$ lantern dns flush
Flushing DNS cache...
✓ DNS cache flushed successfully.
```

### `lantern diagnose`

Run comprehensive network diagnostics.

```bash
$ lantern diagnose
╭───────────────────────────── Network Interfaces ─────────────────────────────╮
│ en0  │ wifi  │ 192.168.1.174  │ ●                                            │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────── Wi-Fi ────────────────────────────────────╮
│  SSID       MyNetwork                                                        │
│  Signal     -50 dBm (Excellent)                                              │
│  Channel    36                                                               │
│  Security   WPA2 Personal                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────── Router ───────────────────────────────────╮
│  Gateway    192.168.1.1                                                      │
│  Interface  en0                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭─────────────────────────── Internet Connectivity ────────────────────────────╮
│ ● Connected  Latency: 12.3ms                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**Options:**
- `--json, -j` - Output in JSON format
- `--quick, -q` - Skip connectivity test for faster results

## JSON Output

All commands support JSON output for scripting and automation:

```bash
$ lantern interfaces --json
[
  {
    "name": "en0",
    "type": "wifi",
    "status": "up",
    "ipv4_address": "192.168.1.174",
    "mac_address": "80:a9:97:33:cb:ed",
    "is_default": true
  }
]
```

## Requirements

- **Python**: 3.11 or higher
- **Operating System**:
  - macOS (fully supported)
  - Linux (coming soon)
  - Windows (coming soon)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/lantern.git
cd lantern

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lantern --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_version.py -v
```

### Code Quality

```bash
# Run linter
ruff check src tests

# Run formatter
ruff format src tests

# Run type checker
mypy src/lantern
```

### Project Structure

```
lantern/
├── src/lantern/
│   ├── __init__.py          # Package version
│   ├── cli.py               # Main CLI application
│   ├── constants.py         # App-wide constants
│   ├── exceptions.py        # Custom exceptions
│   ├── core/
│   │   ├── context.py       # Runtime context
│   │   ├── executor.py      # Command execution
│   │   └── output.py        # Output formatting
│   ├── models/
│   │   └── network.py       # Data models
│   ├── platforms/
│   │   ├── base.py          # Platform adapter interface
│   │   ├── factory.py       # Platform detection
│   │   ├── macos.py         # macOS implementation
│   │   ├── linux.py         # Linux implementation (stub)
│   │   └── windows.py       # Windows implementation (stub)
│   └── tools/
│       ├── interfaces.py    # interfaces command
│       ├── router.py        # router commands
│       ├── dns.py           # dns commands
│       └── diagnose.py      # diagnose command
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── README.md
```

## Roadmap

- [x] Phase 1: Foundation (v0.1.0)
  - [x] Project setup and CLI skeleton
  - [x] Core infrastructure
  - [x] Platform abstraction (macOS)
  - [x] Core commands (interfaces, router, dns, diagnose)
  - [ ] Wi-Fi commands
  - [ ] Testing infrastructure
  - [ ] Documentation

- [ ] Phase 2: Delight & Virality (v1.1)
  - [ ] QR code generation for Wi-Fi sharing
  - [ ] File transfer with QR codes
  - [ ] Visual ping (sonar)
  - [ ] Network scanning

- [ ] Phase 3: LAN Mastery (v2.0)
  - [ ] Device registry
  - [ ] SSH tools
  - [ ] Wake-on-LAN
  - [ ] Smart plug integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.
