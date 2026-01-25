"""Tests for QR code service."""

import pytest

from lantern.services.qr import (
    generate_qr_ascii,
    generate_qr_unicode,
    generate_wifi_qr_data,
)


class TestGenerateQrAscii:
    """Tests for generate_qr_ascii function."""

    def test_generate_basic_qr(self) -> None:
        """Test generating a basic QR code."""
        qr = generate_qr_ascii("test")
        assert qr  # Should not be empty
        assert "\n" in qr  # Should have multiple lines
        # Should contain block characters
        assert any(char in qr for char in ["█", "▀", "▄", " "])

    def test_generate_url_qr(self) -> None:
        """Test generating QR code for URL."""
        qr = generate_qr_ascii("https://example.com")
        assert qr
        # URL QR should be larger than simple text
        lines = qr.split("\n")
        assert len(lines) > 5

    def test_border_size(self) -> None:
        """Test border size affects output."""
        qr_small = generate_qr_ascii("test", border=0)
        qr_large = generate_qr_ascii("test", border=4)
        # Larger border should result in more content
        assert len(qr_large) > len(qr_small)


class TestGenerateQrUnicode:
    """Tests for generate_qr_unicode function."""

    def test_generate_basic_qr(self) -> None:
        """Test generating a basic Unicode QR code."""
        qr = generate_qr_unicode("test")
        assert qr
        assert "\n" in qr
        # Should use double-width characters
        assert "██" in qr or "  " in qr

    def test_inverted_qr(self) -> None:
        """Test inverted QR code is different."""
        qr_normal = generate_qr_unicode("test", invert=False)
        qr_inverted = generate_qr_unicode("test", invert=True)
        assert qr_normal != qr_inverted

    def test_border_size(self) -> None:
        """Test border size affects output."""
        qr_small = generate_qr_unicode("test", border=0)
        qr_large = generate_qr_unicode("test", border=4)
        assert len(qr_large) > len(qr_small)


class TestGenerateWifiQrData:
    """Tests for generate_wifi_qr_data function."""

    def test_wpa_network(self) -> None:
        """Test WPA network QR data."""
        data = generate_wifi_qr_data(
            ssid="MyNetwork",
            password="secret123",
            security="WPA2",
        )
        assert data == "WIFI:T:WPA;S:MyNetwork;P:secret123;;"

    def test_wpa3_network(self) -> None:
        """Test WPA3 network maps to WPA."""
        data = generate_wifi_qr_data(
            ssid="SecureNet",
            password="verysecret",
            security="WPA3",
        )
        assert data == "WIFI:T:WPA;S:SecureNet;P:verysecret;;"

    def test_wep_network(self) -> None:
        """Test WEP network QR data."""
        data = generate_wifi_qr_data(
            ssid="OldNetwork",
            password="wepkey",
            security="WEP",
        )
        assert data == "WIFI:T:WEP;S:OldNetwork;P:wepkey;;"

    def test_open_network(self) -> None:
        """Test open network (no password)."""
        data = generate_wifi_qr_data(
            ssid="FreeWifi",
            password=None,
            security="nopass",
        )
        assert data == "WIFI:T:nopass;S:FreeWifi;;"

    def test_hidden_network(self) -> None:
        """Test hidden network QR data."""
        data = generate_wifi_qr_data(
            ssid="HiddenNet",
            password="secret",
            security="WPA",
            hidden=True,
        )
        assert "H:true" in data
        assert data == "WIFI:T:WPA;S:HiddenNet;P:secret;H:true;;"

    def test_special_characters_escaped(self) -> None:
        """Test special characters are escaped."""
        # SSID with semicolon
        data = generate_wifi_qr_data(
            ssid="My;Network",
            password="pass;word",
            security="WPA",
        )
        assert "My\\;Network" in data
        assert "pass\\;word" in data

    def test_comma_escaped(self) -> None:
        """Test commas are escaped."""
        data = generate_wifi_qr_data(
            ssid="Net,work",
            password="pass,word",
            security="WPA",
        )
        assert "Net\\,work" in data
        assert "pass\\,word" in data

    def test_backslash_escaped(self) -> None:
        """Test backslashes are escaped."""
        data = generate_wifi_qr_data(
            ssid="Net\\work",
            password="pass\\word",
            security="WPA",
        )
        assert "Net\\\\work" in data
        assert "pass\\\\word" in data

    def test_default_security_with_password(self) -> None:
        """Test defaults to WPA when password provided."""
        data = generate_wifi_qr_data(
            ssid="TestNet",
            password="mypassword",
        )
        assert "T:WPA" in data

    def test_nopass_without_password(self) -> None:
        """Test nopass when no password provided."""
        data = generate_wifi_qr_data(
            ssid="OpenNet",
            password=None,
            security="OPEN",
        )
        assert "T:nopass" in data
        assert "P:" not in data
