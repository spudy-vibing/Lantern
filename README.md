# Lantern

A powerful network toolkit CLI for developers. Get instant insights into your network configuration, diagnose connectivity issues, share files, and manage network settings - all from the command line.

## Features

- **Network Diagnostics** - Comprehensive network summary with connectivity testing
- **Network Interfaces** - List all interfaces with IP addresses, MAC addresses, and status
- **Wi-Fi Tools** - View connection details, monitor signal strength, scan for networks
- **QR Code Generation** - Generate QR codes for URLs, text, and Wi-Fi sharing
- **File Transfer** - Share files and directories via HTTP with QR codes
- **Network Utilities** - Public IP lookup, port checking, visual ping
- **Device Discovery** - Scan your network for connected devices with vendor identification
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

# Find your public IP address
lantern whoami

# Share a file with anyone on your network
lantern drop myfile.zip

# Share your Wi-Fi password via QR code
lantern share

# Scan for devices on your network
lantern scan

# Visual ping with live sparkline
lantern sonar google.com
```

## Commands Reference

### QR Code Generation

#### Generate QR Code

Create a QR code from any text or URL:

```bash
lantern qr "https://example.com"
lantern qr "Hello World" --invert
```

**Options:**
- `--invert, -i` - Invert colors (white on black)
- `--border, -b` - Border size (default: 1)

---

#### Share Wi-Fi via QR

Generate a QR code to share your Wi-Fi network:

```bash
lantern share                          # Share current network
lantern share --show-password          # Show password in output
lantern share -s "NetworkName" -p "password"  # Explicit credentials
```

**Options:**
- `--ssid, -s` - Network name (defaults to current)
- `--password, -p` - Password (retrieved from Keychain if not provided)
- `--show-password` - Display password below QR code
- `--invert, -i` - Invert colors

---

### File Transfer

#### One-Shot File Share

Share a file via HTTP with a QR code for easy mobile access:

```bash
lantern drop myfile.zip
lantern drop photo.jpg --port 8080
lantern drop document.pdf --timeout 60
```

The server automatically stops after one download.

**Options:**
- `--port, -p` - Port to serve on (default: auto)
- `--timeout, -t` - Timeout in seconds (default: 300)
- `--no-qr` - Don't display QR code

---

#### Directory Server

Serve a directory for browsing from any device:

```bash
lantern serve                    # Serve current directory
lantern serve ~/Downloads        # Serve specific directory
lantern serve . --port 9000      # Custom port
```

**Options:**
- `--port, -p` - Port to serve on (default: auto)
- `--no-qr` - Don't display QR code

---

### Network Utilities

#### Public IP & Location

Show your public IP address and geolocation:

```bash
lantern whoami              # Full info with panel
lantern whoami --short      # Just the IP address
lantern whoami --json       # JSON output
```

**Example Output:**
```
╭───────────────────────────────── Public IP ──────────────────────────────────╮
│  74.105.81.242                                                               │
│                                                                              │
│  Location:  New York, New York, US                                           │
│  Provider:  AS701 Verizon Business                                           │
│  Timezone:  America/New_York                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

#### Port Checker

Check if a port is open:

```bash
lantern port 8080                # Check localhost:8080
lantern port 22 --host server    # Check server:22
lantern port 80 --external       # Check if port is internet-accessible
```

**Options:**
- `--host, -h` - Host to check (default: localhost)
- `--external, -e` - Check if accessible from internet
- `--json, -j` - JSON output

---

#### Visual Ping (Sonar)

Live ping visualization with sparkline display:

```bash
lantern sonar google.com           # Continuous ping
lantern sonar 8.8.8.8 -c 30        # 30 pings then stop
lantern sonar router -i 0.5        # Ping every 0.5 seconds
```

**Example Output:**
```
SONAR google.com

╭────────────────────────── google.com ───────────────────────────╮
│  ▂▃▂▃▂▃▂▃▂▃▂▃▂▃▂▃▂▃▂▃  12.3ms                                   │
│                                                                  │
│  min 10.2ms  avg 12.1ms  max 14.8ms                              │
╰──────────────────────────────────────────────────────────────────╯
```

**Options:**
- `--count, -c` - Number of pings (default: unlimited)
- `--interval, -i` - Interval between pings (default: 1.0s)

---

### Network Discovery

#### Scan Network

Discover devices on your local network:

```bash
lantern scan              # Show all devices
lantern scan --json       # JSON output for scripting
```

**Example Output:**
```
                        Network Devices (8 found)
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━┓
┃ IP Address    ┃ MAC Address       ┃ Vendor  ┃ Hostname      ┃   ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━┩
│ 192.168.1.1   │ 58:96:71:f2:8f:6c │ -       │ router.local  │ ⬤ │
│ 192.168.1.42  │ 3c:22:fb:12:34:56 │ Apple   │ macbook       │   │
│ 192.168.1.100 │ b8:27:eb:aa:bb:cc │ Rasp Pi │ raspberrypi   │   │
└───────────────┴───────────────────┴─────────┴───────────────┴───┘
⬤ = Gateway/Router
```

