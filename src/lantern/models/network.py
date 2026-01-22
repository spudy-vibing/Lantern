"""Network-related data models."""

from dataclasses import dataclass, field
from enum import Enum


class InterfaceType(str, Enum):
    """Type of network interface."""

    ETHERNET = "ethernet"
    WIFI = "wifi"
    LOOPBACK = "loopback"
    BRIDGE = "bridge"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"


class InterfaceStatus(str, Enum):
    """Status of a network interface."""

    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class NetworkInterface:
    """Represents a network interface."""

    name: str
    type: InterfaceType
    status: InterfaceStatus
    mac_address: str | None = None
    ipv4_address: str | None = None
    ipv4_netmask: str | None = None
    ipv6_address: str | None = None
    mtu: int | None = None
    is_default: bool = False

    def to_dict(self) -> dict[str, str | int | bool | None]:
        """Convert to dictionary for JSON serialization."""
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
    bssid: str | None = None
    channel: int | None = None
    frequency: int | None = None
    rssi: int | None = None
    noise: int | None = None
    tx_rate: float | None = None
    security: str | None = None
    interface: str | None = None

    @property
    def signal_quality(self) -> int | None:
        """Convert RSSI to quality percentage (0-100)."""
        if self.rssi is None:
            return None
        return int(min(max(2 * (self.rssi + 100), 0), 100))

    def to_dict(self) -> dict[str, str | int | float | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "channel": self.channel,
            "frequency": self.frequency,
            "rssi": self.rssi,
            "noise": self.noise,
            "signal_quality": self.signal_quality,
            "tx_rate": self.tx_rate,
            "security": self.security,
            "interface": self.interface,
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

    @property
    def signal_quality(self) -> int:
        """Convert RSSI to quality percentage (0-100)."""
        return int(min(max(2 * (self.rssi + 100), 0), 100))

    def to_dict(self) -> dict[str, str | int | bool]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "channel": self.channel,
            "rssi": self.rssi,
            "signal_quality": self.signal_quality,
            "security": self.security,
            "is_current": self.is_current,
        }


@dataclass
class RouterInfo:
    """Router/gateway information."""

    ip_address: str
    interface: str
    mac_address: str | None = None
    hostname: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convert to dictionary for JSON serialization."""
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
    interface: str | None = None
    is_default: bool = False

    def to_dict(self) -> dict[str, str | bool | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "address": self.address,
            "interface": self.interface,
            "is_default": self.is_default,
        }


@dataclass
class DnsInfo:
    """DNS configuration information."""

    servers: list[DnsServer] = field(default_factory=list)
    search_domains: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[dict[str, str | bool | None]] | list[str]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "servers": [s.to_dict() for s in self.servers],
            "search_domains": self.search_domains,
        }


@dataclass
class PingResult:
    """Result of a ping operation."""

    host: str
    ip_address: str | None = None
    packets_sent: int = 0
    packets_received: int = 0
    packet_loss_percent: float = 0.0
    min_ms: float | None = None
    avg_ms: float | None = None
    max_ms: float | None = None
    stddev_ms: float | None = None

    @property
    def success(self) -> bool:
        """Check if ping was successful (at least one packet received)."""
        return self.packets_received > 0

    def to_dict(self) -> dict[str, str | int | float | bool | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "host": self.host,
            "ip_address": self.ip_address,
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "packet_loss_percent": self.packet_loss_percent,
            "min_ms": self.min_ms,
            "avg_ms": self.avg_ms,
            "max_ms": self.max_ms,
            "stddev_ms": self.stddev_ms,
            "success": self.success,
        }


@dataclass
class ArpEntry:
    """An entry in the ARP table."""

    ip_address: str
    mac_address: str
    interface: str | None = None
    hostname: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "interface": self.interface,
            "hostname": self.hostname,
        }
