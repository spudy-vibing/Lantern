"""Device identification service.

Identifies device types using multiple methods:
1. MAC OUI lookup (vendor identification)
2. Hostname analysis (device type from hostname patterns)
3. Private MAC detection (Apple/Android privacy feature)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from lantern.services.oui import lookup_vendor


class DeviceType(str, Enum):
    """Common device types."""

    ROUTER = "router"
    COMPUTER = "computer"
    LAPTOP = "laptop"
    PHONE = "phone"
    TABLET = "tablet"
    WATCH = "watch"
    TV = "tv"
    SPEAKER = "speaker"
    PRINTER = "printer"
    CAMERA = "camera"
    IOT = "iot"
    GAME_CONSOLE = "game_console"
    STREAMING = "streaming"
    UNKNOWN = "unknown"


@dataclass
class DeviceIdentification:
    """Result of device identification."""

    device_type: DeviceType
    vendor: str | None
    is_private_mac: bool
    confidence: str  # "high", "medium", "low"
    method: str  # How it was identified

    def to_dict(self) -> dict[str, str | bool | None]:
        """Convert to dictionary."""
        return {
            "device_type": self.device_type.value,
            "vendor": self.vendor,
            "is_private_mac": self.is_private_mac,
            "confidence": self.confidence,
            "method": self.method,
        }


# Hostname patterns that indicate device type
HOSTNAME_PATTERNS: list[tuple[str, DeviceType, str]] = [
    # Apple devices
    (r"(?i)iphone", DeviceType.PHONE, "Apple"),
    (r"(?i)ipad", DeviceType.TABLET, "Apple"),
    (r"(?i)macbook|mbp|mba|.*-air$|.*air$", DeviceType.LAPTOP, "Apple"),
    (r"(?i)imac", DeviceType.COMPUTER, "Apple"),
    (r"(?i)mac-?mini|macmini", DeviceType.COMPUTER, "Apple"),
    (r"(?i)mac-?pro|macpro", DeviceType.COMPUTER, "Apple"),
    (r"(?i)^mac$", DeviceType.COMPUTER, "Apple"),  # Generic "mac" hostname
    (r"(?i)apple-?tv|appletv", DeviceType.TV, "Apple"),
    (r"(?i)apple-?watch|watch", DeviceType.WATCH, "Apple"),
    (r"(?i)homepod", DeviceType.SPEAKER, "Apple"),
    (r"(?i)airpods", DeviceType.SPEAKER, "Apple"),
    # Android devices
    (r"(?i)android|galaxy|pixel|oneplus|xiaomi", DeviceType.PHONE, None),
    (r"(?i)galaxy-?tab|kindle|fire-?hd", DeviceType.TABLET, None),
    # Computers
    (r"(?i)desktop|workstation|tower", DeviceType.COMPUTER, None),
    (r"(?i)laptop|notebook|thinkpad|xps|surface", DeviceType.LAPTOP, None),
    (r"(?i)pc|windows|win\d+", DeviceType.COMPUTER, None),
    # Network devices
    (r"(?i)router|gateway|cr\d+|netgear|linksys|asus-?rt", DeviceType.ROUTER, None),
    (r"(?i)\.mynetworksettings\.", DeviceType.ROUTER, None),  # Verizon routers
    # Smart home
    (r"(?i)echo|alexa|dot", DeviceType.SPEAKER, "Amazon"),
    (r"(?i)google-?home|nest-?hub|chromecast", DeviceType.SPEAKER, "Google"),
    (r"(?i)sonos|bose|soundbar", DeviceType.SPEAKER, None),
    (r"(?i)roku|fire-?tv|shield|nvidia-?shield", DeviceType.STREAMING, None),
    (r"(?i)smart-?tv|samsung-?tv|lg-?tv|vizio|bravia", DeviceType.TV, None),
    (r"(?i)nest|ring|arlo|wyze|blink", DeviceType.CAMERA, None),
    (r"(?i)hue|lifx|wemo|kasa|tapo|tp-?link", DeviceType.IOT, None),
    # Gaming
    (r"(?i)playstation|ps\d|xbox|nintendo|switch", DeviceType.GAME_CONSOLE, None),
    # Printers
    (r"(?i)printer|hp-?|epson|canon|brother|laserjet", DeviceType.PRINTER, None),
]

# Vendor to device type mapping (fallback when hostname doesn't help)
VENDOR_DEVICE_TYPES: dict[str, DeviceType] = {
    "Bose": DeviceType.SPEAKER,
    "Sonos": DeviceType.SPEAKER,
    "Roku": DeviceType.STREAMING,
    "Nest": DeviceType.IOT,
    "Ring": DeviceType.CAMERA,
    "Ecobee": DeviceType.IOT,
    "Philips Hue": DeviceType.IOT,
    "TP-Link": DeviceType.IOT,
    "Wistron": DeviceType.ROUTER,  # Often makes ISP routers
    "Arris": DeviceType.ROUTER,
    "Netgear": DeviceType.ROUTER,
    "Linksys": DeviceType.ROUTER,
    "Cisco-Linksys": DeviceType.ROUTER,
    "Canon": DeviceType.PRINTER,
    "HP": DeviceType.PRINTER,
    "Epson": DeviceType.PRINTER,
    "Brother": DeviceType.PRINTER,
    "Samsung": DeviceType.TV,
    "LG": DeviceType.TV,
    "Vizio": DeviceType.TV,
    "Sony": DeviceType.TV,
}


def infer_vendor_from_hostname(hostname: str | None) -> str | None:
    """Infer vendor from hostname patterns.

    Returns vendor name if hostname matches known patterns.
    """
    if not hostname:
        return None

    hostname_lower = hostname.lower()

    # Apple devices
    apple_patterns = [
        "iphone", "ipad", "macbook", "imac", "mac-mini", "macmini",
        "mac-pro", "macpro", "apple-tv", "appletv", "homepod",
        "airpods", "watch", "-air", "mbp", "mba",
    ]
    if any(p in hostname_lower for p in apple_patterns):
        return "Apple"
    if hostname_lower == "mac":
        return "Apple"

    # Amazon devices
    if any(p in hostname_lower for p in ["echo", "alexa", "kindle", "fire-"]):
        return "Amazon"

    # Google devices
    if any(p in hostname_lower for p in ["google-home", "nest-", "chromecast"]):
        return "Google"

    # Samsung
    if "galaxy" in hostname_lower or "samsung" in hostname_lower:
        return "Samsung"

    # Gaming consoles
    if "playstation" in hostname_lower or hostname_lower.startswith("ps"):
        return "Sony"
    if "xbox" in hostname_lower:
        return "Microsoft"
    if "nintendo" in hostname_lower or "switch" in hostname_lower:
        return "Nintendo"

    return None


def is_private_mac(mac_address: str) -> bool:
    """Check if MAC address is locally administered (private/randomized).

    Bit 1 of the first byte indicates locally administered addresses.
    These are typically randomized addresses used for privacy.
    """
    # Normalize and get first byte
    parts = mac_address.replace("-", ":").replace(".", ":").split(":")
    if len(parts) >= 1:
        try:
            first_byte = int(parts[0], 16)
            return (first_byte & 0x02) != 0
        except ValueError:
            pass
    return False


def identify_from_hostname(hostname: str | None) -> tuple[DeviceType, str | None, str] | None:
    """Identify device type from hostname.

    Returns:
        Tuple of (device_type, vendor_hint, confidence) or None
    """
    if not hostname:
        return None

    for pattern, device_type, vendor_hint in HOSTNAME_PATTERNS:
        if re.search(pattern, hostname):
            # Higher confidence for more specific matches
            if len(pattern) > 15:
                confidence = "high"
            elif len(pattern) > 8:
                confidence = "medium"
            else:
                confidence = "low"
            return (device_type, vendor_hint, confidence)

    return None


def identify_device(
    mac_address: str,
    hostname: str | None = None,
    is_gateway: bool = False,
) -> DeviceIdentification:
    """Identify a device using all available methods.

    Args:
        mac_address: Device MAC address
        hostname: Optional hostname
        is_gateway: Whether this device is marked as gateway

    Returns:
        DeviceIdentification with type, vendor, and confidence
    """
    # Check for private MAC
    private_mac = is_private_mac(mac_address)

    # Look up vendor
    vendor = lookup_vendor(mac_address)

    # If it's marked as gateway, it's a router
    if is_gateway:
        return DeviceIdentification(
            device_type=DeviceType.ROUTER,
            vendor=vendor,
            is_private_mac=private_mac,
            confidence="high",
            method="gateway",
        )

    # Try hostname identification first (most reliable for Apple devices with private MACs)
    hostname_result = identify_from_hostname(hostname)
    if hostname_result:
        device_type, vendor_hint, confidence = hostname_result
        return DeviceIdentification(
            device_type=device_type,
            vendor=vendor or vendor_hint,
            is_private_mac=private_mac,
            confidence=confidence,
            method="hostname",
        )

    # Try vendor-based identification
    if vendor and vendor in VENDOR_DEVICE_TYPES:
        return DeviceIdentification(
            device_type=VENDOR_DEVICE_TYPES[vendor],
            vendor=vendor,
            is_private_mac=private_mac,
            confidence="medium",
            method="vendor",
        )

    # Apple devices without specific hostname
    if vendor == "Apple":
        return DeviceIdentification(
            device_type=DeviceType.UNKNOWN,
            vendor=vendor,
            is_private_mac=private_mac,
            confidence="low",
            method="vendor",
        )

    # Unknown
    return DeviceIdentification(
        device_type=DeviceType.UNKNOWN,
        vendor=vendor,
        is_private_mac=private_mac,
        confidence="low",
        method="none",
    )


# Device type to emoji mapping for display
DEVICE_EMOJI: dict[DeviceType, str] = {
    DeviceType.ROUTER: "🌐",
    DeviceType.COMPUTER: "🖥️",
    DeviceType.LAPTOP: "💻",
    DeviceType.PHONE: "📱",
    DeviceType.TABLET: "📱",
    DeviceType.WATCH: "⌚",
    DeviceType.TV: "📺",
    DeviceType.SPEAKER: "🔊",
    DeviceType.PRINTER: "🖨️",
    DeviceType.CAMERA: "📷",
    DeviceType.IOT: "💡",
    DeviceType.GAME_CONSOLE: "🎮",
    DeviceType.STREAMING: "📺",
    DeviceType.UNKNOWN: "❓",
}
