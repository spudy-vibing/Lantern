"""Wake-on-LAN command."""

import asyncio
from typing import Annotated

import typer

from lantern.config import get_config_manager
from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.services.wol import get_subnet_broadcast, send_magic_packet
from lantern.tools import register_tool


def _run_wake(
    target: str,
    port: int,
    broadcast: str | None,
    count: int,
    json_output: bool,
) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_wake_async(target, port, broadcast, count, json_output))


async def _wake_async(
    target: str,
    port: int,
    broadcast: str | None,
    count: int,
    json_output: bool,
) -> None:
    """Send Wake-on-LAN magic packet."""
    ctx = get_context()
    ctx.json_output = json_output

    manager = get_config_manager()

    # Resolve target to MAC address
    mac: str | None = None
    device_name: str | None = None

    # Check if target is a device name
    device = manager.get_device(target)
    if device:
        device_name = device.name
        if device.mac_address:
            mac = device.mac_address
        elif device.ip_address:
            # Try to find MAC from ARP
            if not json_output:
                ctx.info(f"Looking up MAC address for {device.ip_address}...")
            adapter = get_adapter()
            arp_entries = await adapter.get_arp_table()
            for entry in arp_entries:
                if entry.ip_address == device.ip_address:
                    mac = entry.mac_address
                    break
    elif ":" in target or "-" in target or len(target) == 12:
        # Looks like a MAC address
        mac = target
    else:
        # Maybe an IP address - try ARP lookup
        if not json_output:
            ctx.info(f"Looking up MAC address for {target}...")
        adapter = get_adapter()
        arp_entries = await adapter.get_arp_table()
        for entry in arp_entries:
            if entry.ip_address == target:
                mac = entry.mac_address
                break

    if not mac:
        if device_name:
            ctx.error(f"Device '{device_name}' has no MAC address configured.")
            ctx.info("Update with: lantern devices add {device_name} --mac AA:BB:CC:DD:EE:FF")
        else:
            ctx.error(f"Could not find MAC address for '{target}'")
            ctx.info("Provide a MAC address directly, or ensure the device is in the ARP table.")
        raise typer.Exit(1)

    # Determine broadcast address
    if broadcast is None:
        # Try to determine from default interface
        adapter = get_adapter()
        default_if = await adapter.get_default_interface()
        if default_if and default_if.ipv4_address:
            broadcast = get_subnet_broadcast(default_if.ipv4_address)
        else:
            broadcast = "255.255.255.255"

    if not json_output:
        target_display = f"'{device_name}'" if device_name else mac
        ctx.info(f"Sending Wake-on-LAN to {target_display}...")

    # Send magic packets
    results = []
    for _i in range(count):
        result = send_magic_packet(mac, broadcast=broadcast, port=port)
        results.append(result)

        if not result.success:
            if json_output:
                ctx.output(result.to_dict())
            else:
                ctx.error(f"Failed to send magic packet: {result.error}")
            raise typer.Exit(1)

    if json_output:
        ctx.output({
            "mac_address": mac,
            "broadcast_address": broadcast,
            "port": port,
            "packets_sent": count,
            "success": True,
        })
    else:
        ctx.success(f"Sent {count} magic packet(s) to {mac}")
        ctx.console.print(f"  Broadcast: {broadcast}:{port}")
        ctx.console.print()
        ctx.console.print("[dim]Note: The device must have Wake-on-LAN enabled in BIOS/firmware.[/dim]")


@register_tool
def register(app: typer.Typer) -> None:
    """Register the wake command."""

    @app.command("wake")
    def wake(
        target: Annotated[
            str,
            typer.Argument(help="Device name, MAC address, or IP address."),
        ],
        port: Annotated[
            int,
            typer.Option("--port", "-p", help="UDP port (default: 9)."),
        ] = 9,
        broadcast: Annotated[
            str | None,
            typer.Option("--broadcast", "-b", help="Broadcast address."),
        ] = None,
        count: Annotated[
            int,
            typer.Option("--count", "-c", help="Number of packets to send."),
        ] = 3,
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Send Wake-on-LAN magic packet to wake a device.

        Target can be:
        - A saved device name (from 'lantern devices')
        - A MAC address (AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF)
        - An IP address (will look up MAC from ARP table)

        Examples:
            lantern wake myserver
            lantern wake AA:BB:CC:DD:EE:FF
            lantern wake 192.168.1.100
            lantern wake myserver --count 5
        """
        _run_wake(target, port, broadcast, count, json_output)
