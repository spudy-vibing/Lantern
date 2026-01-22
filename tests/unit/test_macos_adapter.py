"""Tests for macOS platform adapter parsing logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lantern.core.executor import CommandResult
from lantern.platforms.macos import MacOSAdapter


@pytest.fixture
def adapter() -> MacOSAdapter:
    """Create a macOS adapter instance."""
    return MacOSAdapter()


class TestMacOSAdapterName:
    """Test adapter name property."""

    def test_name(self, adapter: MacOSAdapter) -> None:
        """Test that adapter name is macOS."""
        assert adapter.name == "macOS"


class TestGetInterfaces:
    """Tests for get_interfaces method."""

    @pytest.mark.asyncio
    async def test_get_interfaces(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing network interfaces."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "networksetup" and "-listallhardwareports" in args:
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["networksetup_ports"],
                    stderr="",
                )
            if base_cmd == "route":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["route_default"],
                    stderr="",
                )
            if base_cmd == "ipconfig":
                if "getifaddr" in args:
                    return CommandResult(
                        command=cmd,
                        args=args,
                        return_code=0,
                        stdout="192.168.1.174\n",
                        stderr="",
                    )
                if "getoption" in args:
                    return CommandResult(
                        command=cmd,
                        args=args,
                        return_code=0,
                        stdout="255.255.255.0\n",
                        stderr="",
                    )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            interfaces = await adapter.get_interfaces()

        assert len(interfaces) >= 1
        # Find the Wi-Fi interface
        wifi_iface = next((i for i in interfaces if i.name == "en0"), None)
        assert wifi_iface is not None
        assert wifi_iface.type.value == "wifi"
        assert wifi_iface.mac_address == "80:a9:97:33:cb:ed"


class TestGetWifiInfo:
    """Tests for get_wifi_info method."""

    @pytest.mark.asyncio
    async def test_get_wifi_info_airport(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing Wi-Fi info from airport command."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "airport" and "-I" in args:
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["airport_info"],
                    stderr="",
                )
            if base_cmd == "networksetup":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout="Hardware Port: Wi-Fi\nDevice: en0\nEthernet Address: N/A\n",
                    stderr="",
                )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            wifi = await adapter._get_wifi_info_airport()

        assert wifi is not None
        assert wifi.ssid == "MyHomeNetwork"
        assert wifi.rssi == -52
        assert wifi.noise == -89
        assert wifi.channel == 36
        assert wifi.tx_rate == 867.0

    @pytest.mark.asyncio
    async def test_get_wifi_info_system_profiler(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing Wi-Fi info from system_profiler."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "system_profiler":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["system_profiler_wifi"],
                    stderr="",
                )
            if base_cmd == "networksetup":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout="Hardware Port: Wi-Fi\nDevice: en0\nEthernet Address: N/A\n",
                    stderr="",
                )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            wifi = await adapter._get_wifi_info_system_profiler()

        assert wifi is not None
        assert wifi.ssid == "MyHomeNetwork"
        assert wifi.rssi == -52
        assert wifi.noise == -89
        assert wifi.channel == 36
        assert wifi.security == "WPA2 Personal"


class TestScanWifi:
    """Tests for scan_wifi method."""

    @pytest.mark.asyncio
    async def test_scan_wifi(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing Wi-Fi scan results."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "airport" and "-s" in args:
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["airport_scan"],
                    stderr="",
                )
            if base_cmd == "airport" and "-I" in args:
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["airport_info"],
                    stderr="",
                )
            if base_cmd == "networksetup":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout="Hardware Port: Wi-Fi\nDevice: en0\nEthernet Address: N/A\n",
                    stderr="",
                )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            networks = await adapter.scan_wifi()

        assert len(networks) >= 1
        # Find MyHomeNetwork
        home = next((n for n in networks if n.ssid == "MyHomeNetwork"), None)
        assert home is not None
        assert home.rssi == -52
        assert home.channel == 36


class TestGetRouterInfo:
    """Tests for get_router_info method."""

    @pytest.mark.asyncio
    async def test_get_router_info(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing router info."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "route":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["route_default"],
                    stderr="",
                )
            if base_cmd == "arp":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["arp_table"],
                    stderr="",
                )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            router = await adapter.get_router_info()

        assert router is not None
        assert router.ip_address == "192.168.1.1"
        assert router.interface == "en0"
        assert router.mac_address == "58:96:71:f2:8f:6c"


class TestGetDnsInfo:
    """Tests for get_dns_info method."""

    @pytest.mark.asyncio
    async def test_get_dns_info(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing DNS info."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "scutil":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["scutil_dns"],
                    stderr="",
                )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            dns = await adapter.get_dns_info()

        assert len(dns.servers) >= 1
        assert dns.servers[0].address == "192.168.1.1"
        assert "home.local" in dns.search_domains


class TestPing:
    """Tests for ping method."""

    @pytest.mark.asyncio
    async def test_ping(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing ping output."""
        mock_executor = MagicMock()

        async def mock_run(
            cmd: str, *args: str, timeout_ms: int | None = None, check: bool = True  # noqa: ARG001
        ) -> CommandResult:
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "ping":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["ping_output"],
                    stderr="",
                )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            result = await adapter.ping("8.8.8.8", count=5)

        assert result.success is True
        assert result.ip_address == "8.8.8.8"
        assert result.packets_sent == 5
        assert result.packets_received == 5
        assert result.packet_loss_percent == 0.0
        assert result.avg_ms == pytest.approx(12.098, rel=0.01)


