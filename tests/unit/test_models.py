"""Tests for data models."""


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


class TestNetworkInterface:
    """Tests for NetworkInterface model."""

    def test_create_interface(self) -> None:
        """Test creating a basic network interface."""
        iface = NetworkInterface(
            name="en0",
            type=InterfaceType.WIFI,
            status=InterfaceStatus.UP,
        )
        assert iface.name == "en0"
        assert iface.type == InterfaceType.WIFI
        assert iface.status == InterfaceStatus.UP
        assert iface.is_default is False

    def test_interface_with_all_fields(self) -> None:
        """Test creating interface with all fields."""
        iface = NetworkInterface(
            name="en0",
            type=InterfaceType.WIFI,
            status=InterfaceStatus.UP,
            mac_address="80:a9:97:33:cb:ed",
            ipv4_address="192.168.1.174",
            ipv4_netmask="255.255.255.0",
            ipv6_address="fe80::1",
            is_default=True,
        )
        assert iface.mac_address == "80:a9:97:33:cb:ed"
        assert iface.ipv4_address == "192.168.1.174"
        assert iface.is_default is True

    def test_interface_to_dict(self) -> None:
        """Test converting interface to dictionary."""
        iface = NetworkInterface(
            name="en0",
            type=InterfaceType.WIFI,
            status=InterfaceStatus.UP,
            ipv4_address="192.168.1.174",
            is_default=True,
        )
        data = iface.to_dict()
        assert data["name"] == "en0"
        assert data["type"] == "wifi"
        assert data["status"] == "up"
        assert data["ipv4_address"] == "192.168.1.174"
        assert data["is_default"] is True


class TestInterfaceType:
    """Tests for InterfaceType enum."""

    def test_interface_types(self) -> None:
        """Test interface type values."""
        assert InterfaceType.WIFI.value == "wifi"
        assert InterfaceType.ETHERNET.value == "ethernet"
        assert InterfaceType.LOOPBACK.value == "loopback"
        assert InterfaceType.VIRTUAL.value == "virtual"
        assert InterfaceType.BRIDGE.value == "bridge"
        assert InterfaceType.UNKNOWN.value == "unknown"


class TestInterfaceStatus:
    """Tests for InterfaceStatus enum."""

    def test_interface_status(self) -> None:
        """Test interface status values."""
        assert InterfaceStatus.UP.value == "up"
        assert InterfaceStatus.DOWN.value == "down"
        assert InterfaceStatus.UNKNOWN.value == "unknown"


class TestWifiInfo:
    """Tests for WifiInfo model."""

    def test_create_wifi_info(self) -> None:
        """Test creating Wi-Fi info."""
        wifi = WifiInfo(
            ssid="MyNetwork",
            channel=36,
            rssi=-52,
        )
        assert wifi.ssid == "MyNetwork"
        assert wifi.channel == 36
        assert wifi.rssi == -52

    def test_wifi_info_signal_quality(self) -> None:
        """Test signal quality calculation."""
        # Excellent signal
        wifi = WifiInfo(ssid="Test", rssi=-40)
        assert wifi.signal_quality == 100

        # Good signal
        wifi = WifiInfo(ssid="Test", rssi=-60)
        assert wifi.signal_quality == 80

        # Fair signal
        wifi = WifiInfo(ssid="Test", rssi=-70)
        assert wifi.signal_quality == 60

        # Weak signal
        wifi = WifiInfo(ssid="Test", rssi=-80)
        assert wifi.signal_quality == 40

        # Poor signal
        wifi = WifiInfo(ssid="Test", rssi=-90)
        assert wifi.signal_quality == 20

        # Very poor signal
        wifi = WifiInfo(ssid="Test", rssi=-100)
        assert wifi.signal_quality == 0

    def test_wifi_info_no_rssi(self) -> None:
        """Test signal quality with no RSSI."""
        wifi = WifiInfo(ssid="Test")
        assert wifi.signal_quality is None

    def test_wifi_info_to_dict(self) -> None:
        """Test converting Wi-Fi info to dictionary."""
        wifi = WifiInfo(
            ssid="MyNetwork",
            bssid="58:96:71:f2:8f:6c",
            channel=36,
            rssi=-52,
            noise=-89,
            tx_rate=867.0,
            security="WPA2 Personal",
            interface="en0",
        )
        data = wifi.to_dict()
        assert data["ssid"] == "MyNetwork"
        assert data["bssid"] == "58:96:71:f2:8f:6c"
        assert data["channel"] == 36
        assert data["rssi"] == -52
        # signal_quality = 2 * (rssi + 100) = 2 * 48 = 96
        assert data["signal_quality"] == 96


class TestWifiNetwork:
    """Tests for WifiNetwork model."""

    def test_create_wifi_network(self) -> None:
        """Test creating a Wi-Fi network."""
        network = WifiNetwork(
            ssid="MyNetwork",
            bssid="58:96:71:f2:8f:6c",
            channel=36,
            rssi=-52,
            security="WPA2",
        )
        assert network.ssid == "MyNetwork"
        assert network.is_current is False

    def test_wifi_network_current(self) -> None:
        """Test current network flag."""
        network = WifiNetwork(
            ssid="MyNetwork",
            bssid="58:96:71:f2:8f:6c",
            channel=36,
            rssi=-52,
            security="WPA2",
            is_current=True,
        )
        assert network.is_current is True

    def test_wifi_network_to_dict(self) -> None:
        """Test converting network to dictionary."""
        network = WifiNetwork(
            ssid="MyNetwork",
            bssid="58:96:71:f2:8f:6c",
            channel=36,
            rssi=-52,
            security="WPA2",
            is_current=True,
        )
        data = network.to_dict()
        assert data["ssid"] == "MyNetwork"
        assert data["is_current"] is True


