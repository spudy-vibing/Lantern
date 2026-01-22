# Device Registry - Architecture Specification

## Overview

The device registry is a core feature that allows users to save, name, and manage devices on their local network. It enables commands like `lantern ssh pi` instead of `lantern ssh pi@192.168.1.50`.

---

## Storage Location

```
~/.config/lantern/
├── config.toml          # General settings
├── devices.toml         # Device registry (this spec)
├── shares.toml          # Saved network shares
└── web.toml             # Saved web interfaces
```

**Why separate files?**
- Easier to backup/sync specific data
- Cleaner separation of concerns
- Can export just devices without settings

---

## Device Schema

### devices.toml

```toml
# Device Registry for Lantern
# Auto-generated and user-editable

[devices.pi-media]
ip = "192.168.1.50"
mac = "dc:a6:32:xx:xx:xx"
hostname = "raspberrypi.local"
user = "pi"                      # Default SSH user
tags = ["ssh", "web"]            # Capabilities
notes = "Media server in closet"
added = "2024-01-15T10:30:00Z"
last_seen = "2024-01-20T14:22:00Z"

[devices.nas]
ip = "192.168.1.100"
mac = "00:11:32:xx:xx:xx"
hostname = "synology.local"
user = "admin"
tags = ["ssh", "smb", "web"]
web_url = "https://192.168.1.100:5001"
notes = "Synology DS920+"
added = "2024-01-10T08:00:00Z"
last_seen = "2024-01-20T14:22:00Z"

[devices.router]
ip = "192.168.1.1"
mac = "aa:bb:cc:dd:ee:ff"
hostname = "router.asus.com"
tags = ["web"]
web_url = "http://192.168.1.1"
notes = "ASUS RT-AX88U"
added = "2024-01-01T00:00:00Z"

[devices.printer]
ip = "192.168.1.200"
mac = "00:00:00:xx:xx:xx"
hostname = "EPSON123456.local"
tags = ["printer"]
notes = "Office printer"
added = "2024-01-05T12:00:00Z"
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ip` | string | Yes | IPv4 address |
| `mac` | string | No | MAC address (for WoL) |
| `hostname` | string | No | mDNS or DNS hostname |
| `user` | string | No | Default SSH username |
| `tags` | array | No | Capability tags |
| `web_url` | string | No | Web interface URL |
| `notes` | string | No | User notes |
| `added` | datetime | Auto | When device was added |
| `last_seen` | datetime | Auto | Last successful ping |

### Supported Tags

```python
DEVICE_TAGS = [
    "ssh",        # Port 22 open
    "web",        # HTTP/HTTPS interface
    "smb",        # SMB file share
    "afp",        # AFP file share (Apple)
    "nfs",        # NFS share
    "vnc",        # VNC remote desktop
    "printer",    # Network printer
    "iot",        # IoT device
    "wol",        # Wake-on-LAN capable
    "smart-plug", # Smart plug device
    "ipmi",       # IPMI/BMC capable server
]
```

---

## Power Management Configuration

Devices can have power management settings for remote on/off control.

### Power Config Schema

```toml
[devices.nas]
ip = "192.168.1.100"
mac = "00:11:32:xx:xx:xx"
user = "admin"
tags = ["ssh", "smb", "web", "wol"]

# Power management settings
[devices.nas.power]
wake_method = "wol"                      # wol, ipmi, plug
shutdown_method = "ssh"                  # ssh, ipmi, plug
shutdown_command = "sudo shutdown -h now"
plug_device = "nas-plug"                 # Optional: backup smart plug

[devices.server]
ip = "192.168.1.10"
mac = "aa:bb:cc:dd:ee:ff"
tags = ["ssh", "ipmi"]

[devices.server.power]
wake_method = "ipmi"
shutdown_method = "ipmi"
ipmi_host = "192.168.1.11"               # BMC/IPMI IP address
ipmi_user = "admin"                      # IPMI username

[devices.pi-media]
ip = "192.168.1.50"
mac = "dc:a6:32:xx:xx:xx"
user = "pi"
tags = ["ssh", "web"]

[devices.pi-media.power]
wake_method = "plug"                     # Pi doesn't support WoL
shutdown_method = "ssh"
shutdown_command = "sudo poweroff"
plug_device = "pi-plug"                  # Smart plug controls power

[devices.desk-lamp]
ip = "192.168.1.201"
type = "smart-plug"
vendor = "kasa"                          # kasa, shelly, tasmota, tuya
tags = ["smart-plug", "iot"]

# Smart plugs don't need [power] section - they ARE power devices
```