class TestGetArpTable:
    """Tests for get_arp_table method."""

    @pytest.mark.asyncio
    async def test_get_arp_table(
        self, adapter: MacOSAdapter, macos_fixtures: dict[str, str]
    ) -> None:
        """Test parsing ARP table."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            base_cmd = cmd.split("/")[-1]
            if base_cmd == "arp":
                return CommandResult(
                    command=cmd,
                    args=args,
                    return_code=0,
                    stdout=macos_fixtures["arp_table"],
                    stderr="",
                )
            return CommandResult(
                command=cmd,
                args=args,
                return_code=1,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            entries = await adapter.get_arp_table()

        assert len(entries) >= 1
        # Find the router entry
        router = next((e for e in entries if e.ip_address == "192.168.1.1"), None)
        assert router is not None
        assert router.mac_address == "58:96:71:f2:8f:6c"


class TestFlushDnsCache:
    """Tests for flush_dns_cache method."""

    @pytest.mark.asyncio
    async def test_flush_dns_cache(self, adapter: MacOSAdapter) -> None:
        """Test DNS cache flush."""
        mock_executor = MagicMock()

        async def mock_run(cmd: str, *args: str, check: bool = True) -> CommandResult:  # noqa: ARG001
            return CommandResult(
                command=cmd,
                args=args,
                return_code=0,
                stdout="",
                stderr="",
            )

        mock_executor.run = AsyncMock(side_effect=mock_run)

        with patch("lantern.platforms.macos.executor", mock_executor):
            result = await adapter.flush_dns_cache()

        assert result is True


class TestInterfaceTypeGuessing:
    """Tests for interface type guessing."""

    def test_guess_wifi(self, adapter: MacOSAdapter) -> None:
        """Test guessing Wi-Fi interface type."""
        assert adapter._guess_interface_type("Wi-Fi", "en0").value == "wifi"
        assert adapter._guess_interface_type("AirPort", "en0").value == "wifi"

    def test_guess_ethernet(self, adapter: MacOSAdapter) -> None:
        """Test guessing Ethernet interface type."""
        assert adapter._guess_interface_type("Ethernet", "en1").value == "ethernet"
        assert adapter._guess_interface_type("Thunderbolt Ethernet", "en1").value == "ethernet"

    def test_guess_loopback(self, adapter: MacOSAdapter) -> None:
        """Test guessing loopback interface type."""
        assert adapter._guess_interface_type("Loopback", "lo0").value == "loopback"
        assert adapter._guess_interface_type("", "lo0").value == "loopback"

    def test_guess_bridge(self, adapter: MacOSAdapter) -> None:
        """Test guessing bridge interface type."""
        # Note: "Thunderbolt Bridge" matches ethernet first due to "thunderbolt"
        # A pure bridge would be detected by device name
        assert adapter._guess_interface_type("Network Bridge", "bridge0").value == "bridge"

    def test_guess_virtual(self, adapter: MacOSAdapter) -> None:
        """Test guessing virtual interface type."""
        assert adapter._guess_interface_type("", "utun0").value == "virtual"
        assert adapter._guess_interface_type("", "vmnet1").value == "virtual"

    def test_guess_unknown(self, adapter: MacOSAdapter) -> None:
        """Test unknown interface type."""
        assert adapter._guess_interface_type("Something", "xyz0").value == "unknown"
