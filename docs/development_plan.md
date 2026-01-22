# Development Plan - Lantern

## Overview

Lantern is a developer-focused CLI tool for local network diagnostics, device management, and connectivity. The tool is designed to be extensible, safe by default, and provide developer-friendly visibility into network status.

**Target Persona**: The "Home Lab Developer" - a developer/power user with a MacBook, Raspberry Pis, NAS, who works from home or coffee shops.

---

## Phase 1: Foundation (V1.0)

**Goal**: Functional CLI on macOS/Linux with read-only diagnostics.

### Milestone 1.1: Project Skeleton
- [ ] Project setup (Poetry, git, initial structure)
- [ ] Add `rich` as core dependency for output formatting
- [ ] `CommandRunner` implementation with robust error handling
- [ ] `PlatformAdapter` ABC definition
- [ ] Basic CLI skeleton (`lantern --version`, `lantern --help`)

### Milestone 1.2: Platform Adapters (macOS Focus)
- [ ] Implement `MacOSAdapter` using `networksetup`, `scutil`, `ipconfig`
- [ ] Implement `LinuxAdapter` detecting `nmcli` or `ip/iw`
- [ ] Windows stub with clear "coming soon" message
- [ ] Unit tests for parsing logic using captured output fixtures

### Milestone 1.3: Core Commands
- [ ] `lantern interfaces` - List active interfaces
- [ ] `lantern router info` - Gateway detection
- [ ] `lantern dns info` - Resolver config
- [ ] `lantern diagnose` - Aggregated network summary

### Milestone 1.4: Wi-Fi Capabilities
- [ ] `lantern wifi info` - Current connection details
- [ ] `lantern wifi signal` - Live sampling loop with sparklines
- [ ] `lantern wifi scan` - With **strict** `--scan` flag requirement

### Milestone 1.5: Polish & Ship
- [ ] JSON output verification for all commands
- [ ] `--verbose` and `--quiet` flags
- [ ] Documentation (README, SECURITY)
- [ ] Final manual verification on macOS

---

## Phase 2: Delight & Virality (V1.1)

**Goal**: Ship the "wow" features that make people share Lantern.

### Milestone 2.1: Quick Wins
- [ ] `lantern share` - Wi-Fi QR code in terminal
- [ ] `lantern qr` - General QR code generator
- [ ] `lantern whoami` - Public IP + geo lookup (opt-in external API)
- [ ] `lantern port` - Port checker (what process is using port X?)

### Milestone 2.2: Visual & Fun
- [ ] `lantern sonar` - Visual ping with sparklines/bars
- [ ] `lantern ping` improvements - Color-coded latency, statistics

### Milestone 2.3: File Transfer
- [ ] `lantern drop` - One-shot file transfer with QR code
- [ ] `lantern serve` - Quick HTTP server for a directory

### Milestone 2.4: Network Discovery
- [ ] `lantern scan` - Fast ARP + mDNS network scan
- [ ] OUI database integration for vendor lookup

---

## Phase 3: LAN Mastery & Connections (V2.0)

**Goal**: Make Lantern the go-to tool for managing local network devices.

### Milestone 3.1: Configuration System
- [ ] Config file support (`~/.config/lantern/config.toml`)
- [ ] Device registry (`~/.config/lantern/devices.toml`)
- [ ] Settings: default interface, color preferences, default targets

### Milestone 3.2: Device Registry
- [ ] `lantern devices` - List saved devices with online/offline status
- [ ] `lantern devices add/remove` - Manage device registry
- [ ] `lantern devices ping` - Health check all devices
- [ ] `lantern devices export/import` - Backup/restore

### Milestone 3.3: SSH Tools
- [ ] `lantern ssh list` - Discover SSH-enabled devices
- [ ] `lantern ssh add` - Save SSH connection
- [ ] `lantern ssh <name>` - Quick connect to saved device
- [ ] `lantern ssh setup` - ssh-copy-id wrapper
- [ ] `lantern tunnel` - Friendly SSH tunnel syntax

### Milestone 3.4: Web & Service Tools
- [ ] `lantern web list/add/open` - Manage device web interfaces
- [ ] `lantern services` - mDNS/Bonjour browser

### Milestone 3.5: Power Management
- [ ] `lantern wake` - Wake-on-LAN (by MAC or saved device name)
- [ ] `lantern wake --wait` - Wait for device to come online
- [ ] `lantern wake --then ssh` - Wake then connect
- [ ] `lantern shutdown` - Remote shutdown via SSH
- [ ] `lantern power status` - Show power state of all devices
- [ ] `lantern power on/off` - Unified power control
- [ ] `lantern power on-group/off-group` - Group power control

