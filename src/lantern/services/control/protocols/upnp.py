"""UPnP/DLNA protocol adapter for device control.

Implements control of UPnP devices like speakers, TVs, and media renderers
using SOAP commands over HTTP.
"""

from __future__ import annotations

import re
import urllib.request
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree

from lantern.services.control.base import (
    PLAYBACK_CAPABILITY,
    POWER_CAPABILITY,
    VOLUME_CAPABILITY,
    ActionResult,
    Capability,
    ControllableDevice,
    DeviceState,
)
from lantern.services.control.discovery import DiscoveredDevice


class UPnPDevice(ControllableDevice):
    """UPnP device implementation.

    Supports standard UPnP/DLNA services:
    - RenderingControl (volume, mute)
    - AVTransport (playback control)
    - ConnectionManager
    """

    def __init__(
        self,
        device_id: str,
        name: str,
        ip_address: str,
        location: str,
        device_type: str = "speaker",
        manufacturer: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize a UPnP device.

        Args:
            device_id: Unique identifier
            name: Human-friendly name
            ip_address: Device IP address
            location: URL to device description XML
            device_type: Type of device
            manufacturer: Device manufacturer
            model: Device model
        """
        super().__init__(
            device_id=device_id,
            name=name,
            ip_address=ip_address,
            device_type=device_type,
            manufacturer=manufacturer,
            model=model,
        )
        self.location = location
        self._base_url = ""
        self._services: dict[str, str] = {}  # service_type -> control_url
        self._connected = False

    async def connect(self) -> bool:
        """Connect to the device and discover available services."""
        try:
            # Parse base URL from location
            parsed = urlparse(self.location)
            self._base_url = f"{parsed.scheme}://{parsed.netloc}"

            # Fetch and parse device description
            with urllib.request.urlopen(self.location, timeout=5) as response:
                xml_data = response.read()

            await self._parse_device_description(xml_data)
            self._connected = True
            self._state.is_online = True

            # Set up capabilities based on available services
            self._setup_capabilities()

            return True

        except Exception:
            self._connected = False
            self._state.is_online = False
            return False

    async def _parse_device_description(self, xml_data: bytes) -> None:
        """Parse UPnP device description XML.

        Extracts device info and available services.
        """
        # Remove namespace declarations and prefixes for easier parsing
        xml_str = xml_data.decode("utf-8")

        # Remove all xmlns declarations (both default and prefixed)
        xml_str = re.sub(r'\s+xmlns(?::\w+)?="[^"]*"', "", xml_str)

        # Remove namespace prefixes from tags (e.g., <bose:foo> -> <foo>)
        xml_str = re.sub(r"<(/?)(\w+):", r"<\1", xml_str)

        root = ElementTree.fromstring(xml_str)

        # Get device info
        device = root.find(".//device")
        if device is not None:
            friendly_name = device.findtext("friendlyName")
            if friendly_name:
                self.name = friendly_name

            manufacturer = device.findtext("manufacturer")
            if manufacturer:
                self.manufacturer = manufacturer

            model_name = device.findtext("modelName")
            if model_name:
                self.model = model_name

        # Find services
        for service in root.findall(".//service"):
            service_type = service.findtext("serviceType") or ""
            control_url = service.findtext("controlURL") or ""

            if control_url and not control_url.startswith("http"):
                if not control_url.startswith("/"):
                    control_url = "/" + control_url
                control_url = self._base_url + control_url

            # Store by service type suffix for easier lookup
            if "RenderingControl" in service_type:
                self._services["RenderingControl"] = control_url
            elif "AVTransport" in service_type:
                self._services["AVTransport"] = control_url
            elif "ConnectionManager" in service_type:
                self._services["ConnectionManager"] = control_url

    def _setup_capabilities(self) -> None:
        """Set up device capabilities based on available services."""
        if "RenderingControl" in self._services:
            self.add_capability(VOLUME_CAPABILITY)

        if "AVTransport" in self._services:
            self.add_capability(PLAYBACK_CAPABILITY)
            self.add_capability(
                Capability(
                    name="now_playing",
                    description="Current media information",
                    actions=["get"],
                    parameters=[],
                    category="media",
                )
            )

        # All devices support power (even if just status check)
        self.add_capability(POWER_CAPABILITY)

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        self._connected = False

    async def is_available(self) -> bool:
        """Check if device is reachable."""
        try:
            with urllib.request.urlopen(self.location, timeout=2):
                return True
        except Exception:
            return False

    async def execute(
        self,
        capability: str,
        action: str,
        **kwargs: Any,
    ) -> ActionResult:
        """Execute an action on a capability."""
        if not self._connected:
            connected = await self.connect()
            if not connected:
                return ActionResult(success=False, error="Device not connected")

        try:
            if capability == "volume":
                return await self._execute_volume(action, **kwargs)
            elif capability == "playback":
                return await self._execute_playback(action)
            elif capability == "power":
                return await self._execute_power(action)
            elif capability == "now_playing":
                return await self._get_now_playing()
            else:
                return ActionResult(success=False, error=f"Unknown capability: {capability}")

        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def _execute_volume(self, action: str, **kwargs: Any) -> ActionResult:
        """Execute volume-related actions."""
        control_url = self._services.get("RenderingControl")
        if not control_url:
            return ActionResult(success=False, error="RenderingControl service not available")

        if action == "get":
            # Get current volume
            response = self._soap_request(
                control_url,
                "RenderingControl",
                "GetVolume",
                {"InstanceID": "0", "Channel": "Master"},
            )
            if response:
                volume = self._extract_value(response, "CurrentVolume")
                if volume is not None:
                    self._state.set("volume", int(volume))
                    return ActionResult(success=True, value=int(volume))
            return ActionResult(success=False, error="Failed to get volume")

        elif action == "set":
            level = kwargs.get("level")
            if level is None:
                return ActionResult(success=False, error="Volume level required")

            level = max(0, min(100, int(level)))
            self._soap_request(
                control_url,
                "RenderingControl",
                "SetVolume",
                {"InstanceID": "0", "Channel": "Master", "DesiredVolume": str(level)},
            )
            self._state.set("volume", level)
            return ActionResult(success=True, value=level)

        elif action == "up":
            # Get current volume from device if not cached
            if "volume" not in self._state.values:
                await self._execute_volume("get")
            current = self._state.get("volume", 50)
            step = kwargs.get("step", 5)
            new_level = min(100, current + step)
            return await self._execute_volume("set", level=new_level)

        elif action == "down":
            # Get current volume from device if not cached
            if "volume" not in self._state.values:
                await self._execute_volume("get")
            current = self._state.get("volume", 50)
            step = kwargs.get("step", 5)
            new_level = max(0, current - step)
            return await self._execute_volume("set", level=new_level)

        elif action == "mute":
            self._soap_request(
                control_url,
                "RenderingControl",
                "SetMute",
                {"InstanceID": "0", "Channel": "Master", "DesiredMute": "1"},
            )
            self._state.set("muted", True)
            return ActionResult(success=True, value=True)

        elif action == "unmute":
            self._soap_request(
                control_url,
                "RenderingControl",
                "SetMute",
                {"InstanceID": "0", "Channel": "Master", "DesiredMute": "0"},
            )
            self._state.set("muted", False)
            return ActionResult(success=True, value=False)

        return ActionResult(success=False, error=f"Unknown volume action: {action}")

    async def _execute_playback(self, action: str) -> ActionResult:
        """Execute playback-related actions."""
        control_url = self._services.get("AVTransport")
        if not control_url:
            return ActionResult(success=False, error="AVTransport service not available")

        action_map = {
            "play": "Play",
            "pause": "Pause",
            "stop": "Stop",
            "next": "Next",
            "previous": "Previous",
        }

        upnp_action = action_map.get(action)
        if not upnp_action:
            return ActionResult(success=False, error=f"Unknown playback action: {action}")

        args = {"InstanceID": "0"}
        if action == "play":
            args["Speed"] = "1"

        self._soap_request(control_url, "AVTransport", upnp_action, args)
        return ActionResult(success=True)

    async def _execute_power(self, action: str) -> ActionResult:
        """Execute power-related actions.

        Note: Standard UPnP doesn't have power control, but some devices
        support standby via AVTransport.
        """
        if action == "get":
            # Check if device is responding
            available = await self.is_available()
            return ActionResult(success=True, value="on" if available else "off")

        # Power on/off not supported via standard UPnP
        return ActionResult(success=False, error="Power control not supported via UPnP")

    async def _get_now_playing(self) -> ActionResult:
        """Get current media information."""
        control_url = self._services.get("AVTransport")
        if not control_url:
            return ActionResult(success=False, error="AVTransport service not available")

        response = self._soap_request(
            control_url,
            "AVTransport",
            "GetPositionInfo",
            {"InstanceID": "0"},
        )

        if response:
            info = {
                "track": self._extract_value(response, "Track"),
                "duration": self._extract_value(response, "TrackDuration"),
                "position": self._extract_value(response, "RelTime"),
                "uri": self._extract_value(response, "TrackURI"),
            }

            # Try to get metadata
            metadata = self._extract_value(response, "TrackMetaData")
            if metadata and metadata != "NOT_IMPLEMENTED":
                # Parse DIDL-Lite metadata
                try:
                    meta_root = ElementTree.fromstring(metadata)
                    title = meta_root.findtext(".//{http://purl.org/dc/elements/1.1/}title")
                    artist = meta_root.findtext(".//{urn:schemas-upnp-org:metadata-1-0/upnp/}artist")
                    if title:
                        info["title"] = title
                    if artist:
                        info["artist"] = artist
                except Exception:
                    pass

            return ActionResult(success=True, value=info)

        return ActionResult(success=False, error="Failed to get playback info")

    async def refresh_state(self) -> DeviceState:
        """Refresh device state."""
        self._state.is_online = await self.is_available()

        if self._state.is_online and "RenderingControl" in self._services:
            # Get volume if available
            result = await self.execute("volume", "get")
            if result.success:
                self._state.set("volume", result.value)

        return self._state

    def _soap_request(
        self,
        control_url: str,
        service: str,
        action: str,
        arguments: dict[str, str],
    ) -> str | None:
        """Send a SOAP request to the device.

        Args:
            control_url: Service control URL
            service: Service name (e.g., "RenderingControl")
            action: Action name (e.g., "GetVolume")
            arguments: Action arguments

        Returns:
            Response XML string or None
        """
        # Build SOAP envelope
        args_xml = "".join(
            f"<{key}>{value}</{key}>" for key, value in arguments.items()
        )

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:{action} xmlns:u="urn:schemas-upnp-org:service:{service}:1">
            {args_xml}
        </u:{action}>
    </s:Body>
</s:Envelope>"""

        headers = {
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPAction": f'"urn:schemas-upnp-org:service:{service}:1#{action}"',
        }

        try:
            request = urllib.request.Request(
                control_url,
                data=soap_body.encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.read().decode("utf-8")
        except Exception:
            return None

    def _extract_value(self, xml_response: str, element_name: str) -> str | None:
        """Extract a value from SOAP response XML."""
        # Simple regex extraction (more robust than parsing namespaced XML)
        pattern = rf"<{element_name}[^>]*>([^<]*)</{element_name}>"
        match = re.search(pattern, xml_response, re.IGNORECASE)
        if match:
            return match.group(1)
        return None


async def create_upnp_device(discovered: DiscoveredDevice) -> UPnPDevice | None:
    """Create a UPnP device from discovery info.

    Args:
        discovered: Discovery information

    Returns:
        Configured UPnPDevice or None
    """
    if not discovered.location:
        return None

    device = UPnPDevice(
        device_id=f"upnp_{discovered.ip_address}",
        name=discovered.name or f"UPnP Device ({discovered.ip_address})",
        ip_address=discovered.ip_address,
        location=discovered.location,
        device_type=discovered.device_type,
        manufacturer=discovered.manufacturer,
        model=discovered.model,
    )

    # Connect to fetch device info and services
    connected = await device.connect()
    if not connected:
        return None

    return device
