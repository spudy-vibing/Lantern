"""Integration tests for CLI commands."""

import json
from unittest.mock import MagicMock

from typer.testing import CliRunner

from lantern.cli import app

runner = CliRunner()


class TestInterfacesCommand:
    """Tests for the interfaces command."""

    def test_interfaces_help(self) -> None:
        """Test interfaces --help."""
        result = runner.invoke(app, ["interfaces", "--help"])
        assert result.exit_code == 0
        assert "network interfaces" in result.stdout.lower()

    def test_interfaces_json(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test interfaces --json output."""
        result = runner.invoke(app, ["interfaces", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "en0"
        assert data[0]["type"] == "wifi"

    def test_interfaces_table(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test interfaces table output."""
        result = runner.invoke(app, ["interfaces"])
        assert result.exit_code == 0
        assert "en0" in result.stdout
        assert "wifi" in result.stdout.lower()


class TestRouterCommand:
    """Tests for the router command."""

    def test_router_help(self) -> None:
        """Test router --help."""
        result = runner.invoke(app, ["router", "--help"])
        assert result.exit_code == 0

    def test_router_info_json(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test router info --json output."""
        result = runner.invoke(app, ["router", "info", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["ip_address"] == "192.168.1.1"
        assert data["interface"] == "en0"

    def test_router_info_table(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test router info table output."""
        result = runner.invoke(app, ["router", "info"])
        assert result.exit_code == 0
        assert "192.168.1.1" in result.stdout


class TestDnsCommand:
    """Tests for the dns command."""

    def test_dns_help(self) -> None:
        """Test dns --help."""
        result = runner.invoke(app, ["dns", "--help"])
        assert result.exit_code == 0

    def test_dns_info_json(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test dns info --json output."""
        result = runner.invoke(app, ["dns", "info", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "servers" in data
        assert len(data["servers"]) >= 1
        assert data["servers"][0]["address"] == "192.168.1.1"

    def test_dns_info_table(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test dns info table output."""
        result = runner.invoke(app, ["dns", "info"])
        assert result.exit_code == 0
        assert "192.168.1.1" in result.stdout

    def test_dns_flush(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test dns flush command."""
        result = runner.invoke(app, ["dns", "flush"])
        assert result.exit_code == 0
        assert "success" in result.stdout.lower() or "flush" in result.stdout.lower()


class TestWifiCommand:
    """Tests for the wifi command."""

    def test_wifi_help(self) -> None:
        """Test wifi --help."""
        result = runner.invoke(app, ["wifi", "--help"])
        assert result.exit_code == 0
        assert "info" in result.stdout
        assert "signal" in result.stdout
        assert "scan" in result.stdout

    def test_wifi_info_json(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test wifi info --json output."""
        result = runner.invoke(app, ["wifi", "info", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["connected"] is True
        assert data["ssid"] == "MyHomeNetwork"
        assert data["rssi"] == -52

    def test_wifi_info_table(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test wifi info table output."""
        result = runner.invoke(app, ["wifi", "info"])
        assert result.exit_code == 0
        assert "MyHomeNetwork" in result.stdout

    def test_wifi_scan_requires_flag(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test that wifi scan requires --scan flag."""
        result = runner.invoke(app, ["wifi", "scan"])
        assert result.exit_code == 0
        assert "--scan" in result.stdout

    def test_wifi_scan_json(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test wifi scan --scan --json output."""
        result = runner.invoke(app, ["wifi", "scan", "--scan", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["ssid"] == "MyHomeNetwork"


class TestDiagnoseCommand:
    """Tests for the diagnose command."""

    def test_diagnose_help(self) -> None:
        """Test diagnose --help."""
        result = runner.invoke(app, ["diagnose", "--help"])
        assert result.exit_code == 0
        assert "comprehensive" in result.stdout.lower() or "diagnostic" in result.stdout.lower()

    def test_diagnose_quick_json(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test diagnose --quick --json output."""
        result = runner.invoke(app, ["diagnose", "--quick", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "interfaces" in data
        assert "wifi" in data
        assert "router" in data
        assert "dns" in data
        # Quick mode skips connectivity test
        assert data["connectivity"] is None

    def test_diagnose_json(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test diagnose --json output (with connectivity)."""
        result = runner.invoke(app, ["diagnose", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "connectivity" in data
        assert data["connectivity"]["success"] is True

    def test_diagnose_table(self, patch_adapter: MagicMock) -> None:  # noqa: ARG002
        """Test diagnose table output."""
        result = runner.invoke(app, ["diagnose", "--quick"])
        assert result.exit_code == 0
        assert "en0" in result.stdout


class TestVersionCommand:
    """Tests for version flag."""

    def test_version(self) -> None:
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout or "lantern" in result.stdout.lower()


class TestMainHelp:
    """Tests for main app help."""

    def test_help(self) -> None:
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "interfaces" in result.stdout
        assert "router" in result.stdout
        assert "dns" in result.stdout
        assert "wifi" in result.stdout
        assert "diagnose" in result.stdout
