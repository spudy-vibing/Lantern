"""Windows platform adapter implementation (stub)."""

from lantern.exceptions import PlatformNotSupportedError
from lantern.models.network import (
    ArpEntry,
    DnsInfo,
    NetworkInterface,
    PingResult,
    RouterInfo,
    WifiInfo,
    WifiNetwork,
)
from lantern.platforms.base import PlatformAdapter


class WindowsAdapter(PlatformAdapter):
    """Windows-specific implementation of PlatformAdapter.

    This is currently a stub that raises PlatformNotSupportedError
    for all methods. Full implementation will be added in a future version.
    """

    @property
    def name(self) -> str:
        """Return the platform name."""
        return "Windows"

    def _not_implemented(self, feature: str) -> PlatformNotSupportedError:
        """Create a PlatformNotSupportedError for the given feature."""
        return PlatformNotSupportedError("Windows", feature)

    async def get_interfaces(self) -> list[NetworkInterface]:
        """Get all network interfaces."""
        raise self._not_implemented("get_interfaces")

    async def get_default_interface(self) -> NetworkInterface | None:
        """Get the default network interface."""
        raise self._not_implemented("get_default_interface")

    async def get_wifi_info(self) -> WifiInfo | None:
        """Get current Wi-Fi connection info."""
        raise self._not_implemented("get_wifi_info")

    async def get_wifi_interface(self) -> str | None:
        """Get the name of the Wi-Fi interface."""
        raise self._not_implemented("get_wifi_interface")

    async def scan_wifi(self) -> list[WifiNetwork]:
        """Scan for available Wi-Fi networks."""
        raise self._not_implemented("scan_wifi")

    async def get_router_info(self) -> RouterInfo | None:
        """Get default gateway/router info."""
        raise self._not_implemented("get_router_info")

    async def get_dns_info(self) -> DnsInfo:
        """Get DNS configuration."""
        raise self._not_implemented("get_dns_info")

    async def ping(
        self,
        host: str,  # noqa: ARG002
        count: int = 5,  # noqa: ARG002
        timeout: float = 2.0,  # noqa: ARG002
    ) -> PingResult:
        """Ping a host."""
        raise self._not_implemented("ping")

    async def get_arp_table(self) -> list[ArpEntry]:
        """Get ARP table entries."""
        raise self._not_implemented("get_arp_table")

    async def flush_dns_cache(self) -> bool:
        """Flush the DNS cache."""
        raise self._not_implemented("flush_dns_cache")
