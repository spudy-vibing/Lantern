"""Tests for configuration management."""

import pytest
from pathlib import Path
import tempfile

from lantern.config import (
    AppConfig,
    ConfigManager,
    DeviceConfig,
)


class TestDeviceConfig:
    """Tests for DeviceConfig."""

    def test_create_device_minimal(self) -> None:
        """Create device with minimal fields."""
        device = DeviceConfig(name="test")
        assert device.name == "test"
        assert device.mac_address is None
        assert device.ip_address is None
        assert device.device_type == "generic"
        assert device.ssh_port == 22

    def test_create_device_full(self) -> None:
        """Create device with all fields."""
        device = DeviceConfig(
            name="myserver",
            mac_address="AA:BB:CC:DD:EE:FF",
            ip_address="192.168.1.100",
            hostname="server.local",
            device_type="server",
            ssh_user="admin",
            ssh_port=2222,
            ssh_key="~/.ssh/id_rsa",
            notes="Production server",
        )
        assert device.name == "myserver"
        assert device.mac_address == "AA:BB:CC:DD:EE:FF"
        assert device.ip_address == "192.168.1.100"
        assert device.ssh_port == 2222

    def test_to_dict(self) -> None:
        """Convert device to dictionary."""
        device = DeviceConfig(
            name="test",
            ip_address="192.168.1.1",
            ssh_user="root",
        )
        d = device.to_dict()
        assert d["name"] == "test"
        assert d["ip_address"] == "192.168.1.1"
        assert d["ssh_user"] == "root"
        assert "mac_address" not in d  # None values excluded

    def test_from_dict(self) -> None:
        """Create device from dictionary."""
        data = {
            "ip_address": "192.168.1.50",
            "mac_address": "11:22:33:44:55:66",
            "device_type": "printer",
        }
        device = DeviceConfig.from_dict("office-printer", data)
        assert device.name == "office-printer"
        assert device.ip_address == "192.168.1.50"
        assert device.device_type == "printer"


class TestAppConfig:
    """Tests for AppConfig."""

    def test_default_values(self) -> None:
        """Check default configuration values."""
        config = AppConfig()
        assert config.json_output is False
        assert config.color is True
        assert config.ping_count == 5
        assert config.ping_timeout == 2.0

    def test_to_dict_minimal(self) -> None:
        """Empty config produces minimal dict."""
        config = AppConfig()
        d = config.to_dict()
        # Default values should not be included
        assert d == {}

    def test_to_dict_with_values(self) -> None:
        """Config with non-default values."""
        config = AppConfig(
            json_output=True,
            ping_count=10,
            ssh_default_user="admin",
        )
        d = config.to_dict()
        assert d["general"]["json_output"] is True
        assert d["network"]["ping_count"] == 10
        assert d["ssh"]["default_user"] == "admin"

    def test_from_dict(self) -> None:
        """Create config from dictionary."""
        data = {
            "general": {"verbose": True},
            "network": {"ping_count": 3},
            "ssh": {"default_user": "root"},
        }
        config = AppConfig.from_dict(data)
        assert config.verbose is True
        assert config.ping_count == 3
        assert config.ssh_default_user == "root"


class TestConfigManager:
    """Tests for ConfigManager."""

    def test_ensure_config_dir(self, tmp_path: Path) -> None:
        """Create config directory if it doesn't exist."""
        config_dir = tmp_path / "lantern_test"
        manager = ConfigManager(config_dir=config_dir)

        assert not config_dir.exists()
        manager.ensure_config_dir()
        assert config_dir.exists()

    def test_save_and_load_config(self, tmp_path: Path) -> None:
        """Save and load application config."""
        manager = ConfigManager(config_dir=tmp_path)

        config = AppConfig(ping_count=10, verbose=True)
        manager.save_config(config)

        # Clear cache and reload
        manager.clear_cache()
        loaded = manager.load_config()

        assert loaded.ping_count == 10
        assert loaded.verbose is True

    def test_save_and_load_devices(self, tmp_path: Path) -> None:
        """Save and load devices."""
        manager = ConfigManager(config_dir=tmp_path)

        device = DeviceConfig(
            name="testserver",
            ip_address="192.168.1.100",
            mac_address="AA:BB:CC:DD:EE:FF",
        )
        manager.add_device(device)

        # Clear cache and reload
        manager.clear_cache()
        loaded = manager.get_device("testserver")

        assert loaded is not None
        assert loaded.ip_address == "192.168.1.100"
        assert loaded.mac_address == "AA:BB:CC:DD:EE:FF"

    def test_remove_device(self, tmp_path: Path) -> None:
        """Remove a device."""
        manager = ConfigManager(config_dir=tmp_path)

        device = DeviceConfig(name="toremove", ip_address="192.168.1.1")
        manager.add_device(device)

        assert manager.get_device("toremove") is not None
        assert manager.remove_device("toremove") is True
        assert manager.get_device("toremove") is None
        assert manager.remove_device("toremove") is False  # Already gone

    def test_list_devices(self, tmp_path: Path) -> None:
        """List all devices."""
        manager = ConfigManager(config_dir=tmp_path)

        manager.add_device(DeviceConfig(name="device1", ip_address="192.168.1.1"))
        manager.add_device(DeviceConfig(name="device2", ip_address="192.168.1.2"))

        devices = manager.list_devices()
        assert len(devices) == 2
        names = {d.name for d in devices}
        assert names == {"device1", "device2"}

    def test_find_device_by_ip(self, tmp_path: Path) -> None:
        """Find device by IP address."""
        manager = ConfigManager(config_dir=tmp_path)

        manager.add_device(DeviceConfig(name="server", ip_address="192.168.1.100"))

        found = manager.find_device_by_ip("192.168.1.100")
        assert found is not None
        assert found.name == "server"

        not_found = manager.find_device_by_ip("192.168.1.999")
        assert not_found is None

    def test_find_device_by_mac(self, tmp_path: Path) -> None:
        """Find device by MAC address."""
        manager = ConfigManager(config_dir=tmp_path)

        manager.add_device(DeviceConfig(name="server", mac_address="AA:BB:CC:DD:EE:FF"))

        # Find with same format
        found = manager.find_device_by_mac("AA:BB:CC:DD:EE:FF")
        assert found is not None
        assert found.name == "server"

        # Find with different format (lowercase, dashes)
        found = manager.find_device_by_mac("aa-bb-cc-dd-ee-ff")
        assert found is not None
        assert found.name == "server"

    def test_update_device(self, tmp_path: Path) -> None:
        """Update an existing device."""
        manager = ConfigManager(config_dir=tmp_path)

        # Add initial device
        manager.add_device(DeviceConfig(name="server", ip_address="192.168.1.100"))

        # Update with new IP
        manager.add_device(DeviceConfig(name="server", ip_address="192.168.1.200"))

        device = manager.get_device("server")
        assert device is not None
        assert device.ip_address == "192.168.1.200"

        # Should still be only one device
        assert len(manager.list_devices()) == 1
