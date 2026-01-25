"""Tests for Wake-on-LAN service."""

import pytest

from lantern.services.wol import (
    create_magic_packet,
    get_subnet_broadcast,
    normalize_mac,
)


class TestNormalizeMac:
    """Tests for MAC address normalization."""

    def test_colon_format(self) -> None:
        """Normalize colon-separated MAC."""
        result = normalize_mac("AA:BB:CC:DD:EE:FF")
        assert result == "AA:BB:CC:DD:EE:FF"

    def test_dash_format(self) -> None:
        """Normalize dash-separated MAC."""
        result = normalize_mac("AA-BB-CC-DD-EE-FF")
        assert result == "AA:BB:CC:DD:EE:FF"

    def test_no_separator(self) -> None:
        """Normalize MAC without separators."""
        result = normalize_mac("AABBCCDDEEFF")
        assert result == "AA:BB:CC:DD:EE:FF"

    def test_lowercase(self) -> None:
        """Normalize lowercase MAC."""
        result = normalize_mac("aa:bb:cc:dd:ee:ff")
        assert result == "AA:BB:CC:DD:EE:FF"

    def test_mixed_case(self) -> None:
        """Normalize mixed case MAC."""
        result = normalize_mac("Aa:Bb:Cc:Dd:Ee:Ff")
        assert result == "AA:BB:CC:DD:EE:FF"

    def test_invalid_length_short(self) -> None:
        """Reject MAC that's too short."""
        with pytest.raises(ValueError, match="Invalid MAC"):
            normalize_mac("AA:BB:CC")

    def test_invalid_length_long(self) -> None:
        """Reject MAC that's too long."""
        with pytest.raises(ValueError, match="Invalid MAC"):
            normalize_mac("AA:BB:CC:DD:EE:FF:00")

    def test_invalid_characters(self) -> None:
        """Reject MAC with invalid characters."""
        with pytest.raises(ValueError, match="Invalid MAC"):
            normalize_mac("GG:HH:II:JJ:KK:LL")


class TestCreateMagicPacket:
    """Tests for magic packet creation."""

    def test_packet_length(self) -> None:
        """Magic packet is 102 bytes."""
        packet = create_magic_packet("AA:BB:CC:DD:EE:FF")
        assert len(packet) == 102

    def test_packet_structure(self) -> None:
        """Magic packet has correct structure."""
        mac = "AA:BB:CC:DD:EE:FF"
        packet = create_magic_packet(mac)

        # First 6 bytes are 0xFF
        assert packet[:6] == b"\xff" * 6

        # Next 96 bytes are 16 repetitions of MAC
        mac_bytes = bytes.fromhex("AABBCCDDEEFF")
        for i in range(16):
            start = 6 + (i * 6)
            assert packet[start : start + 6] == mac_bytes

    def test_different_mac_formats(self) -> None:
        """Create packet from various MAC formats."""
        packet1 = create_magic_packet("AA:BB:CC:DD:EE:FF")
        packet2 = create_magic_packet("AA-BB-CC-DD-EE-FF")
        packet3 = create_magic_packet("aabbccddeeff")

        # All should produce the same packet
        assert packet1 == packet2 == packet3


class TestGetSubnetBroadcast:
    """Tests for subnet broadcast calculation."""

    def test_standard_24_subnet(self) -> None:
        """Calculate broadcast for /24 network."""
        broadcast = get_subnet_broadcast("192.168.1.100", "255.255.255.0")
        assert broadcast == "192.168.1.255"

    def test_standard_16_subnet(self) -> None:
        """Calculate broadcast for /16 network."""
        broadcast = get_subnet_broadcast("172.16.50.100", "255.255.0.0")
        assert broadcast == "172.16.255.255"

    def test_standard_8_subnet(self) -> None:
        """Calculate broadcast for /8 network."""
        broadcast = get_subnet_broadcast("10.50.100.150", "255.0.0.0")
        assert broadcast == "10.255.255.255"

    def test_cidr_25(self) -> None:
        """Calculate broadcast for /25 network."""
        # First half of .0 subnet
        broadcast = get_subnet_broadcast("192.168.1.50", "255.255.255.128")
        assert broadcast == "192.168.1.127"

        # Second half
        broadcast = get_subnet_broadcast("192.168.1.150", "255.255.255.128")
        assert broadcast == "192.168.1.255"

    def test_default_mask(self) -> None:
        """Use default /24 mask."""
        broadcast = get_subnet_broadcast("192.168.1.100")
        assert broadcast == "192.168.1.255"
