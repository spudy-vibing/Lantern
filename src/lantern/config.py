"""Configuration management for Lantern.

Handles loading, saving, and accessing configuration from TOML files.
Uses ~/.config/lantern/ on Unix and ~/AppData/Local/lantern/ on Windows.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli_w

from lantern.constants import CONFIG_DIR


@dataclass
class DeviceConfig:
    """Configuration for a saved device."""

    name: str  # User-friendly nickname
    mac_address: str | None = None
    ip_address: str | None = None
    hostname: str | None = None
    device_type: str = "generic"  # generic, server, printer, plug, etc.
    ssh_user: str | None = None
    ssh_port: int = 22
    ssh_key: str | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        result: dict[str, Any] = {"name": self.name, "device_type": self.device_type}
        if self.mac_address:
            result["mac_address"] = self.mac_address
        if self.ip_address:
            result["ip_address"] = self.ip_address
        if self.hostname:
            result["hostname"] = self.hostname
        if self.ssh_user:
            result["ssh_user"] = self.ssh_user
        if self.ssh_port != 22:
            result["ssh_port"] = self.ssh_port
        if self.ssh_key:
            result["ssh_key"] = self.ssh_key
        if self.notes:
            result["notes"] = self.notes
        return result

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> DeviceConfig:
        """Create from dictionary."""
        return cls(
            name=name,
            mac_address=data.get("mac_address"),
            ip_address=data.get("ip_address"),
            hostname=data.get("hostname"),
            device_type=data.get("device_type", "generic"),
            ssh_user=data.get("ssh_user"),
            ssh_port=data.get("ssh_port", 22),
            ssh_key=data.get("ssh_key"),
            notes=data.get("notes"),
        )


@dataclass
class AppConfig:
    """Main application configuration."""

    # General settings
    default_interface: str | None = None
    json_output: bool = False
    color: bool = True
    verbose: bool = False

    # Network defaults
    ping_count: int = 5
    ping_timeout: float = 2.0
    scan_timeout: float = 2.0

    # SSH defaults
    ssh_default_user: str | None = None
    ssh_default_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        result: dict[str, Any] = {}

        # General section
        general: dict[str, Any] = {}
        if self.default_interface:
            general["default_interface"] = self.default_interface
        if self.json_output:
            general["json_output"] = self.json_output
        if not self.color:
            general["color"] = self.color
        if self.verbose:
            general["verbose"] = self.verbose
        if general:
            result["general"] = general

        # Network section
        network: dict[str, Any] = {}
        if self.ping_count != 5:
            network["ping_count"] = self.ping_count
        if self.ping_timeout != 2.0:
            network["ping_timeout"] = self.ping_timeout
        if self.scan_timeout != 2.0:
            network["scan_timeout"] = self.scan_timeout
        if network:
            result["network"] = network

        # SSH section
        ssh: dict[str, Any] = {}
        if self.ssh_default_user:
            ssh["default_user"] = self.ssh_default_user
        if self.ssh_default_key:
            ssh["default_key"] = self.ssh_default_key
        if ssh:
            result["ssh"] = ssh

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        """Create from dictionary."""
        general = data.get("general", {})
        network = data.get("network", {})
        ssh = data.get("ssh", {})

        return cls(
            default_interface=general.get("default_interface"),
            json_output=general.get("json_output", False),
            color=general.get("color", True),
            verbose=general.get("verbose", False),
            ping_count=network.get("ping_count", 5),
            ping_timeout=network.get("ping_timeout", 2.0),
            scan_timeout=network.get("scan_timeout", 2.0),
            ssh_default_user=ssh.get("default_user"),
            ssh_default_key=ssh.get("default_key"),
        )


@dataclass
class ConfigManager:
    """Manages loading and saving configuration files."""

    config_dir: Path = field(default_factory=lambda: CONFIG_DIR)
    _app_config: AppConfig | None = field(default=None, repr=False)
    _devices: dict[str, DeviceConfig] | None = field(default=None, repr=False)

    def ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def config_file(self) -> Path:
        """Path to main config file."""
        return self.config_dir / "config.toml"

    @property
    def devices_file(self) -> Path:
        """Path to devices file."""
        return self.config_dir / "devices.toml"

    # --- App Config ---

    def load_config(self) -> AppConfig:
        """Load application configuration."""
        if self._app_config is not None:
            return self._app_config

        if self.config_file.exists():
            with open(self.config_file, "rb") as f:
                data = tomllib.load(f)
            self._app_config = AppConfig.from_dict(data)
        else:
            self._app_config = AppConfig()

        return self._app_config

    def save_config(self, config: AppConfig | None = None) -> None:
        """Save application configuration."""
        if config is not None:
            self._app_config = config

        if self._app_config is None:
            return

        self.ensure_config_dir()
        data = self._app_config.to_dict()

        with open(self.config_file, "wb") as f:
            tomli_w.dump(data, f)

    def get_config(self) -> AppConfig:
        """Get current config, loading if needed."""
        return self.load_config()

    # --- Devices ---

    def load_devices(self) -> dict[str, DeviceConfig]:
        """Load saved devices."""
        if self._devices is not None:
            return self._devices

        if self.devices_file.exists():
            with open(self.devices_file, "rb") as f:
                data = tomllib.load(f)

            self._devices = {}
            devices_data = data.get("devices", {})
            for name, device_data in devices_data.items():
                self._devices[name] = DeviceConfig.from_dict(name, device_data)
        else:
            self._devices = {}

        return self._devices

    def save_devices(self) -> None:
        """Save devices to file."""
        if self._devices is None:
            return

        self.ensure_config_dir()
        data: dict[str, Any] = {"devices": {}}

        for name, device in self._devices.items():
            data["devices"][name] = device.to_dict()

        with open(self.devices_file, "wb") as f:
            tomli_w.dump(data, f)

    def get_device(self, name: str) -> DeviceConfig | None:
        """Get a device by name."""
        devices = self.load_devices()
        return devices.get(name)

    def add_device(self, device: DeviceConfig) -> None:
        """Add or update a device."""
        devices = self.load_devices()
        devices[device.name] = device
        self.save_devices()

    def remove_device(self, name: str) -> bool:
        """Remove a device by name. Returns True if removed."""
        devices = self.load_devices()
        if name in devices:
            del devices[name]
            self.save_devices()
            return True
        return False

    def list_devices(self) -> list[DeviceConfig]:
        """List all saved devices."""
        return list(self.load_devices().values())

    def find_device_by_ip(self, ip_address: str) -> DeviceConfig | None:
        """Find a device by IP address."""
        for device in self.load_devices().values():
            if device.ip_address == ip_address:
                return device
        return None

    def find_device_by_mac(self, mac_address: str) -> DeviceConfig | None:
        """Find a device by MAC address."""
        mac_normalized = mac_address.lower().replace("-", ":")
        for device in self.load_devices().values():
            if device.mac_address:
                device_mac = device.mac_address.lower().replace("-", ":")
                if device_mac == mac_normalized:
                    return device
        return None

    def clear_cache(self) -> None:
        """Clear cached config and devices (useful for testing)."""
        self._app_config = None
        self._devices = None


# Global config manager instance
_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """Get the global config manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Convenience function to get app config."""
    return get_config_manager().get_config()


def get_device(name: str) -> DeviceConfig | None:
    """Convenience function to get a device."""
    return get_config_manager().get_device(name)
