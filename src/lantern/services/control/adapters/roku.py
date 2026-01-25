"""Roku device adapter.

Controls Roku devices via the External Control Protocol (ECP) REST API.
"""

from __future__ import annotations

import urllib.request
from typing import Any
from xml.etree import ElementTree

from lantern.services.control.base import (
    PLAYBACK_CAPABILITY,
    POWER_CAPABILITY,
    ActionResult,
    Capability,
    ControllableDevice,
    DeviceState,
    Parameter,
    ParameterType,
)


class RokuDevice(ControllableDevice):
    """Roku device implementation using ECP.

    The External Control Protocol (ECP) is a RESTful API for controlling
    Roku devices over the network.
    """

    # Key codes for remote control simulation
    KEYS = {
        "home": "Home",
        "back": "Back",
        "select": "Select",
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
        "play": "Play",
        "pause": "Pause",
        "rewind": "Rev",
        "forward": "Fwd",
        "info": "Info",
        "volume_up": "VolumeUp",
        "volume_down": "VolumeDown",
        "mute": "VolumeMute",
        "power": "Power",
        "power_on": "PowerOn",
        "power_off": "PowerOff",
    }

    def __init__(
        self,
        device_id: str,
        name: str,
        ip_address: str,
    ) -> None:
        """Initialize a Roku device.

        Args:
            device_id: Unique identifier
            name: Human-friendly name
            ip_address: Device IP address
        """
        super().__init__(
            device_id=device_id,
            name=name,
            ip_address=ip_address,
            device_type="streaming",
            manufacturer="Roku",
        )
        self._base_url = f"http://{ip_address}:8060"
        self._connected = False
        self._apps: dict[str, str] = {}  # app_id -> app_name

    async def connect(self) -> bool:
        """Connect to the Roku and fetch device info."""
        try:
            # Fetch device info
            with urllib.request.urlopen(f"{self._base_url}/query/device-info", timeout=5) as response:
                xml_data = response.read()

            root = ElementTree.fromstring(xml_data)
            self.name = root.findtext("user-device-name") or root.findtext("friendly-device-name") or self.name
            self.model = root.findtext("model-name")

            # Fetch installed apps
            await self._fetch_apps()

            self._connected = True
            self._state.is_online = True
            self._setup_capabilities()

            return True

        except Exception:
            self._connected = False
            self._state.is_online = False
            return False

    async def _fetch_apps(self) -> None:
        """Fetch list of installed apps."""
        try:
            with urllib.request.urlopen(f"{self._base_url}/query/apps", timeout=5) as response:
                xml_data = response.read()

            root = ElementTree.fromstring(xml_data)
            for app in root.findall("app"):
                app_id = app.get("id", "")
                app_name = app.text or ""
                if app_id and app_name:
                    self._apps[app_id] = app_name

        except Exception:
            pass

    def _setup_capabilities(self) -> None:
        """Set up device capabilities."""
        # Power control
        self.add_capability(POWER_CAPABILITY)

        # Playback control
        self.add_capability(PLAYBACK_CAPABILITY)

        # Volume control (if TV)
        self.add_capability(
            Capability(
                name="volume",
                description="Volume control",
                actions=["up", "down", "mute"],
                parameters=[],
                category="audio",
            )
        )

        # Navigation
        self.add_capability(
            Capability(
                name="navigate",
                description="Navigation controls",
                actions=["up", "down", "left", "right", "select", "back", "home"],
                parameters=[],
                category="navigation",
            )
        )

        # App launching
        app_names = list(self._apps.values())
        self.add_capability(
            Capability(
                name="app",
                description="App launcher",
                actions=["list", "launch"],
                parameters=[
                    Parameter(
                        name="name",
                        param_type=ParameterType.STRING,
                        description="App name to launch",
                        choices=app_names[:10] if app_names else None,  # Limit choices
                    ),
                ],
                category="apps",
            )
        )

        # Remote keys
        self.add_capability(
            Capability(
                name="key",
                description="Send remote key press",
                actions=["press"],
                parameters=[
                    Parameter(
                        name="key",
                        param_type=ParameterType.ENUM,
                        description="Key to press",
                        choices=list(self.KEYS.keys()),
                    ),
                ],
                category="remote",
            )
        )

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        self._connected = False

    async def is_available(self) -> bool:
        """Check if device is reachable."""
        try:
            with urllib.request.urlopen(f"{self._base_url}/query/device-info", timeout=2):
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
            if capability == "power":
                return await self._execute_power(action)
            elif capability == "playback":
                return await self._execute_playback(action)
            elif capability == "volume":
                return await self._execute_volume(action)
            elif capability == "navigate":
                return await self._execute_navigate(action)
            elif capability == "app":
                return await self._execute_app(action, **kwargs)
            elif capability == "key":
                return await self._execute_key(**kwargs)
            else:
                return ActionResult(success=False, error=f"Unknown capability: {capability}")

        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def _execute_power(self, action: str) -> ActionResult:
        """Execute power actions."""
        if action == "get":
            available = await self.is_available()
            return ActionResult(success=True, value="on" if available else "off")
        elif action == "on":
            return await self._send_keypress("PowerOn")
        elif action == "off":
            return await self._send_keypress("PowerOff")
        elif action == "toggle":
            return await self._send_keypress("Power")
        return ActionResult(success=False, error=f"Unknown power action: {action}")

    async def _execute_playback(self, action: str) -> ActionResult:
        """Execute playback actions."""
        key_map = {
            "play": "Play",
            "pause": "Play",  # Play/Pause toggle
            "stop": "Back",  # No stop, use back
            "next": "Fwd",
            "previous": "Rev",
        }
        key = key_map.get(action)
        if key:
            return await self._send_keypress(key)
        return ActionResult(success=False, error=f"Unknown playback action: {action}")

    async def _execute_volume(self, action: str) -> ActionResult:
        """Execute volume actions."""
        key_map = {
            "up": "VolumeUp",
            "down": "VolumeDown",
            "mute": "VolumeMute",
        }
        key = key_map.get(action)
        if key:
            return await self._send_keypress(key)
        return ActionResult(success=False, error=f"Unknown volume action: {action}")

    async def _execute_navigate(self, action: str) -> ActionResult:
        """Execute navigation actions."""
        key_map = {
            "up": "Up",
            "down": "Down",
            "left": "Left",
            "right": "Right",
            "select": "Select",
            "back": "Back",
            "home": "Home",
        }
        key = key_map.get(action)
        if key:
            return await self._send_keypress(key)
        return ActionResult(success=False, error=f"Unknown navigate action: {action}")

    async def _execute_app(self, action: str, **kwargs: Any) -> ActionResult:
        """Execute app actions."""
        if action == "list":
            return ActionResult(success=True, value=self._apps)

        elif action == "launch":
            name = kwargs.get("name", "").lower()
            # Find app by name (case-insensitive partial match)
            app_id = None
            for aid, aname in self._apps.items():
                if name in aname.lower():
                    app_id = aid
                    break

            if not app_id:
                return ActionResult(success=False, error=f"App not found: {name}")

            return await self._launch_app(app_id)

        return ActionResult(success=False, error=f"Unknown app action: {action}")

    async def _execute_key(self, **kwargs: Any) -> ActionResult:
        """Execute key press."""
        key = kwargs.get("key")
        if not key:
            return ActionResult(success=False, error="Key name required")

        roku_key = self.KEYS.get(key)
        if not roku_key:
            return ActionResult(success=False, error=f"Unknown key: {key}")

        return await self._send_keypress(roku_key)

    async def _send_keypress(self, key: str) -> ActionResult:
        """Send a keypress to the Roku."""
        try:
            url = f"{self._base_url}/keypress/{key}"
            request = urllib.request.Request(url, method="POST", data=b"")
            with urllib.request.urlopen(request, timeout=5):
                pass
            return ActionResult(success=True)
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def _launch_app(self, app_id: str) -> ActionResult:
        """Launch an app by ID."""
        try:
            url = f"{self._base_url}/launch/{app_id}"
            request = urllib.request.Request(url, method="POST", data=b"")
            with urllib.request.urlopen(request, timeout=5):
                pass
            return ActionResult(success=True)
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def refresh_state(self) -> DeviceState:
        """Refresh device state."""
        self._state.is_online = await self.is_available()

        if self._state.is_online:
            # Get current app
            try:
                with urllib.request.urlopen(f"{self._base_url}/query/active-app", timeout=5) as response:
                    xml_data = response.read()

                root = ElementTree.fromstring(xml_data)
                app = root.find("app")
                if app is not None:
                    self._state.set("current_app", app.text)
                    self._state.set("current_app_id", app.get("id"))

            except Exception:
                pass

        return self._state
