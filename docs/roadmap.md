# Roadmap - Lantern

## Feature Priority Matrix

Features are prioritized by **Impact** (how useful/delightful) vs **Effort** (complexity to implement).

```
                    HIGH IMPACT
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    │   QUICK WINS       │   BIG BETS         │
    │   (Do First)       │   (Plan Carefully) │
    │                    │                    │
    │  • share (QR)      │  • device registry │
    │  • drop (transfer) │  • ssh tools       │
    │  • whoami          │  • scan            │
    │  • port            │  • dashboard TUI   │
    │  • sonar           │                    │
    │                    │                    │
LOW ─┼────────────────────┼────────────────────┼─ HIGH
EFFORT                   │                    │  EFFORT
    │                    │                    │
    │   FILL-INS         │   MAYBE LATER      │
    │   (When Time)      │   (Reconsider)     │
    │                    │                    │
    │  • subnet calc     │  • plugin SDK      │
    │  • dns flush       │  • mqtt tools      │
    │  • hosts manager   │  • Windows support │
    │  • qr (general)    │  • cast/AirPlay    │
    │                    │                    │
    └────────────────────┼────────────────────┘
                         │
                    LOW IMPACT
```

---

## Ordered Feature Roadmap

### Tier 1: Foundation (Must Ship First)
| Feature | Command | Why First |
|---------|---------|-----------|
| Interface listing | `lantern interfaces` | Core functionality |
| Wi-Fi info | `lantern wifi info` | Most common use case |
| Diagnose summary | `lantern diagnose` | Immediate value |
| DNS info | `lantern dns info` | Debug staple |
| Router/gateway | `lantern router info` | Network basics |

### Tier 2: Viral Features (Ship Early)
| Feature | Command | Viral Potential |
|---------|---------|-----------------|
| Wi-Fi QR | `lantern share` | "Holy shit that's cool" moment |
| File drop | `lantern drop file.pdf` | AirDrop from terminal |
| Visual ping | `lantern sonar google.com` | Satisfying to watch |
| Public IP | `lantern whoami` | VPN verification |
| Port check | `lantern port 3000` | Daily dev need |

### Tier 3: Power User (Differentiators)
| Feature | Command | Power Level |
|---------|---------|-------------|
| Network scan | `lantern scan` | See all devices |
| Device registry | `lantern devices` | Name your devices |
| SSH manager | `lantern ssh pi` | Never forget IPs |
| Power control | `lantern power on/off` | Remote power management |
| Wake-on-LAN | `lantern wake nas --then ssh` | Wake and connect |
| Smart plugs | `lantern plug lamp toggle` | Control IoT devices |
| Web UI manager | `lantern web open router` | Quick access |

### Tier 4: Observability (Monitoring)
| Feature | Command | Use Case |
|---------|---------|----------|
| Network watcher | `lantern watch` | Detect changes |
| Bandwidth monitor | `lantern bw` | What's eating bandwidth |
| Signal heatmap | `lantern wifi heatmap` | Find best spot |
| Device uptime | `lantern uptime pi` | Is it still alive? |
| Power scheduling | `lantern power schedule` | Auto on/off times |
| Daemon mode | `lantern daemon` | Background service |

### Tier 5: Pro Tools (Advanced)
| Feature | Command | Audience |
|---------|---------|----------|
| Traceroute++ | `lantern trace` | Network debugging |
| SSL checker | `lantern ssl example.com` | Cert monitoring |
| Request catcher | `lantern catch` | Webhook debugging |
| Clipboard share | `lantern clip` | Cross-device workflow |

---

## Version Targets

### V1.0 - "It Works"
- All Tier 1 features
- JSON output support
- macOS primary, Linux basic

### V1.1 - "It's Delightful"
- All Tier 2 features
- OUI vendor lookup
- Improved error messages

### V2.0 - "It's Powerful"
- All Tier 3 features
- Configuration system
- Device registry
- Power management (wake/shutdown/smart plugs)

### V2.1 - "It's Always Watching"
- All Tier 4 features
- TUI dashboard
- Background monitoring

### V3.0 - "It's Extensible"
- All Tier 5 features
- Plugin SDK
- Community contributions

---

## Feature Dependencies

```
lantern interfaces ──┬──> lantern diagnose
lantern wifi info ───┘
lantern router info ─┘

lantern scan ────────┬──> lantern devices
                     ├──> lantern ssh list
                     ├──> lantern web list
                     ├──> lantern services
                     └──> lantern plugs discover

lantern devices ─────┬──> lantern ssh <name>
                     ├──> lantern wake <name>
                     ├──> lantern power on/off <name>
                     ├──> lantern shutdown <name>
                     └──> lantern web open <name>

lantern plugs ───────┬──> lantern plug <name> on/off
                     └──> lantern power (plug method)

lantern daemon ──────┬──> lantern power schedule
                     ├──> lantern watch (background)
                     └──> lantern uptime (continuous)

config.toml ─────────┬──> lantern devices
                     ├──> default settings
                     └──> lantern watch (persistence)
```

---

## Competitive Landscape

| Tool | What It Does | Lantern Advantage |
|------|--------------|-------------------|
| `ifconfig`/`ip` | Raw interface info | Better formatting, cross-platform |
| `nmap` | Network scanning | Simpler, safer defaults |
| `ping` | Connectivity test | Visual, sparklines |
| `ssh` | Remote connection | Device registry, discovery |
| `netstat` | Connections | Grouped by process, readable |
| `speedtest-cli` | Bandwidth test | Integrated (wrapper) |
| `wakeonlan` | WoL packets | Integrated with device registry, --then ssh |
| `kasa` CLI | Kasa plugs only | Multi-vendor, unified interface |
| Home Assistant | Full home automation | CLI-focused, no server needed |

