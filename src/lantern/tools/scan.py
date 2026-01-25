"""Network device discovery command."""

import asyncio
from dataclasses import dataclass
from typing import Annotated

import typer
from rich.table import Table

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.services.oui import lookup_vendor
from lantern.tools import register_tool


@dataclass
class DiscoveredDevice:
    """A discovered device on the network."""

    ip_address: str
    mac_address: str | None = None
    hostname: str | None = None
    vendor: str | None = None
    is_gateway: bool = False

    def to_dict(self) -> dict[str, str | bool | None]:
        """Convert to dictionary."""
        return {
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "is_gateway": self.is_gateway,
        }


def _run_scan(json_output: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_scan_async(json_output))


async def _scan_async(json_output: bool) -> None:
    """Scan network for devices."""
    ctx = get_context()
    ctx.json_output = json_output

    adapter = get_adapter()

    if not json_output:
        ctx.info("Scanning network for devices...")

    # Get ARP table
    arp_entries = await adapter.get_arp_table()

    # Get router info for marking gateway
    router_info = await adapter.get_router_info()
    gateway_ip = router_info.ip_address if router_info else None

    # Build device list
    devices: list[DiscoveredDevice] = []
    seen_ips: set[str] = set()

    for entry in arp_entries:
        if entry.ip_address in seen_ips:
            continue
        seen_ips.add(entry.ip_address)

        vendor = lookup_vendor(entry.mac_address) if entry.mac_address else None

        devices.append(
            DiscoveredDevice(
                ip_address=entry.ip_address,
                mac_address=entry.mac_address,
                hostname=entry.hostname,
                vendor=vendor,
                is_gateway=entry.ip_address == gateway_ip,
            )
        )

    # Sort by IP address (numeric)
    def ip_sort_key(d: DiscoveredDevice) -> tuple[int, ...]:
        try:
            return tuple(int(p) for p in d.ip_address.split("."))
        except ValueError:
            return (999, 999, 999, 999)

    devices.sort(key=ip_sort_key)

    if json_output:
        ctx.output([d.to_dict() for d in devices])
        return

    if not devices:
        ctx.warning("No devices found on the network.")
        ctx.info("Try running 'ping' to a few local IPs to populate the ARP cache.")
        return

    # Display table
    table = Table(title=f"Network Devices ({len(devices)} found)", show_header=True, header_style="bold")
    table.add_column("IP Address", style="cyan")
    table.add_column("MAC Address")
    table.add_column("Vendor")
    table.add_column("Hostname")
    table.add_column("", justify="center")  # Gateway marker

    for device in devices:
        marker = "[green]⬤[/green]" if device.is_gateway else ""
        table.add_row(
            device.ip_address,
            device.mac_address or "-",
            device.vendor or "-",
            device.hostname or "-",
            marker,
        )

    ctx.console.print()
    ctx.console.print(table)
    ctx.console.print()
    if gateway_ip:
        ctx.console.print("[dim][green]⬤[/green] = Gateway/Router[/dim]")
    ctx.console.print()


@register_tool
def register(app: typer.Typer) -> None:
    """Register the scan command."""

    @app.command("scan")
    def scan(
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Scan network for connected devices.

        Discovers devices on your local network using the ARP table.
        Shows IP address, MAC address, vendor (manufacturer), and hostname.

        Examples:
            lantern scan              # Show all devices
            lantern scan --json       # JSON output for scripting
        """
        _run_scan(json_output)