### Power Methods

| Method | Turn ON | Turn OFF | Requirements |
|--------|---------|----------|--------------|
| `wol` | Magic packet | N/A (use ssh) | MAC address |
| `ssh` | N/A | SSH command | SSH access, user |
| `ipmi` | IPMI power-on | IPMI power-off | IPMI host, credentials |
| `plug` | Smart plug API | Smart plug API | Plug device reference |

### Smart Plug Vendors

```toml
# TP-Link Kasa
[devices.kasa-plug]
ip = "192.168.1.201"
type = "smart-plug"
vendor = "kasa"

# Shelly
[devices.shelly-plug]
ip = "192.168.1.202"
type = "smart-plug"
vendor = "shelly"

# Tasmota (flashed devices)
[devices.tasmota-plug]
ip = "192.168.1.203"
type = "smart-plug"
vendor = "tasmota"

# Tuya/Smart Life
[devices.tuya-plug]
ip = "192.168.1.204"
type = "smart-plug"
vendor = "tuya"
device_id = "abc123"                     # Required for Tuya
local_key = "xyz789"                     # Required for Tuya
```

### Power Schedule Schema

```toml
# Stored in ~/.config/lantern/schedules.toml

[schedules.nas]
device = "nas"
on_time = "08:00"
on_days = ["mon", "tue", "wed", "thu", "fri"]
off_time = "23:00"
off_days = ["mon", "tue", "wed", "thu", "fri"]
enabled = true

[schedules.desk-lamp]
device = "desk-lamp"
on_time = "sunset"                       # Special: uses local sunset time
off_time = "23:30"
on_days = ["*"]                          # Every day
off_days = ["*"]
enabled = true
```

---

## CLI Commands

### List Devices

```bash
$ lantern devices
┌──────────┬───────────────┬───────────────────┬──────────┬────────────┐
│ Name     │ IP            │ MAC               │ Tags     │ Status     │
├──────────┼───────────────┼───────────────────┼──────────┼────────────┤
│ pi-media │ 192.168.1.50  │ dc:a6:32:xx:xx:xx │ ssh, web │ ● Online   │
│ nas      │ 192.168.1.100 │ 00:11:32:xx:xx:xx │ ssh, smb │ ● Online   │
│ router   │ 192.168.1.1   │ aa:bb:cc:dd:ee:ff │ web      │ ● Online   │
│ printer  │ 192.168.1.200 │ 00:00:00:xx:xx:xx │ printer  │ ○ Offline  │
└──────────┴───────────────┴───────────────────┴──────────┴────────────┘
```

### Add Device

```bash
# Minimal
$ lantern devices add pi-media --ip 192.168.1.50
✓ Added "pi-media" (192.168.1.50)

# Full
$ lantern devices add nas \
    --ip 192.168.1.100 \
    --mac 00:11:32:xx:xx:xx \
    --user admin \
    --tags ssh,smb,web \
    --notes "Synology NAS"
✓ Added "nas" (192.168.1.100)

# From scan (interactive)
$ lantern devices add --from-scan
? Select a device to add:
  ❯ 192.168.1.50  (dc:a6:32:xx:xx:xx) Raspberry Pi
    192.168.1.100 (00:11:32:xx:xx:xx) Synology
    192.168.1.200 (00:00:00:xx:xx:xx) EPSON
? Name for this device: pi-media
✓ Added "pi-media" (192.168.1.50)
```

### Remove Device

```bash
$ lantern devices remove pi-media
? Remove "pi-media" (192.168.1.50)? [y/N] y
✓ Removed "pi-media"
```

### Update Device

```bash
$ lantern devices update nas --ip 192.168.1.101
✓ Updated "nas" IP: 192.168.1.100 → 192.168.1.101

$ lantern devices update nas --add-tag vnc
✓ Updated "nas" tags: ssh, smb, web, vnc
```

### Ping All Devices