### Milestone 3.6: Smart Plug Integration
- [ ] `lantern plugs discover` - Find smart plugs on network
- [ ] `lantern plug <name> on/off/toggle` - Control plugs
- [ ] Kasa (TP-Link) support via `python-kasa`
- [ ] Shelly support via HTTP API
- [ ] Tasmota support via HTTP API

### Milestone 3.7: File Shares
- [ ] `lantern shares list` - Discover SMB/AFP/NFS shares
- [ ] `lantern shares add/mount` - Save and mount shares

---

## Phase 4: Observability & Monitoring (V2.1)

**Goal**: Long-running monitoring and rich TUI experiences.

### Milestone 4.1: Network Monitoring
- [ ] `lantern watch` - Network change watcher (IP, SSID, interface changes)
- [ ] `lantern bw` - Live bandwidth monitor per interface
- [ ] `lantern uptime <device>` - Device availability monitoring
- [ ] `lantern arp --live` - Real-time ARP table with alerts

### Milestone 4.2: TUI Mode
- [ ] Add `textual` as optional dependency
- [ ] `lantern wifi heatmap` - Fullscreen signal strength TUI
- [ ] `lantern dashboard` - Combined network status TUI

### Milestone 4.3: Connection Visibility
- [ ] `lantern connections` - Active TCP/UDP by process
- [ ] `lantern tunnels` - List active SSH tunnels

### Milestone 4.4: Power Scheduling & IPMI
- [ ] `lantern power schedule` - Schedule power on/off times
- [ ] `lantern power schedules` - List all schedules
- [ ] `lantern daemon` - Background service for scheduling
- [ ] `lantern ipmi` - IPMI/BMC support for servers

---

## Phase 5: Pro Tools & Extensibility (V3.0)

**Goal**: Advanced diagnostics and community extensibility.

### Milestone 5.1: Network Diagnostics
- [ ] `lantern trace` - Pretty traceroute with geo hints
- [ ] `lantern ssl` - Certificate checker
- [ ] `lantern probe` - HTTP healthcheck tool
- [ ] `lantern resolve` - DNS lookup with timing
- [ ] `lantern mtu` - Path MTU discovery

### Milestone 5.2: Developer Tools
- [ ] `lantern catch` - HTTP request bin for webhook debugging
- [ ] `lantern mock` - Mock API server from JSON
- [ ] `lantern dns flush` - Cross-platform DNS cache flush
- [ ] `lantern hosts` - Hosts file manager

### Milestone 5.3: Remote Access
- [ ] `lantern vnc list/connect` - VNC discovery and connection
- [ ] `lantern screen` - macOS screen sharing wrapper
- [ ] `lantern clip send/receive` - LAN clipboard sharing

### Milestone 5.4: Extensibility
- [ ] Plugin SDK design and documentation
- [ ] `lantern init` - Scaffold new plugin
- [ ] Plugin discovery and loading system

---

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| CLI Framework | Typer | Modern, type hints, excellent DX |
| Packaging | Poetry | Robust dependency management |
| Output Formatting | Rich | Tables, colors, progress, sparklines |
| TUI Framework | Textual (Phase 4) | Built on Rich, good for dashboards |
| Config Format | TOML | Human-readable, well-supported |
| Python Version | 3.9+ | Modern typing features |

---

## Platform Priority

1. **macOS** - Primary development and testing
2. **Linux** - Best-effort with `nmcli`, `ip`, `iw`
3. **Windows** - Stubbed with clear messaging (future consideration)

---

## Dependencies (Core)

```toml
[tool.poetry.dependencies]
python = "^3.9"
typer = "^0.9.0"
rich = "^13.0.0"
qrcode = "^7.4.0"

[tool.poetry.group.power.dependencies]
python-kasa = "^0.5.0"       # TP-Link Kasa smart plugs
aiohttp = "^3.9.0"           # HTTP API for Shelly/Tasmota

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
ruff = "^0.1.0"
mypy = "^1.0.0"
```

---

## Success Metrics

- **Phase 1**: Tool installs and runs basic diagnostics on macOS
- **Phase 2**: At least one "viral" feature (`share` or `drop`) working smoothly
- **Phase 3**: Can manage 5+ devices by name, SSH without remembering IPs, wake/shutdown devices
- **Phase 4**: Useful monitoring for home lab scenarios, scheduled power management
- **Phase 5**: Community contributes first plugin
