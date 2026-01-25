"""Tests for HTTP server service."""

import tempfile
from pathlib import Path

import pytest

from lantern.services.http_server import (
    FileServer,
    ServerInfo,
    find_free_port,
    get_local_ip,
)


class TestGetLocalIp:
    """Tests for get_local_ip function."""

    def test_returns_ip_address(self) -> None:
        """Test that get_local_ip returns a valid IP address."""
        ip = get_local_ip()
        assert ip  # Not empty
        # Should be an IP address format
        parts = ip.split(".")
        assert len(parts) == 4
        for part in parts:
            assert part.isdigit()
            assert 0 <= int(part) <= 255


class TestFindFreePort:
    """Tests for find_free_port function."""

    def test_finds_port(self) -> None:
        """Test that find_free_port returns a valid port."""
        port = find_free_port()
        assert 8000 <= port <= 9000

    def test_finds_port_in_range(self) -> None:
        """Test custom port range."""
        port = find_free_port(start=9000, end=9100)
        assert 9000 <= port < 9100


class TestServerInfo:
    """Tests for ServerInfo dataclass."""

    def test_url_property(self) -> None:
        """Test URL property."""
        info = ServerInfo(
            host="192.168.1.100",
            port=8000,
            path=Path("/tmp/test"),
            is_directory=False,
        )
        assert info.url == "http://192.168.1.100:8000"

    def test_local_url_property(self) -> None:
        """Test local URL property."""
        info = ServerInfo(
            host="192.168.1.100",
            port=8080,
            path=Path("/tmp/test"),
            is_directory=True,
        )
        assert info.local_url == "http://localhost:8080"


class TestFileServer:
    """Tests for FileServer class."""

    def test_server_info_for_file(self) -> None:
        """Test server info for file serving."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = Path(f.name)

        try:
            server = FileServer(temp_path, port=8765)
            info = server.info
            assert info.port == 8765
            assert info.is_directory is False
            assert info.path == temp_path.resolve()
        finally:
            temp_path.unlink()

    def test_server_info_for_directory(self) -> None:
        """Test server info for directory serving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = FileServer(Path(tmpdir), port=8766)
            info = server.info
            assert info.port == 8766
            assert info.is_directory is True

    def test_server_info_properties(self) -> None:
        """Test that server info has correct properties."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = Path(f.name)

        try:
            server = FileServer(temp_path, port=8888, one_shot=True)
            info = server.info
            assert info.port == 8888
            assert info.host  # Has an IP
            assert "8888" in info.url
            assert "localhost:8888" in info.local_url
        finally:
            temp_path.unlink()

    def test_auto_port_selection(self) -> None:
        """Test automatic port selection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            server = FileServer(Path(tmpdir))
            assert 8000 <= server.port <= 9000