```bash
$ lantern devices ping
┌──────────┬───────────────┬──────────┬──────────┐
│ Name     │ IP            │ Status   │ Latency  │
├──────────┼───────────────┼──────────┼──────────┤
│ pi-media │ 192.168.1.50  │ ● Online │ 2.3ms    │
│ nas      │ 192.168.1.100 │ ● Online │ 1.1ms    │
│ router   │ 192.168.1.1   │ ● Online │ 0.8ms    │
│ printer  │ 192.168.1.200 │ ○ Offline│ -        │
└──────────┴───────────────┴──────────┴──────────┘
```

### Show Device Details

```bash
$ lantern devices show nas
┌─────────────────────────────────────────────────┐
│ nas                                             │
├─────────────────────────────────────────────────┤
│ IP:        192.168.1.100                        │
│ MAC:       00:11:32:xx:xx:xx                    │
│ Hostname:  synology.local                       │
│ User:      admin                                │
│ Tags:      ssh, smb, web                        │
│ Web:       https://192.168.1.100:5001           │
│ Notes:     Synology DS920+                      │
│ Added:     2024-01-10                           │
│ Last Seen: 2 hours ago                          │
│ Status:    ● Online (1.1ms)                     │
└─────────────────────────────────────────────────┘
```

### Export/Import

```bash
# Export
$ lantern devices export > my-devices.toml
✓ Exported 4 devices

# Import
$ lantern devices import my-devices.toml
? Import 4 devices? [y/N] y
✓ Imported: pi-media, nas, router, printer

# Import with merge strategy
$ lantern devices import my-devices.toml --merge
✓ Added 2 new devices, updated 2 existing
```

---

## Integration with Other Commands

### SSH Integration

```bash
# Uses device registry
$ lantern ssh pi-media
# Translates to: ssh pi@192.168.1.50

# With custom user
$ lantern ssh pi-media --user root
# Translates to: ssh root@192.168.1.50
```

### Wake-on-LAN Integration

```bash
# Uses MAC from registry
$ lantern wake nas
Sending magic packet to 00:11:32:xx:xx:xx...
✓ Packet sent

# Wait for device
$ lantern wake nas --wait
Sending magic packet to 00:11:32:xx:xx:xx...
Waiting for device... ● Online (took 12s)
```

### Web Integration

```bash
# Uses web_url from registry
$ lantern web open nas
Opening https://192.168.1.100:5001...
```

### Scan Integration

```bash
# Show which devices are known
$ lantern scan
┌───────────────┬───────────────────┬──────────┬────────────┬──────────┐
│ IP            │ MAC               │ Vendor   │ Ports      │ Known As │
├───────────────┼───────────────────┼──────────┼────────────┼──────────┤
│ 192.168.1.1   │ aa:bb:cc:dd:ee:ff │ ASUS     │ 80, 443    │ router   │
│ 192.168.1.50  │ dc:a6:32:xx:xx:xx │ Raspberry│ 22, 80     │ pi-media │
│ 192.168.1.100 │ 00:11:32:xx:xx:xx │ Synology │ 22, 5000   │ nas      │
│ 192.168.1.150 │ 11:22:33:xx:xx:xx │ Apple    │ 22         │ (new)    │
└───────────────┴───────────────────┴──────────┴────────────┴──────────┘
```

### Power Integration

```bash
# Show power status of all devices
$ lantern power status
┌────────────┬────────────┬──────────┬─────────────┐
│ Device     │ Method     │ State    │ Since       │
├────────────┼────────────┼──────────┼─────────────┤
│ nas        │ WoL + SSH  │ ● On     │ 3 hours ago │
│ server     │ IPMI       │ ○ Off    │ 8 hours ago │
│ pi-media   │ Plug + SSH │ ● On     │ Always on   │
│ desk-lamp  │ Kasa       │ ○ Off    │ 2 hours ago │
└────────────┴────────────┴──────────┴─────────────┘

# Turn on a device (uses configured wake_method)
$ lantern power on nas
Sending WoL packet to 00:11:32:xx:xx:xx...
Waiting for device... ● Online (12s)

# Turn off a device (uses configured shutdown_method)
$ lantern power off nas
Connecting via SSH...
Running: sudo shutdown -h now
✓ Shutdown initiated

# Force power off via smart plug
$ lantern power off pi-media --force
Turning off smart plug "pi-plug"...
✓ Power cut

# Wake then connect
$ lantern wake nas --then ssh
Sending WoL packet...
Waiting for device... ● Online (14s)
Connecting via SSH...
admin@nas:~$

# Group power control
$ lantern power on-group workstation
[1/3] Waking nas (WoL)... ✓
[2/3] Powering on server (IPMI)... ✓
[3/3] Turning on desk-lamp (Kasa)... ✓
All devices powered on!
```

