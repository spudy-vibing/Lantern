# Lantern - Feature Ideas & Boundaries

This document serves as a brainstorming "bank" for future features and a strict boundary definition for what Lantern will **not** become.

---

## Target Persona: The "Home Lab Developer"

A developer/power user with a MacBook, a few Raspberry Pis, maybe a NAS, who works from home or coffee shops. Technical enough to use CLI tools but doesn't want to memorize `networksetup` flags or parse `ifconfig` output.

---

## Phase 2: Delight & Virality (Ship These Early)

These are the "wow" features that get people to share Lantern.

### `lantern share` (Wi-Fi QR Code)
- **Concept**: Generates a standard Wi-Fi QR code in the terminal.
- **Use Case**: "Hey, what's the Wi-Fi password?" -> Run `lantern share`, friend scans screen.
- **Tech**: Uses `qrcodegen` library + local SSID/Password retrieval.

### `lantern drop` (Local File Transfer)
- **Concept**: Temporary, zero-config HTTP server to share a file with devices on the LAN.
- **Use Case**: "I need to get this PDF to my phone." -> `lantern drop report.pdf`.
- **UX**: Prints a QR code + URL. Server shuts down after one successful download.

### `lantern sonar` (Visual Latency)
- **Concept**: Radar-like or sparkline TUI that pings a target.
- **Use Case**: Diagnosing intermittent lag while gaming or coding.
- **Visual**: Live graph `▂ ▃ ▅ ▇ █` in the terminal.

### `lantern whoami` (Public IP & Geo)
- **Concept**: Fetches public IP and details.
- **Use Case**: Verifying VPN status or checking ISP visibility.
- **Output**: Public IP, Location, ISP (via external API, opt-in).

### `lantern qr` (General QR Generator)
- **Concept**: Generate QR code for any text in terminal.
- **Use Case**: Quick sharing of URLs, text, contact info.
- **Command**: `lantern qr "https://example.com"` or pipe input.

### `lantern port` (Port Checker)
- **Concept**: Check if a port is in use and by what process.
- **Use Case**: "Why can't I start my server on port 3000?"
- **Command**: `lantern port 3000` -> Shows PID, process name.

### `lantern scan` (Quick Network Scan)
- **Concept**: Fast ARP + mDNS scan showing devices on network.
- **Use Case**: "What's connected to my network right now?"
- **Output**: IP, hostname, vendor (OUI), common open ports.

---

## Phase 3: LAN Mastery & Device Connections

### Device Registry System

#### `lantern devices` (Device Management)
- **Concept**: Named device registry for quick access.
- **Commands**:
  - `lantern devices` - List all saved devices with online/offline status
  - `lantern devices add pi --ip 192.168.1.50 --mac aa:bb:cc:...`
  - `lantern devices remove old-pi`
  - `lantern devices ping` - Health check all saved devices
  - `lantern devices export/import` - Backup/restore device list

### SSH Tools

#### `lantern ssh` (SSH Connection Manager)
- **Concept**: Discover and manage SSH connections to local devices.
- **Commands**:
  - `lantern ssh list` - Find devices with port 22 open
  - `lantern ssh add pi-media pi@192.168.1.50` - Save for quick access
  - `lantern ssh pi-media` - Connect using saved name
  - `lantern ssh setup pi-media` - Interactive key setup (ssh-copy-id wrapper)

#### `lantern tunnel` (SSH Tunnels)
- **Concept**: Friendly SSH tunnel syntax.
- **Command**: `lantern tunnel pi-media 8080:localhost:80`
- **Use Case**: Forward a port from a remote device with readable syntax.

### Web Interface Tools

#### `lantern web` (Web UI Manager)
- **Concept**: Discover and manage device web interfaces.
- **Commands**:
  - `lantern web list` - Find devices with HTTP/HTTPS ports
  - `lantern web add router https://192.168.1.1` - Save a web UI
  - `lantern web open router` - Open in browser
  - `lantern web check` - Ping all saved web UIs, show status

### File Share Tools

#### `lantern shares` (Network Shares)
- **Concept**: Discover and mount SMB/AFP/NFS shares.
- **Commands**:
  - `lantern shares list` - Discover shares on network
  - `lantern shares add media smb://192.168.1.100/media`
  - `lantern shares mount media ~/mnt/media`
  - `lantern shares browse nas` - List shares on a specific device

### Power Management

