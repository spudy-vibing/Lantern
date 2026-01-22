"""macOS platform adapter implementation."""

import contextlib
import re

from lantern.core.executor import executor
from lantern.exceptions import CommandNotFoundError
from lantern.models.network import (
    ArpEntry,
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
from lantern.platforms.base import PlatformAdapter


class MacOSAdapter(PlatformAdapter):
    """macOS-specific implementation of PlatformAdapter."""

    @property
    def name(self) -> str:
        """Return the platform name."""
        return "macOS"

    async def get_interfaces(self) -> list[NetworkInterface]:
        """Get all network interfaces using networksetup."""
        interfaces: list[NetworkInterface] = []

        # Get hardware ports
        result = await executor.run("networksetup", "-listallhardwareports", check=False)
        if not result.success:
            return interfaces

        # Parse hardware ports output
        current_name = None
        current_device = None
        current_mac = None

        for line in result.stdout.split("\n"):
            line = line.strip()
            if line.startswith("Hardware Port:"):
                current_name = line.split(":", 1)[1].strip()
            elif line.startswith("Device:"):
                current_device = line.split(":", 1)[1].strip()
            elif line.startswith("Ethernet Address:"):
                current_mac = line.split(":", 1)[1].strip()
                if current_mac == "N/A":
                    current_mac = None

                if current_device:
                    # Determine interface type
                    iface_type = self._guess_interface_type(current_name or "", current_device)

                    # Get IP info for this interface
                    ip_info = await self._get_interface_ip(current_device)

                    interfaces.append(
                        NetworkInterface(
                            name=current_device,
                            type=iface_type,
                            status=InterfaceStatus.UP if ip_info.get("ip") else InterfaceStatus.DOWN,
                            mac_address=current_mac,
                            ipv4_address=ip_info.get("ip"),
                            ipv4_netmask=ip_info.get("netmask"),
                        )
                    )

                current_name = None
                current_device = None
                current_mac = None

        # Mark default interface (get name directly to avoid recursion)
        default_name = await self._get_default_interface_name()
        if default_name:
            for iface in interfaces:
                if iface.name == default_name:
                    iface.is_default = True
                    break

        return interfaces

    async def _get_default_interface_name(self) -> str | None:
        """Get the name of the default interface without recursion."""
        result = await executor.run("route", "-n", "get", "default", check=False)
        if not result.success:
            return None

        for line in result.stdout.split("\n"):
            line = line.strip()
            if line.startswith("interface:"):
                return line.split(":", 1)[1].strip()
        return None

    async def _get_interface_ip(self, device: str) -> dict[str, str | None]:
        """Get IP address info for a specific interface."""
        result = await executor.run("ipconfig", "getifaddr", device, check=False)
        ip = result.stdout.strip() if result.success else None

        netmask = None
        if ip:
            result = await executor.run("ipconfig", "getoption", device, "subnet_mask", check=False)
            netmask = result.stdout.strip() if result.success else None

        return {"ip": ip, "netmask": netmask}

    def _guess_interface_type(self, name: str, device: str) -> InterfaceType:
        """Guess the interface type from its name."""
        name_lower = name.lower()
        device_lower = device.lower()

        if "wi-fi" in name_lower or "wifi" in name_lower or "airport" in name_lower:
            return InterfaceType.WIFI
        elif "ethernet" in name_lower or "thunderbolt" in name_lower:
            return InterfaceType.ETHERNET
        elif device_lower == "lo0" or "loopback" in name_lower:
            return InterfaceType.LOOPBACK
        elif "bridge" in name_lower or device_lower.startswith("bridge"):
            return InterfaceType.BRIDGE
        elif device_lower.startswith("utun") or device_lower.startswith("vmnet"):
            return InterfaceType.VIRTUAL
        return InterfaceType.UNKNOWN

    async def get_default_interface(self) -> NetworkInterface | None:
        """Get the default network interface."""
        interface_name = await self._get_default_interface_name()
        if not interface_name:
            return None

        # Get IP info for this interface
        ip_info = await self._get_interface_ip(interface_name)

        # Determine interface type
        iface_type = self._guess_interface_type("", interface_name)

        return NetworkInterface(
            name=interface_name,
            type=iface_type,
            status=InterfaceStatus.UP if ip_info.get("ip") else InterfaceStatus.DOWN,
            ipv4_address=ip_info.get("ip"),
            ipv4_netmask=ip_info.get("netmask"),
            is_default=True,
        )

    async def get_wifi_info(self) -> WifiInfo | None:
        """Get current Wi-Fi connection info.

        Tries airport command first (older macOS), then falls back to
        system_profiler (newer macOS where airport was removed).
        """
        # Try airport command first (may not exist on newer macOS)
        try:
            return await self._get_wifi_info_airport()
        except CommandNotFoundError:
            pass

        # Fall back to system_profiler
        return await self._get_wifi_info_system_profiler()

    async def _get_wifi_info_airport(self) -> WifiInfo | None:
        """Get Wi-Fi info using airport command (older macOS)."""
        airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

        result = await executor.run(airport_path, "-I", check=False)
        if not result.success:
            return None

        info: dict[str, str | int | float | None] = {}

        for line in result.stdout.split("\n"):
            line = line.strip()
            if ":" not in line:
                continue

            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()

            if key == "ssid":
                info["ssid"] = value
            elif key == "bssid":
                info["bssid"] = value
            elif key == "channel":
                channel_str = value.split(",")[0]
                with contextlib.suppress(ValueError):
                    info["channel"] = int(channel_str)
            elif key == "agrctlrssi":
                with contextlib.suppress(ValueError):
                    info["rssi"] = int(value)
            elif key == "agrctlnoise":
                with contextlib.suppress(ValueError):
                    info["noise"] = int(value)
            elif key == "lasttxrate":
                with contextlib.suppress(ValueError):
                    info["tx_rate"] = float(value)
            elif key == "link auth":
                info["security"] = value

        if not info.get("ssid"):
            return None

        wifi_interface = await self.get_wifi_interface()

        channel = info.get("channel")
        rssi = info.get("rssi")
        noise = info.get("noise")
        tx_rate = info.get("tx_rate")

        return WifiInfo(
            ssid=str(info.get("ssid", "")),
            bssid=str(info.get("bssid")) if info.get("bssid") else None,
            channel=int(channel) if isinstance(channel, int) else None,
            rssi=int(rssi) if isinstance(rssi, int) else None,
            noise=int(noise) if isinstance(noise, int) else None,
            tx_rate=float(tx_rate) if isinstance(tx_rate, (int, float)) else None,
            security=str(info.get("security")) if info.get("security") else None,
            interface=wifi_interface,
        )

    async def _get_wifi_info_system_profiler(self) -> WifiInfo | None:
        """Get Wi-Fi info using system_profiler (newer macOS)."""
        result = await executor.run(
            "system_profiler", "SPAirPortDataType", "-detailLevel", "basic",
            check=False
        )
        if not result.success:
            return None

        info: dict[str, str | int | float | None] = {}
        in_current_network = False

        for line in result.stdout.split("\n"):
            line_stripped = line.strip()

            # Look for "Current Network Information:" section
            if "Current Network Information:" in line:
                in_current_network = True
                continue

            if in_current_network:
                # End of current network section - check if we've moved to a different section
                is_section_end = (
                    line_stripped
                    and not line.startswith(" " * 8)
                    and ":" in line_stripped
                    and not line.startswith(" " * 12)
                )
                if is_section_end and info.get("ssid"):
                    break

                # Parse network name (SSID) - it's the first indented line after header
                if line.startswith(" " * 10) and ":" in line_stripped and not info.get("ssid"):
                    # The SSID is the key before the colon
                    ssid = line_stripped.split(":")[0].strip()
                    if ssid:
                        info["ssid"] = ssid

                # Parse properties
                if "PHY Mode:" in line:
                    pass  # Not using this currently
                elif "BSSID:" in line:
                    info["bssid"] = line_stripped.split(":", 1)[1].strip()
                elif "Channel:" in line:
                    channel_str = line_stripped.split(":", 1)[1].strip()
                    with contextlib.suppress(ValueError):
                        info["channel"] = int(channel_str.split(",")[0].split()[0])
                elif "Security:" in line:
                    info["security"] = line_stripped.split(":", 1)[1].strip()
                elif "Signal / Noise:" in line:
                    # Format: "Signal / Noise: -52 dBm / -89 dBm"
                    sn_str = line_stripped.split(":", 1)[1].strip()
                    parts = sn_str.split("/")
                    if len(parts) == 2:
                        with contextlib.suppress(ValueError):
                            info["rssi"] = int(parts[0].replace("dBm", "").strip())
                            info["noise"] = int(parts[1].replace("dBm", "").strip())
                elif "Transmit Rate:" in line:
                    tx_str = line_stripped.split(":", 1)[1].strip()
                    with contextlib.suppress(ValueError):
                        info["tx_rate"] = float(tx_str.replace("Mbps", "").strip())

        if not info.get("ssid"):
            return None

        wifi_interface = await self.get_wifi_interface()

        channel = info.get("channel")
        rssi = info.get("rssi")
        noise = info.get("noise")
        tx_rate = info.get("tx_rate")

        return WifiInfo(
            ssid=str(info.get("ssid", "")),
            bssid=str(info.get("bssid")) if info.get("bssid") else None,
            channel=int(channel) if isinstance(channel, int) else None,
            rssi=int(rssi) if isinstance(rssi, int) else None,
            noise=int(noise) if isinstance(noise, int) else None,
            tx_rate=float(tx_rate) if isinstance(tx_rate, (int, float)) else None,
            security=str(info.get("security")) if info.get("security") else None,
            interface=wifi_interface,
        )

    async def get_wifi_interface(self) -> str | None:
        """Get the name of the Wi-Fi interface."""
        result = await executor.run("networksetup", "-listallhardwareports", check=False)
        if not result.success:
            return None

        lines = result.stdout.split("\n")
        for i, line in enumerate(lines):
            if ("Wi-Fi" in line or "AirPort" in line) and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith("Device:"):
                    return next_line.split(":", 1)[1].strip()
        return None

    async def scan_wifi(self) -> list[WifiNetwork]:
        """Scan for available Wi-Fi networks.

        Note: Requires the airport command which may not be available
        on newer macOS versions (Sequoia+). Returns empty list if unavailable.
        """
        airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

        try:
            result = await executor.run(airport_path, "-s", check=False)
        except CommandNotFoundError:
            return []

        if not result.success:
            return []

        networks: list[WifiNetwork] = []
        current_wifi = await self.get_wifi_info()
        current_bssid = current_wifi.bssid if current_wifi else None

        lines = result.stdout.split("\n")
        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue

            # Parse the fixed-width format
            # SSID                             BSSID             RSSI CHANNEL HT CC SECURITY
            parts = line.split()
            if len(parts) < 5:
                continue

            # BSSID is always in format xx:xx:xx:xx:xx:xx
            bssid_idx = None
            for i, part in enumerate(parts):
                if re.match(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$", part):
                    bssid_idx = i
                    break

            if bssid_idx is None:
                continue

            ssid = " ".join(parts[:bssid_idx]) if bssid_idx > 0 else ""
            bssid = parts[bssid_idx]

            try:
                rssi = int(parts[bssid_idx + 1])
                channel = int(parts[bssid_idx + 2].split(",")[0])
            except (ValueError, IndexError):
                continue

            # Security is usually the last part(s)
            security = " ".join(parts[bssid_idx + 5:]) if len(parts) > bssid_idx + 5 else "Open"

            networks.append(
                WifiNetwork(
                    ssid=ssid,
                    bssid=bssid,
                    channel=channel,
                    rssi=rssi,
                    security=security if security else "Open",
                    is_current=bssid == current_bssid,
                )
            )

        return networks

    async def get_router_info(self) -> RouterInfo | None:
        """Get default gateway/router info."""
        result = await executor.run("route", "-n", "get", "default", check=False)
        if not result.success:
            return None

        gateway_ip = None
        interface = None

        for line in result.stdout.split("\n"):
            line = line.strip()
            if line.startswith("gateway:"):
                gateway_ip = line.split(":", 1)[1].strip()
            elif line.startswith("interface:"):
                interface = line.split(":", 1)[1].strip()

        if not gateway_ip or not interface:
            return None

        # Try to get MAC address from ARP
        mac_address = None
        arp_entries = await self.get_arp_table()
        for entry in arp_entries:
            if entry.ip_address == gateway_ip:
                mac_address = entry.mac_address
                break

        return RouterInfo(
            ip_address=gateway_ip,
            interface=interface,
            mac_address=mac_address,
        )

    async def get_dns_info(self) -> DnsInfo:
        """Get DNS configuration using scutil."""
        result = await executor.run("scutil", "--dns", check=False)
        if not result.success:
            return DnsInfo()

        servers: list[DnsServer] = []
        search_domains: list[str] = []
        seen_servers: set[str] = set()

        current_interface = None
        in_resolver = False

        for line in result.stdout.split("\n"):
            line = line.strip()

            if line.startswith("resolver"):
                in_resolver = True
                current_interface = None
            elif line.startswith("if_index"):
                # Extract interface name
                match = re.search(r"\((.+)\)", line)
                if match:
                    current_interface = match.group(1)
            elif line.startswith("nameserver[") and in_resolver:
                # Extract DNS server address
                match = re.search(r":\s*(.+)", line)
                if match:
                    server_addr = match.group(1).strip()
                    if server_addr not in seen_servers:
                        seen_servers.add(server_addr)
                        servers.append(
                            DnsServer(
                                address=server_addr,
                                interface=current_interface,
                                is_default=len(servers) == 0,
                            )
                        )
            elif line.startswith("search domain["):
                match = re.search(r":\s*(.+)", line)
                if match:
                    domain = match.group(1).strip()
                    if domain not in search_domains:
                        search_domains.append(domain)

        return DnsInfo(servers=servers, search_domains=search_domains)

    async def ping(
        self, host: str, count: int = 5, timeout: float = 2.0
    ) -> PingResult:
        """Ping a host."""
        result = await executor.run(
            "ping",
            "-c", str(count),
            "-W", str(int(timeout * 1000)),  # macOS uses milliseconds
            host,
            check=False,
            timeout_ms=int((count * timeout + 5) * 1000),
        )

        ping_result = PingResult(host=host)

        # Parse output
        for line in result.stdout.split("\n"):
            # Get resolved IP
            if "PING" in line:
                match = re.search(r"PING .+ \((.+?)\)", line)
                if match:
                    ping_result.ip_address = match.group(1)

            # Get statistics
            if "packets transmitted" in line:
                match = re.search(
                    r"(\d+) packets transmitted, (\d+) (?:packets )?received",
                    line,
                )
                if match:
                    ping_result.packets_sent = int(match.group(1))
                    ping_result.packets_received = int(match.group(2))
                    if ping_result.packets_sent > 0:
                        ping_result.packet_loss_percent = (
                            (ping_result.packets_sent - ping_result.packets_received)
                            / ping_result.packets_sent
                            * 100
                        )

            # Get timing stats
            if "min/avg/max" in line:
                match = re.search(
                    r"(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)",
                    line,
                )
                if match:
                    ping_result.min_ms = float(match.group(1))
                    ping_result.avg_ms = float(match.group(2))
                    ping_result.max_ms = float(match.group(3))
                    ping_result.stddev_ms = float(match.group(4))

        return ping_result

    async def get_arp_table(self) -> list[ArpEntry]:
        """Get ARP table entries."""
        result = await executor.run("arp", "-a", check=False)
        if not result.success:
            return []

        entries: list[ArpEntry] = []

        for line in result.stdout.split("\n"):
            # Format: hostname (ip) at mac on interface [...]
            match = re.match(
                r"(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+(\S+)\s+on\s+(\S+)",
                line,
            )
            if match:
                hostname = match.group(1)
                ip = match.group(2)
                mac = match.group(3)
                interface = match.group(4)

                # Skip incomplete entries
                if mac == "(incomplete)":
                    continue

                entries.append(
                    ArpEntry(
                        ip_address=ip,
                        mac_address=mac,
                        interface=interface,
                        hostname=hostname if hostname != "?" else None,
                    )
                )

        return entries

    async def flush_dns_cache(self) -> bool:
        """Flush the DNS cache using dscacheutil."""
        result = await executor.run("dscacheutil", "-flushcache", check=False)
        return result.success

    async def get_wifi_password(self, ssid: str) -> str | None:
        """Get saved Wi-Fi password from Keychain."""
        result = await executor.run(
            "security",
            "find-generic-password",
            "-D", "AirPort network password",
            "-s", ssid,
            "-w",
            check=False,
        )
        if result.success:
            return result.stdout.strip()
        return None