class TestRouterInfo:
    """Tests for RouterInfo model."""

    def test_create_router_info(self) -> None:
        """Test creating router info."""
        router = RouterInfo(
            ip_address="192.168.1.1",
            interface="en0",
        )
        assert router.ip_address == "192.168.1.1"
        assert router.interface == "en0"
        assert router.mac_address is None

    def test_router_info_with_mac(self) -> None:
        """Test router info with MAC address."""
        router = RouterInfo(
            ip_address="192.168.1.1",
            interface="en0",
            mac_address="58:96:71:f2:8f:6c",
        )
        assert router.mac_address == "58:96:71:f2:8f:6c"

    def test_router_info_to_dict(self) -> None:
        """Test converting router info to dictionary."""
        router = RouterInfo(
            ip_address="192.168.1.1",
            interface="en0",
            mac_address="58:96:71:f2:8f:6c",
        )
        data = router.to_dict()
        assert data["ip_address"] == "192.168.1.1"
        assert data["interface"] == "en0"
        assert data["mac_address"] == "58:96:71:f2:8f:6c"


class TestDnsServer:
    """Tests for DnsServer model."""

    def test_create_dns_server(self) -> None:
        """Test creating DNS server."""
        server = DnsServer(address="8.8.8.8")
        assert server.address == "8.8.8.8"
        assert server.interface is None
        assert server.is_default is False

    def test_dns_server_default(self) -> None:
        """Test default DNS server."""
        server = DnsServer(
            address="192.168.1.1",
            interface="en0",
            is_default=True,
        )
        assert server.is_default is True

    def test_dns_server_to_dict(self) -> None:
        """Test converting DNS server to dictionary."""
        server = DnsServer(
            address="8.8.8.8",
            interface="en0",
            is_default=True,
        )
        data = server.to_dict()
        assert data["address"] == "8.8.8.8"
        assert data["is_default"] is True


class TestDnsInfo:
    """Tests for DnsInfo model."""

    def test_create_dns_info(self) -> None:
        """Test creating DNS info."""
        dns = DnsInfo()
        assert dns.servers == []
        assert dns.search_domains == []

    def test_dns_info_with_servers(self) -> None:
        """Test DNS info with servers."""
        dns = DnsInfo(
            servers=[
                DnsServer(address="192.168.1.1", is_default=True),
                DnsServer(address="8.8.8.8"),
            ],
            search_domains=["home.local", "local"],
        )
        assert len(dns.servers) == 2
        assert dns.servers[0].is_default is True
        assert len(dns.search_domains) == 2

    def test_dns_info_to_dict(self) -> None:
        """Test converting DNS info to dictionary."""
        dns = DnsInfo(
            servers=[DnsServer(address="8.8.8.8")],
            search_domains=["home.local"],
        )
        data = dns.to_dict()
        assert len(data["servers"]) == 1
        assert data["servers"][0]["address"] == "8.8.8.8"
        assert data["search_domains"] == ["home.local"]


class TestPingResult:
    """Tests for PingResult model."""

    def test_create_ping_result(self) -> None:
        """Test creating ping result."""
        result = PingResult(host="8.8.8.8")
        assert result.host == "8.8.8.8"
        assert result.success is False  # No packets received

    def test_ping_result_success(self) -> None:
        """Test successful ping result."""
        result = PingResult(
            host="8.8.8.8",
            ip_address="8.8.8.8",
            packets_sent=5,
            packets_received=5,
            packet_loss_percent=0.0,
            min_ms=10.0,
            avg_ms=12.0,
            max_ms=14.0,
        )
        assert result.success is True
        assert result.packet_loss_percent == 0.0

    def test_ping_result_partial_loss(self) -> None:
        """Test ping result with packet loss."""
        result = PingResult(
            host="8.8.8.8",
            packets_sent=5,
            packets_received=3,
            packet_loss_percent=40.0,
        )
        assert result.success is True  # Some packets received
        assert result.packet_loss_percent == 40.0

    def test_ping_result_to_dict(self) -> None:
        """Test converting ping result to dictionary."""
        result = PingResult(
            host="8.8.8.8",
            packets_sent=5,
            packets_received=5,
            avg_ms=12.0,
        )
        data = result.to_dict()
        assert data["host"] == "8.8.8.8"
        assert data["success"] is True
        assert data["avg_ms"] == 12.0


class TestArpEntry:
    """Tests for ArpEntry model."""

    def test_create_arp_entry(self) -> None:
        """Test creating ARP entry."""
        entry = ArpEntry(
            ip_address="192.168.1.1",
            mac_address="58:96:71:f2:8f:6c",
            interface="en0",
        )
        assert entry.ip_address == "192.168.1.1"
        assert entry.mac_address == "58:96:71:f2:8f:6c"
        assert entry.hostname is None

    def test_arp_entry_with_hostname(self) -> None:
        """Test ARP entry with hostname."""
        entry = ArpEntry(
            ip_address="192.168.1.100",
            mac_address="aa:bb:cc:dd:ee:ff",
            interface="en0",
            hostname="mydevice.local",
        )
        assert entry.hostname == "mydevice.local"

    def test_arp_entry_to_dict(self) -> None:
        """Test converting ARP entry to dictionary."""
        entry = ArpEntry(
            ip_address="192.168.1.1",
            mac_address="58:96:71:f2:8f:6c",
            interface="en0",
            hostname="router.local",
        )
        data = entry.to_dict()
        assert data["ip_address"] == "192.168.1.1"
        assert data["mac_address"] == "58:96:71:f2:8f:6c"
        assert data["hostname"] == "router.local"