#### `lantern power` (Device Power Control)
- **Concept**: Turn devices on and off remotely using multiple methods.
- **Commands**:
  - `lantern power status` - Show power state of all devices
  - `lantern power on <device>` - Turn on (auto-detect method)
  - `lantern power off <device>` - Turn off (graceful shutdown)
  - `lantern power off <device> --force` - Hard power off (smart plug)
  - `lantern power restart <device>` - Restart device
  - `lantern power on-group <group>` - Power on device group
  - `lantern power off-group <group>` - Power off device group

#### `lantern wake` (Wake-on-LAN)
- **Concept**: Send Magic Packet to wake a device.
- **Commands**:
  - `lantern wake <device>` - Send magic packet
  - `lantern wake <device> --wait` - Wait until device comes online
  - `lantern wake <device> --then ssh` - Wake then connect via SSH
  - `lantern wake <device> --at 06:00` - Scheduled wake
- **Use Case**: Turn on your media server from the couch.

#### `lantern shutdown` (Remote Shutdown)
- **Concept**: Gracefully shut down remote devices via SSH.
- **Commands**:
  - `lantern shutdown <device>` - SSH shutdown command
  - `lantern shutdown <device> --reboot` - Reboot instead
- **Use Case**: Shut down your Pi before pulling the plug.

#### `lantern plug` (Smart Plug Control)
- **Concept**: Control smart plugs on your network.
- **Commands**:
  - `lantern plugs discover` - Find smart plugs on network
  - `lantern plugs list` - List known plugs
  - `lantern plug <name> on|off|toggle` - Control plug
  - `lantern plug <name> status` - State + power usage (if supported)
- **Supported**: TP-Link Kasa, Shelly, Tasmota, Tuya (local API)
- **Use Case**: Control desk lamp, kill power to frozen device.

#### `lantern ipmi` (Server Power Control)
- **Concept**: IPMI/BMC control for servers with baseboard management.
- **Commands**:
  - `lantern ipmi <device> power-on|power-off|reset|status`
  - `lantern ipmi <device> console` - Serial-over-LAN console
- **Use Case**: Manage headless servers, recover from freezes.

#### Power Scheduling (Requires Daemon)
- **Concept**: Schedule power on/off for devices.
- **Commands**:
  - `lantern power schedule <device> --on "08:00" --off "23:00"`
  - `lantern power schedule <device> --on "weekdays 08:00"`
  - `lantern power schedules` - List all schedules
  - `lantern power unschedule <device>` - Remove schedule
- **Use Case**: Auto-start NAS in morning, shut down at night.

#### Power Methods by Device Type
| Device Type | Turn ON | Turn OFF |
|-------------|---------|----------|
| PC/Server (WoL) | Wake-on-LAN magic packet | SSH shutdown command |
| Server (IPMI) | IPMI power-on | IPMI power-off |
| Raspberry Pi | WoL (if supported) or smart plug | SSH poweroff |
| Smart Plug | API call | API call |
| Any device | Smart plug as backup | Smart plug (force) |

### Service Discovery

#### `lantern services` (mDNS Browser)
- **Concept**: Scan for advertised services (Bonjour/Avahi).
- **Use Case**: Find printers, file shares, IoT devices, Raspberry Pis.
- **Output**: Service name, type, host, port.

---

## Phase 4: Observability & Monitoring

### `lantern watch` (Network Change Watcher)
- **Concept**: Long-running process that alerts on network changes.
- **Use Case**: Detect Wi-Fi to Ethernet switch, public IP changes.
- **Output**: Log stream with timestamps.

### `lantern bw` (Bandwidth Monitor)
- **Concept**: Live bytes/sec per interface.
- **Use Case**: "What's eating my bandwidth?"
- **Visual**: Streaming output with upload/download rates.

### `lantern wifi heatmap` (Signal TUI)
- **Concept**: Fullscreen signal strength meter.
- **Use Case**: Finding the best seat in a coffee shop.
- **Tech**: Uses `textual` or `rich` for TUI.

### `lantern uptime` (Device Monitor)
- **Concept**: Monitor a device's availability over time.
- **Command**: `lantern uptime pi-media --interval 30`
- **Output**: Uptime percentage, downtime events.

### `lantern connections` (Active Connections)
- **Concept**: Show active TCP/UDP connections grouped by process.
- **Use Case**: "What's making network requests?"
- **Output**: Process name, local/remote address, state.

### `lantern arp --live` (ARP Watch)
- **Concept**: Live ARP table with new device alerts.
- **Use Case**: See when new devices join your network.

---

## Phase 5: Pro Tools & Extensibility

### Network Diagnostics

#### `lantern trace` (Traceroute++)
- **Concept**: Prettier traceroute with latency bars and geo hints.
- **Use Case**: Debug routing issues with visual clarity.

