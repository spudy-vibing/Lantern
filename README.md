# Lantern

A powerful network toolkit CLI for developers. Get instant insights into your network configuration, diagnose connectivity issues, and manage network settings - all from the command line.

## Features

- **Network Interfaces** - List all network interfaces with IP addresses, MAC addresses, and status
- **Router Info** - View default gateway details and MAC address
- **DNS Management** - View DNS servers, search domains, and flush DNS cache
- **Wi-Fi Tools** - View connection details, monitor signal strength in real-time, scan for networks
- **Network Diagnostics** - Comprehensive network summary with connectivity testing
- **JSON Output** - All commands support `--json` for scripting and automation

## Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS (fully supported), Linux and Windows coming soon

## Installation

### Prerequisites

1. **Check Python version** (must be 3.11+):
   ```bash
   python3 --version
   ```

2. **Install Python 3.11+** if needed:
   - macOS: `brew install python@3.11`
   - Or download from [python.org](https://www.python.org/downloads/)

### Option 1: Install from PyPI (Recommended)

```bash
pip install lantern-net
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/spudy-vibing/Lantern.git
cd Lantern

# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

### Verify Installation

```bash
lantern --version
```

## Quick Start

```bash
# Get a quick overview of your network
lantern diagnose

# List all network interfaces
lantern interfaces

# Check your Wi-Fi connection
lantern wifi info

# Monitor Wi-Fi signal strength in real-time
lantern wifi signal
```

## Commands Reference

### Network Interfaces

List all network interfaces with their configuration.

```bash
lantern interfaces
```

**Example Output:**
```
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

---

### Router Information

Show default gateway/router information.

```bash
lantern router info
```

**Example Output:**
```
╭────────────────────────────── Default Gateway ───────────────────────────────╮
│   IP Address     192.168.1.1                                                 │
│   Interface      en0                                                         │
│   MAC Address    58:96:71:f2:8f:6c                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**Options:**
- `--json, -j` - Output in JSON format

---

### DNS Commands

#### View DNS Configuration

```bash
lantern dns info
```

**Example Output:**
```
                  DNS Servers
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ Address                ┃ Interface ┃ Default ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ 192.168.1.1            │ en0       │    ✓    │
│ 8.8.8.8                │ -         │         │
└────────────────────────┴───────────┴─────────┘

Search Domains: local, home
```

#### Flush DNS Cache

Clear the local DNS resolver cache to force fresh lookups:

```bash
lantern dns flush
```

---

### Wi-Fi Commands

#### View Current Connection

```bash
lantern wifi info
```

**Example Output:**
```
╭────────────────────────────── Wi-Fi Connection ──────────────────────────────╮
│   SSID        MyNetwork                                                      │
│   Signal      -52 dBm (Excellent)                                            │
│   Channel     36 (5 GHz)                                                     │
│   TX Rate     867.0 Mbps                                                     │
│   Security    WPA2 Personal                                                  │
│   Interface   en0                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
```

#### Monitor Signal Strength

Watch your Wi-Fi signal strength in real-time with a sparkline visualization:

```bash
lantern wifi signal
```

**Example Output:**
```
Monitoring signal for MyNetwork... Press Ctrl+C to stop.

╭──────────────────────────── Wi-Fi Signal Monitor ────────────────────────────╮
│ Signal: ▅▆▇▆▅▆▇█▇▆  -51 dBm (Good)                                           │
│                                                                              │
│ SSID: MyNetwork  Channel: 36  Avg: -52 dBm  Range: -48/-56 dBm               │
╰──────────────────────────────────────────────────────────────────────────────╯
```

**Options:**
- `--interval, -i` - Sampling interval in seconds (default: 1.0)
- `--count, -c` - Number of samples before stopping (default: infinite)

#### Scan for Networks

Scan for available Wi-Fi networks in range:

```bash
lantern wifi scan --scan
```

> **Note:** The `--scan` flag is required for explicit permission. On macOS Sequoia and later, scanning may not be available as Apple removed the airport utility.

---

### Network Diagnostics

Run comprehensive network diagnostics in one command:

```bash
lantern diagnose
```

This shows:
- Active network interfaces
- Current Wi-Fi connection details
- Router/gateway information
- DNS configuration
- Internet connectivity status with latency

**Options:**
- `--json, -j` - Output in JSON format
- `--quick, -q` - Skip connectivity test for faster results

---

## JSON Output for Scripting

All commands support `--json` output for easy integration with scripts and other tools:

```bash
# Get interface data as JSON
lantern interfaces --json

# Parse with jq
lantern interfaces --json | jq '.[] | select(.is_default == true)'

# Use in shell scripts
if lantern diagnose --json | jq -e '.connectivity.success' > /dev/null; then
    echo "Internet is connected"
fi
```

**Example JSON Output:**
```json
{
  "connected": true,
  "ssid": "MyNetwork",
  "bssid": "58:96:71:f2:8f:6c",
  "channel": 36,
  "rssi": -52,
  "noise": -89,
  "signal_quality": 96,
  "tx_rate": 867.0,
  "security": "WPA2 Personal",
  "interface": "en0"
}
```

---

## Common Use Cases

### Check if you're connected to the internet
```bash
lantern diagnose --quick
```

### Troubleshoot DNS issues
```bash
# Check current DNS servers
lantern dns info

# Flush DNS cache if having resolution issues
lantern dns flush
```

### Find your local IP address
```bash
lantern interfaces --json | jq -r '.[] | select(.is_default) | .ipv4_address'
```

### Monitor Wi-Fi stability
```bash
# Monitor for 60 seconds
lantern wifi signal --count 60
```

### Get router MAC address (for Wake-on-LAN setup)
```bash
lantern router info --json | jq -r '.mac_address'
```

---

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/spudy-vibing/Lantern.git
cd Lantern

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=lantern --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_models.py -v
```

### Code Quality

```bash
# Run linter
ruff check src tests

# Auto-fix linting issues
ruff check src tests --fix

# Format code
ruff format src tests

# Type checking
mypy src/lantern
```

---

## Project Structure

```
Lantern/
├── src/lantern/
│   ├── __init__.py          # Package version
│   ├── cli.py               # Main CLI application
│   ├── constants.py         # App-wide constants
│   ├── exceptions.py        # Custom exceptions
│   ├── core/
│   │   ├── context.py       # Runtime context
│   │   ├── executor.py      # Async command execution
│   │   └── output.py        # Output formatting
│   ├── models/
│   │   └── network.py       # Data models
│   ├── platforms/
│   │   ├── base.py          # Platform adapter interface
│   │   ├── factory.py       # Platform detection
│   │   ├── macos.py         # macOS implementation
│   │   ├── linux.py         # Linux (stub)
│   │   └── windows.py       # Windows (stub)
│   └── tools/
│       ├── interfaces.py    # interfaces command
│       ├── router.py        # router commands
│       ├── dns.py           # dns commands
│       ├── diagnose.py      # diagnose command
│       └── wifi/            # Wi-Fi commands
├── tests/
│   ├── fixtures/            # Test data
│   ├── unit/                # Unit tests
│   └── integration/         # CLI integration tests
├── pyproject.toml
└── README.md
```

---

## Roadmap

### Phase 1: Foundation (v0.1.0) ✅
- [x] Project setup and CLI skeleton
- [x] Core infrastructure (async executor, output formatting)
- [x] Platform abstraction (macOS fully implemented)
- [x] Core commands (interfaces, router, dns, diagnose)
- [x] Wi-Fi commands (info, signal, scan)
- [x] Testing infrastructure (96 tests, 79% coverage)
- [x] Documentation

### Phase 2: Delight & Virality (v1.1)
- [ ] QR code generation for Wi-Fi sharing
- [ ] File transfer with QR codes
- [ ] Visual ping (sonar)
- [ ] Network device scanning

### Phase 3: LAN Mastery (v2.0)
- [ ] Device registry and nicknames
- [ ] SSH connection tools
- [ ] Wake-on-LAN
- [ ] Smart plug integration

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.