### Smart Plug Integration

```bash
# Discover smart plugs
$ lantern plugs discover
┌─────────────┬───────────────┬────────┬────────┬─────────┐
│ Name        │ IP            │ Vendor │ State  │ Power   │
├─────────────┼───────────────┼────────┼────────┼─────────┤
│ HS103-1234  │ 192.168.1.201 │ Kasa   │ ON     │ 45W     │
│ shelly1-abc │ 192.168.1.202 │ Shelly │ OFF    │ -       │
└─────────────┴───────────────┴────────┴────────┴─────────┘

# Control a plug directly
$ lantern plug desk-lamp on
✓ desk-lamp turned ON

$ lantern plug desk-lamp toggle
✓ desk-lamp turned OFF

# Check plug status with power consumption
$ lantern plug desk-lamp status
┌─────────────────────────────────┐
│ desk-lamp                       │
├─────────────────────────────────┤
│ State:   ● ON                   │
│ Power:   12.5W                  │
│ Voltage: 120V                   │
│ Today:   0.15 kWh               │
│ Month:   4.2 kWh                │
└─────────────────────────────────┘
```

---

## Python Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class PowerConfig:
    wake_method: Optional[str] = None      # wol, ipmi, plug
    shutdown_method: Optional[str] = None  # ssh, ipmi, plug
    shutdown_command: str = "sudo shutdown -h now"
    plug_device: Optional[str] = None      # Reference to smart plug
    ipmi_host: Optional[str] = None
    ipmi_user: Optional[str] = None

@dataclass
class Device:
    name: str
    ip: str
    mac: Optional[str] = None
    hostname: Optional[str] = None
    user: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    web_url: Optional[str] = None
    notes: Optional[str] = None
    added: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None
    device_type: str = "device"            # device, smart-plug
    vendor: Optional[str] = None           # For smart plugs: kasa, shelly, etc.
    power: Optional[PowerConfig] = None

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def can_ssh(self) -> bool:
        return "ssh" in self.tags

    def can_wake(self) -> bool:
        if self.power and self.power.wake_method:
            return True
        return self.mac is not None  # Default to WoL if MAC exists

    def can_shutdown(self) -> bool:
        if self.power and self.power.shutdown_method:
            return True
        return self.can_ssh()  # Default to SSH if available

    def is_smart_plug(self) -> bool:
        return self.device_type == "smart-plug"
```

### Registry Class

```python
from pathlib import Path
import tomli
import tomli_w

class DeviceRegistry:
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".config" / "lantern"
        self.devices_file = self.config_dir / "devices.toml"
        self._devices: dict[str, Device] = {}
        self._load()

    def _load(self) -> None:
        if self.devices_file.exists():
            with open(self.devices_file, "rb") as f:
                data = tomli.load(f)
            for name, d in data.get("devices", {}).items():
                self._devices[name] = Device(name=name, **d)

    def _save(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        data = {"devices": {}}
        for name, device in self._devices.items():
            data["devices"][name] = asdict(device)
        with open(self.devices_file, "wb") as f:
            tomli_w.dump(data, f)

    def get(self, name: str) -> Optional[Device]:
        return self._devices.get(name)

    def add(self, device: Device) -> None:
        self._devices[device.name] = device
        self._save()

    def remove(self, name: str) -> bool:
        if name in self._devices:
            del self._devices[name]
            self._save()
            return True
        return False

    def list(self) -> List[Device]:
        return list(self._devices.values())

    def find_by_ip(self, ip: str) -> Optional[Device]:
        for device in self._devices.values():
            if device.ip == ip:
                return device
        return None
```

---

## Auto-Discovery Integration

When running `lantern scan`, devices can be auto-suggested for adding:

```python
async def suggest_new_devices(registry: DeviceRegistry, scan_results: List[ScanResult]):
    """Compare scan results with registry, suggest new devices."""
    new_devices = []
    for result in scan_results:
        if not registry.find_by_ip(result.ip):
            new_devices.append(result)
    return new_devices
```