#### `lantern ssl` (Certificate Checker)
- **Concept**: Check SSL certificate details.
- **Output**: Expiry date, issuer, chain validity.
- **Use Case**: "Is my cert about to expire?"

#### `lantern probe` (HTTP Healthcheck)
- **Concept**: HTTP status, response time, headers summary.
- **Command**: `lantern probe https://api.example.com`
- **Use Case**: Quick API endpoint health check.

#### `lantern catch` (Request Bin)
- **Concept**: Catch and display incoming HTTP requests.
- **Command**: `lantern catch --port 9999`
- **Use Case**: Webhook debugging.

### Utilities

#### `lantern subnet` (Subnet Calculator)
- **Concept**: Calculate subnet details offline.
- **Command**: `lantern subnet 192.168.1.0/24`
- **Output**: Range, broadcast, usable hosts, wildcard mask.

#### `lantern resolve` (DNS Lookup)
- **Concept**: DNS lookup with timing and resolver info.
- **Command**: `lantern resolve example.com`
- **Output**: IPs, TTL, which resolver answered, query time.

#### `lantern dns flush` (Flush DNS Cache)
- **Concept**: Cross-platform DNS cache flush.
- **Use Case**: Everyone googles "how to flush DNS" constantly.

#### `lantern hosts` (Hosts File Manager)
- **Concept**: Pretty-print and edit `/etc/hosts`.
- **Commands**:
  - `lantern hosts` - Show current entries
  - `lantern hosts add dev.local 127.0.0.1`
  - `lantern hosts remove dev.local`

### Remote Access

#### `lantern vnc` (VNC Connection Manager)
- **Concept**: Discover and connect to VNC servers.
- **Commands**:
  - `lantern vnc list` - Find devices with VNC (port 5900+)
  - `lantern vnc connect pi-desktop` - Launch viewer

#### `lantern screen` (macOS Screen Sharing)
- **Concept**: Quick macOS screen sharing.
- **Command**: `lantern screen mac-mini` (wraps `open vnc://`)

### Sharing & Transfer

#### `lantern clip` (Clipboard Sharing)
- **Concept**: Share clipboard text across LAN devices.
- **Commands**: `lantern clip send` / `lantern clip receive`
- **Use Case**: Copy on laptop, paste on desktop.

#### `lantern serve` (HTTP Server)
- **Concept**: Instant HTTP server for a folder.
- **Command**: `lantern serve ./public --port 8080`
- **Use Case**: Better `python -m http.server`.

### Extensibility

#### `lantern init` (Plugin SDK)
- **Concept**: Scaffold a new lantern plugin.
- **Use Case**: Community extensions.

#### `lantern vendor` (OUI Database)
- **Concept**: Offline MAC vendor resolution.
- **Command**: `lantern vendor update` - Download IEEE OUI database.

---

## Additional Ideas Bank

### Developer Productivity
| Tool | Description |
|------|-------------|
| `lantern proxy` | Show HTTP_PROXY settings, detect system proxy |
| `lantern tunnels` | List active SSH tunnels, ngrok sessions |
| `lantern mock` | Start a mock API server from a JSON file |
| `lantern ping-multi` | Parallel ping multiple targets, compare latency |

### Network Debugging
| Tool | Description |
|------|-------------|
| `lantern mtu` | Discover path MTU to a target |
| `lantern route` | Show routing table in readable format |
| `lantern gateway ping` | Auto-resolve and ping default gateway |
| `lantern interfaces --watch` | Live interface status changes |

### IoT & Smart Home
| Tool | Description |
|------|-------------|
| `lantern cast` | Discover and control Chromecast/AirPlay devices |
| `lantern advertise` | Make your machine discoverable via mDNS |
| `lantern mqtt` | Simple MQTT publish/subscribe for IoT debugging |

### Fun & Novelty
| Tool | Description |
|------|-------------|
| `lantern ping-msg` | Embed ASCII message in ICMP payload (packet sniffers only) |
| `lantern score` | Composite "network health" score (latency, loss, DNS speed) |
| `lantern speed` | Bandwidth test (wraps speedtest-cli if installed) |

---

## Configuration System

### Config File Location
```
~/.config/lantern/
├── config.toml          # General settings
├── devices.toml         # Device registry
└── history.log          # Connection history (optional)
```

### Example config.toml
```toml
[general]
default_interface = "en0"
color = true
json_output = false

[ping]
default_count = 5
default_target = "8.8.8.8"

[scan]
timeout = 2
ports = [22, 80, 443, 5000, 8080]
```

