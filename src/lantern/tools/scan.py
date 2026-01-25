"""Network device discovery command."""

import asyncio
from dataclasses import dataclass
from typing import Annotated

import typer
from rich.table import Table

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.services.device_id import (
    DEVICE_EMOJI,
    DeviceType,
    identify_device,
    infer_vendor_from_hostname,
    is_private_mac,
)
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
    device_type: DeviceType = DeviceType.UNKNOWN
    is_private_mac: bool = False

    def to_dict(self) -> dict[str, str | bool | None]:
        """Convert to dictionary."""
        return {
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "is_gateway": self.is_gateway,
            "device_type": self.device_type.value,
            "is_private_mac": self.is_private_mac,
        }


def _run_scan(json_output: bool = False, identify: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_scan_async(json_output, identify))


async def _scan_async(json_output: bool, identify: bool) -> None:
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
        is_gw = entry.ip_address == gateway_ip
        private_mac = is_private_mac(entry.mac_address) if entry.mac_address else False

        # If no vendor from OUI, try to infer from hostname
        if not vendor and entry.hostname:
            vendor = infer_vendor_from_hostname(entry.hostname)

        # Identify device type if requested
        device_type = DeviceType.UNKNOWN
        if identify and entry.mac_address:
            identification = identify_device(
                mac_address=entry.mac_address,
                hostname=entry.hostname,
                is_gateway=is_gw,
            )
            device_type = identification.device_type
            # Use identified vendor if we didn't find one from OUI
            if not vendor:
                vendor = identification.vendor

        devices.append(
            DiscoveredDevice(
                ip_address=entry.ip_address,
                mac_address=entry.mac_address,
                hostname=entry.hostname,
                vendor=vendor,
                is_gateway=is_gw,
                device_type=device_type,
                is_private_mac=private_mac,
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
    title = f"Network Devices ({len(devices)} found)"
    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("IP Address", style="cyan")
    table.add_column("MAC Address")
    table.add_column("Vendor")
    table.add_column("Hostname")

    if identify:
        table.add_column("Type", justify="center")

    table.add_column("", justify="center")  # Gateway/private marker

    for device in devices:
        # Build markers
        markers = []
        if device.is_gateway:
            markers.append("[green]⬤[/green]")
        if device.is_private_mac:
            markers.append("[dim]🔒[/dim]")
        marker = " ".join(markers)

        row = [
            device.ip_address,
            device.mac_address or "-",
            device.vendor or "-",
            device.hostname or "-",
        ]

        if identify:
            emoji = DEVICE_EMOJI.get(device.device_type, "")
            type_display = f"{emoji} {device.device_type.value}" if emoji else device.device_type.value
            row.append(type_display)

        row.append(marker)
        table.add_row(*row)

    ctx.console.print()
    ctx.console.print(table)
    ctx.console.print()

    # Legend
    legend_parts = []
    if gateway_ip:
        legend_parts.append("[green]⬤[/green] Gateway")
    if any(d.is_private_mac for d in devices):
        legend_parts.append("[dim]🔒[/dim] Private MAC (randomized)")

    if legend_parts:
        ctx.console.print("[dim]" + "  ".join(legend_parts) + "[/dim]")
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
        identify: Annotated[
            bool,
            typer.Option("--identify", "-i", help="Identify device types."),
        ] = False,
    ) -> None:
        """Scan network for connected devices.

        Discovers devices on your local network using the ARP table.
        Shows IP address, MAC address, vendor (manufacturer), and hostname.

        Use --identify to detect device types (phone, laptop, speaker, etc.)
        based on hostname patterns and vendor information.

        Examples:
            lantern scan              # Show all devices
            lantern scan --identify   # Identify device types
            lantern scan --json       # JSON output for scripting
        """
        _run_scan(json_output, identify)
