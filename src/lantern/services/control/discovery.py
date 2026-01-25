"""Device discovery engine for the control system.

Discovers controllable devices on the network using multiple protocols:
- UPnP/SSDP for media devices, speakers, TVs
- mDNS for Apple devices and modern IoT
- Protocol-specific discovery (Roku, Kasa, etc.)
"""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lantern.services.control.base import ControllableDevice


@dataclass
class DiscoveredDevice:
    """A device discovered on the network before full identification."""

    ip_address: str
    protocol: str  # "upnp", "mdns", "roku", "kasa", etc.
    device_type: str = "unknown"
    name: str = ""
    manufacturer: str | None = None
    model: str | None = None
    location: str | None = None  # URL for device description (UPnP)
    services: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ip_address": self.ip_address,
            "protocol": self.protocol,
            "device_type": self.device_type,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "location": self.location,
            "services": self.services,
        }


class DeviceDiscovery:
    """Multi-protocol device discovery engine.

    Discovers devices on the local network that can be controlled.
    Supports UPnP/SSDP, mDNS, and protocol-specific discovery methods.
    """

    def __init__(self, timeout: float = 5.0) -> None:
        """Initialize the discovery engine.

        Args:
            timeout: Discovery timeout in seconds
        """
        self.timeout = timeout
        self._discovered: dict[str, DiscoveredDevice] = {}

    async def discover_all(self) -> list[DiscoveredDevice]:
        """Discover devices using all available protocols.

        Returns:
            List of discovered devices
        """
        # Run all discovery methods concurrently
        results = await asyncio.gather(
            self.discover_upnp(),
            self.discover_roku(),
            return_exceptions=True,
        )

        # Collect results (filter out exceptions)
        all_devices: list[DiscoveredDevice] = []
        for result in results:
            if isinstance(result, list):
                all_devices.extend(result)

        # Deduplicate by IP address (keep first discovered)
        seen_ips: set[str] = set()
        unique_devices: list[DiscoveredDevice] = []
        for device in all_devices:
            if device.ip_address not in seen_ips:
                seen_ips.add(device.ip_address)
                unique_devices.append(device)
                self._discovered[device.ip_address] = device

        return unique_devices

    async def discover_upnp(self) -> list[DiscoveredDevice]:
        """Discover UPnP devices using SSDP.

        Sends M-SEARCH request to find all UPnP devices on the network.

        Returns:
            List of discovered UPnP devices
        """
        # Single search for all devices
        try:
            devices = await self._ssdp_search("ssdp:all")
        except Exception:
            devices = []

        # Deduplicate by IP (keep device with most info)
        by_ip: dict[str, DiscoveredDevice] = {}
        for d in devices:
            existing = by_ip.get(d.ip_address)
            if not existing or (d.location and not existing.location):
                by_ip[d.ip_address] = d

        return list(by_ip.values())

    async def _ssdp_search(self, search_target: str) -> list[DiscoveredDevice]:
        """Perform SSDP M-SEARCH for a specific target.

        Args:
            search_target: The ST (search target) header value

        Returns:
            List of discovered devices
        """
        import time

        SSDP_ADDR = "239.255.255.250"
        SSDP_PORT = 1900

        # Build M-SEARCH request
        request = (
            "M-SEARCH * HTTP/1.1\r\n"
            f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
            'MAN: "ssdp:discover"\r\n'
            "MX: 3\r\n"
            f"ST: {search_target}\r\n"
            "\r\n"
        ).encode()

        devices: list[DiscoveredDevice] = []

        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)  # Short timeout per receive
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        try:
            sock.sendto(request, (SSDP_ADDR, SSDP_PORT))

            end_time = time.time() + self.timeout
            while time.time() < end_time:
                try:
                    data, addr = sock.recvfrom(4096)
                    response = data.decode("utf-8", errors="ignore")
                    device = self._parse_ssdp_response(response, addr[0])
                    if device:
                        devices.append(device)
                except (TimeoutError, OSError):
                    # Socket timeout, continue checking
                    continue
        finally:
            sock.close()

        return devices

    def _parse_ssdp_response(self, response: str, ip_address: str) -> DiscoveredDevice | None:
        """Parse an SSDP response into a DiscoveredDevice.

        Args:
            response: Raw SSDP response text
            ip_address: IP address of the responding device

        Returns:
            DiscoveredDevice or None if parsing fails
        """
        headers: dict[str, str] = {}
        for line in response.split("\r\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().upper()] = value.strip()

        location = headers.get("LOCATION")
        server = headers.get("SERVER", "")
        st = headers.get("ST", "")
        usn = headers.get("USN", "")

        # Skip if no location (can't get device info)
        if not location:
            return None

        # Determine device type from ST/USN
        device_type = "unknown"
        if "MediaRenderer" in st or "MediaRenderer" in usn:
            device_type = "speaker"
        elif "MediaServer" in st or "MediaServer" in usn:
            device_type = "media_server"
        elif "RenderingControl" in st:
            device_type = "speaker"

        # Try to extract manufacturer from SERVER header
        manufacturer = None
        if "Bose" in server:
            manufacturer = "Bose"
        elif "Sonos" in server:
            manufacturer = "Sonos"
        elif "Samsung" in server:
            manufacturer = "Samsung"
        elif "LG" in server:
            manufacturer = "LG"
        elif "Roku" in server:
            manufacturer = "Roku"

        return DiscoveredDevice(
            ip_address=ip_address,
            protocol="upnp",
            device_type=device_type,
            name=server.split("/")[0] if server else "",
            manufacturer=manufacturer,
            location=location,
            services=[st] if st else [],
            raw_data=headers,
        )

    async def discover_roku(self) -> list[DiscoveredDevice]:
        """Discover Roku devices using SSDP with Roku-specific ST.

        Returns:
            List of discovered Roku devices
        """
        devices = await self._ssdp_search("roku:ecp")

        # Mark as Roku devices
        for device in devices:
            device.protocol = "roku"
            device.device_type = "streaming"
            device.manufacturer = "Roku"

        return devices

    async def get_device_adapter(
        self, discovered: DiscoveredDevice
    ) -> ControllableDevice | None:
        """Create an appropriate device adapter for a discovered device.

        Args:
            discovered: The discovered device info

        Returns:
            A ControllableDevice implementation or None
        """
        # Import adapters here to avoid circular imports
        if discovered.protocol == "upnp":
            from lantern.services.control.protocols.upnp import create_upnp_device

            return await create_upnp_device(discovered)

        if discovered.protocol == "roku":
            from lantern.services.control.adapters.roku import RokuDevice

            return RokuDevice(
                device_id=f"roku_{discovered.ip_address}",
                name=discovered.name or f"Roku ({discovered.ip_address})",
                ip_address=discovered.ip_address,
            )

        return None

    async def discover_and_create_devices(self) -> list[ControllableDevice]:
        """Discover devices and create appropriate adapters.

        Returns:
            List of ControllableDevice instances
        """
        discovered = await self.discover_all()
        devices: list[ControllableDevice] = []

        for disc in discovered:
            try:
                device = await self.get_device_adapter(disc)
                if device:
                    devices.append(device)
            except Exception:
                continue  # Skip devices that fail to initialize

        return devices