---

### Network Interfaces

List all network interfaces with their configuration:

```bash
lantern interfaces
lantern interfaces --json
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

---

### Router Information

Show default gateway/router information:

```bash
lantern router info
lantern router info --json
```

---

### DNS Commands

#### View DNS Configuration

```bash
lantern dns info
```

#### Flush DNS Cache

```bash
lantern dns flush
```

---

### Wi-Fi Commands

#### View Current Connection

```bash
lantern wifi info
```

#### Monitor Signal Strength

```bash
lantern wifi signal
lantern wifi signal --count 60    # Monitor for 60 samples
```

#### Scan for Networks

```bash
lantern wifi scan --scan
```

---

### Network Diagnostics

Run comprehensive network diagnostics:

```bash
lantern diagnose
lantern diagnose --quick    # Skip connectivity test
lantern diagnose --json     # JSON output
```

---

## JSON Output for Scripting

All commands support `--json` output for easy integration:

```bash
# Get public IP as JSON
lantern whoami --json | jq '.ip'

# Get all devices as JSON
lantern scan --json | jq '.[] | select(.vendor == "Apple")'

# Check if connected to internet
if lantern diagnose --json | jq -e '.connectivity.success' > /dev/null; then
    echo "Internet is connected"
fi
```

---

## Common Use Cases

### Share a file with someone on your network
```bash
lantern drop presentation.pdf
# Scan the QR code from your phone to download
```

### Share Wi-Fi with a guest
```bash
lantern share --show-password
# Guest scans QR code to connect automatically
```

### Monitor connection stability
```bash
lantern sonar 8.8.8.8 -c 100
```

### Find all devices on your network
```bash
lantern scan
```

### Check if your server port is accessible
```bash
lantern port 443 --external
```

### Get your public IP for remote access setup
```bash
lantern whoami --short
```

---

## Development

### Setup Development Environment

```bash
git clone https://github.com/spudy-vibing/Lantern.git
cd Lantern
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest                                    # Run all tests
pytest --cov=lantern --cov-report=html   # With coverage
pytest tests/unit/test_qr.py -v          # Specific test
```

### Code Quality

```bash
ruff check src tests        # Linting
ruff format src tests       # Formatting
mypy src/lantern            # Type checking
```

---

## Project Structure

```
Lantern/
├── src/lantern/
│   ├── cli.py               # Main CLI application
│   ├── core/                # Runtime context, executor, output
│   ├── models/              # Data models
│   ├── platforms/           # Platform adapters (macOS, Linux, Windows)
│   ├── services/            # Reusable services
│   │   ├── qr.py            # QR code generation
│   │   ├── http_server.py   # File server
│   │   └── oui.py           # MAC vendor lookup
│   └── tools/               # CLI commands
│       ├── qr.py, share.py       # QR commands
│       ├── drop.py, serve.py     # File transfer
│       ├── whoami.py, port.py    # Network utilities
│       ├── sonar.py, scan.py     # Monitoring & discovery
│       ├── interfaces.py         # Network interfaces
│       ├── router.py, dns.py     # Router & DNS
│       ├── diagnose.py           # Diagnostics
│       └── wifi/                 # Wi-Fi commands
├── tests/
├── pyproject.toml
└── README.md
```

---

## Roadmap

### Phase 1: Foundation (v0.1.0) ✅
- [x] Core infrastructure and CLI skeleton
- [x] Platform abstraction (macOS)
- [x] Core commands (interfaces, router, dns, diagnose)
- [x] Wi-Fi commands (info, signal, scan)
- [x] Testing infrastructure

### Phase 2: Delight & Virality (v0.2.0) ✅
- [x] QR code generation (`qr`, `share`)
- [x] File transfer (`drop`, `serve`)
- [x] Network utilities (`whoami`, `port`)
- [x] Visual ping (`sonar`)
- [x] Network scanning (`scan`)

### Phase 3: LAN Mastery (v0.3.0)
- [ ] Configuration system
- [ ] Device registry and nicknames
- [ ] SSH connection tools
- [ ] Wake-on-LAN
- [ ] Smart plug integration

### Phase 4: Observability (v0.4.0)
- [ ] Network event watcher
- [ ] Bandwidth monitoring
- [ ] TUI dashboard

### Phase 5: Pro Tools (v0.5.0)
- [ ] Advanced diagnostics (traceroute, SSL checker)
- [ ] Developer tools (request bin, hosts manager)
- [ ] Plugin SDK

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
