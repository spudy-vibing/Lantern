"""Abstract base class for platform adapters."""

from abc import ABC, abstractmethod

from lantern.models.network import (
    ArpEntry,
    DnsInfo,
    NetworkInterface,
    PingResult,
    RouterInfo,
    WifiInfo,
    WifiNetwork,
)


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific implementations.

    Each platform (macOS, Linux, Windows) implements this interface
    to provide consistent network information across operating systems.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the platform name (e.g., 'macOS', 'Linux')."""
        ...

    @abstractmethod
    async def get_interfaces(self) -> list[NetworkInterface]:
        """Get all network interfaces.

        Returns:
            List of NetworkInterface objects.
        """
        ...

    @abstractmethod
    async def get_default_interface(self) -> NetworkInterface | None:
        """Get the default network interface.

        Returns:
            The default NetworkInterface or None if not found.
        """
        ...

    @abstractmethod
    async def get_wifi_info(self) -> WifiInfo | None:
        """Get current Wi-Fi connection info.

        Returns:
            WifiInfo for current connection or None if not connected.
        """
        ...

    @abstractmethod
    async def get_wifi_interface(self) -> str | None:
        """Get the name of the Wi-Fi interface.

        Returns:
            Interface name (e.g., 'en0') or None if not found.
        """
        ...

    @abstractmethod
    async def scan_wifi(self) -> list[WifiNetwork]:
        """Scan for available Wi-Fi networks.

        Returns:
            List of WifiNetwork objects found.
        """
        ...

    @abstractmethod
    async def get_router_info(self) -> RouterInfo | None:
        """Get default gateway/router info.

        Returns:
            RouterInfo for the default gateway or None if not found.
        """
        ...

    @abstractmethod
    async def get_dns_info(self) -> DnsInfo:
        """Get DNS configuration.

        Returns:
            DnsInfo with servers and search domains.
        """
        ...

    @abstractmethod
    async def ping(
        self, host: str, count: int = 5, timeout: float = 2.0
    ) -> PingResult:
        """Ping a host.

        Args:
            host: Hostname or IP address to ping.
            count: Number of ping packets to send.
            timeout: Timeout in seconds for each packet.

        Returns:
            PingResult with statistics.
        """
        ...

    @abstractmethod
    async def get_arp_table(self) -> list[ArpEntry]:
        """Get ARP table entries.

        Returns:
            List of ArpEntry objects.
        """
        ...

    @abstractmethod
    async def flush_dns_cache(self) -> bool:
        """Flush the DNS cache.

        Returns:
            True if successful, False otherwise.
        """
        ...

    async def get_wifi_password(self, ssid: str) -> str | None:  # noqa: ARG002
        """Get saved Wi-Fi password for an SSID.

        Args:
            ssid: The SSID to get the password for.

        Returns:
            The password or None if not found/not supported.
        """
        return None
