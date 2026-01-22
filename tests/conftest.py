"""Shared test fixtures for Lantern."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lantern.core.executor import CommandExecutor, CommandResult

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def macos_fixtures() -> dict[str, str]:
    """Load macOS fixture files."""
    fixtures = {}
    macos_dir = FIXTURES_DIR / "macos"
    if macos_dir.exists():
        for f in macos_dir.glob("*.txt"):
            fixtures[f.stem] = f.read_text()
    return fixtures


@pytest.fixture
def mock_command_result() -> type[CommandResult]:
    """Factory for creating mock CommandResult objects."""

    def _create(
        command: str = "test",
        args: tuple[str, ...] = (),
        return_code: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> CommandResult:
        return CommandResult(
            command=command,
            args=args,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
        )

    return _create


@pytest.fixture
def mock_executor(macos_fixtures: dict[str, str]) -> Generator[MagicMock, None, None]:
    """Create a mock executor with fixture responses."""
    mock = MagicMock(spec=CommandExecutor)

    # Fixture mapping based on command and args
    fixture_map: dict[tuple[str, ...], str] = {
        ("networksetup", "-listallhardwareports"): "networksetup_ports",
        ("scutil", "--dns"): "scutil_dns",
        ("route", "-n", "get", "default"): "route_default",
        ("airport", "-I"): "airport_info",
        ("airport", "-s"): "airport_scan",
        ("arp", "-a"): "arp_table",
        ("system_profiler", "SPAirPortDataType", "-detailLevel", "basic"): "system_profiler_wifi",
    }

    async def mock_run(
        command: str, *args: str, timeout_ms: int | None = None, check: bool = True  # noqa: ARG001
    ) -> CommandResult:
        # Normalize command to base name
        base_cmd = command.split("/")[-1]

        # Try to find matching fixture
        key = (base_cmd, *args)
        fixture_name = fixture_map.get(key)

        if fixture_name and fixture_name in macos_fixtures:
            return CommandResult(
                command=command,
                args=args,
                return_code=0,
                stdout=macos_fixtures[fixture_name],
                stderr="",
            )

        # Handle ping specially
        if base_cmd == "ping" and "ping_output" in macos_fixtures:
            return CommandResult(
                command=command,
                args=args,
                return_code=0,
                stdout=macos_fixtures["ping_output"],
                stderr="",
            )

        # Handle ipconfig commands
        if base_cmd == "ipconfig":
            if "getifaddr" in args:
                return CommandResult(
                    command=command,
                    args=args,
                    return_code=0,
                    stdout="192.168.1.174\n",
                    stderr="",
                )
            if "getoption" in args and "subnet_mask" in args:
                return CommandResult(
                    command=command,
                    args=args,
                    return_code=0,
                    stdout="255.255.255.0\n",
                    stderr="",
                )

        # Handle dscacheutil
        if base_cmd == "dscacheutil" and "-flushcache" in args:
            return CommandResult(
                command=command,
                args=args,
                return_code=0,
                stdout="",
                stderr="",
            )

        # Default: return empty success result
        return CommandResult(
            command=command,
            args=args,
            return_code=0,
            stdout="",
            stderr="",
        )

    mock.run = AsyncMock(side_effect=mock_run)
    mock.find_command = MagicMock(return_value="/usr/bin/test")
    mock.command_exists = MagicMock(return_value=True)

    yield mock


@pytest.fixture
def patch_executor(mock_executor: MagicMock) -> Generator[MagicMock, None, None]:
    """Patch the global executor with mock."""
    with patch("lantern.core.executor.executor", mock_executor):  # noqa: SIM117
        with patch("lantern.platforms.macos.executor", mock_executor):
            yield mock_executor


@pytest.fixture
def mock_adapter(macos_fixtures: dict[str, str]) -> MagicMock:  # noqa: ARG001
    """Create a mock platform adapter."""
    from lantern.models.network import (
        DnsInfo,
        DnsServer,
        InterfaceStatus,
        InterfaceType,
        NetworkInterface,
        PingResult,
        RouterInfo,
        WifiInfo,
        WifiNetwork,
    )

    adapter = MagicMock()
    adapter.name = "macOS"

    # Mock interfaces
    adapter.get_interfaces = AsyncMock(
        return_value=[
            NetworkInterface(
                name="en0",
                type=InterfaceType.WIFI,
                status=InterfaceStatus.UP,
                mac_address="80:a9:97:33:cb:ed",
                ipv4_address="192.168.1.174",
                ipv4_netmask="255.255.255.0",
                is_default=True,
            ),
            NetworkInterface(
                name="en1",
                type=InterfaceType.ETHERNET,
                status=InterfaceStatus.DOWN,
                mac_address="36:c2:f0:66:c2:40",
            ),
        ]
    )

    adapter.get_default_interface = AsyncMock(
        return_value=NetworkInterface(
            name="en0",
            type=InterfaceType.WIFI,
            status=InterfaceStatus.UP,
            mac_address="80:a9:97:33:cb:ed",
            ipv4_address="192.168.1.174",
            is_default=True,
        )
    )

    # Mock Wi-Fi
    adapter.get_wifi_info = AsyncMock(
        return_value=WifiInfo(
            ssid="MyHomeNetwork",
            bssid="58:96:71:f2:8f:6c",
            channel=36,
            rssi=-52,
            noise=-89,
            tx_rate=867.0,
            security="WPA2 Personal",
            interface="en0",
        )
    )

    adapter.get_wifi_interface = AsyncMock(return_value="en0")

    adapter.scan_wifi = AsyncMock(
        return_value=[
            WifiNetwork(
                ssid="MyHomeNetwork",
                bssid="58:96:71:f2:8f:6c",
                channel=36,
                rssi=-52,
                security="WPA2(PSK/AES/AES)",
                is_current=True,
            ),
            WifiNetwork(
                ssid="NeighborWifi",
                bssid="a4:b1:c1:d2:e3:f4",
                channel=11,
                rssi=-68,
                security="WPA2(PSK/AES/AES)",
            ),
        ]
    )

    # Mock router
    adapter.get_router_info = AsyncMock(
        return_value=RouterInfo(
            ip_address="192.168.1.1",
            interface="en0",
            mac_address="58:96:71:f2:8f:6c",
        )
    )

    # Mock DNS
    adapter.get_dns_info = AsyncMock(
        return_value=DnsInfo(
            servers=[
                DnsServer(address="192.168.1.1", interface="en0", is_default=True),
                DnsServer(address="8.8.8.8"),
            ],
            search_domains=["home.local"],
        )
    )

    # Mock ping
    adapter.ping = AsyncMock(
        return_value=PingResult(
            host="8.8.8.8",
            ip_address="8.8.8.8",
            packets_sent=5,
            packets_received=5,
            packet_loss_percent=0.0,
            min_ms=10.567,
            avg_ms=12.098,
            max_ms=13.456,
            stddev_ms=1.023,
        )
    )

    # Mock DNS flush
    adapter.flush_dns_cache = AsyncMock(return_value=True)

    return adapter


@pytest.fixture
def patch_adapter(mock_adapter: MagicMock) -> Generator[MagicMock, None, None]:
    """Patch the adapter factory to return mock adapter."""
    with patch("lantern.platforms.factory.get_adapter", return_value=mock_adapter):  # noqa: SIM117
        with patch("lantern.platforms.factory.get_platform_adapter", return_value=mock_adapter):
            yield mock_adapter
