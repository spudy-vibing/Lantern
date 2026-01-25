"""Device management commands."""

from typing import Annotated

import typer
from rich.table import Table

from lantern.config import DeviceConfig, get_config_manager
from lantern.core.context import get_context
from lantern.tools import register_tool

devices_app = typer.Typer(help="Manage saved devices.")


@devices_app.command("list")
def list_devices(
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """List all saved devices.

    Examples:
        lantern devices list
        lantern devices list --json
    """
    ctx = get_context()
    ctx.json_output = json_output
    manager = get_config_manager()

    devices = manager.list_devices()

    if json_output:
        ctx.output([d.to_dict() for d in devices])
        return

    if not devices:
        ctx.info("No saved devices. Use 'lantern devices add' to add one.")
        return

    table = Table(title=f"Saved Devices ({len(devices)})", show_header=True, header_style="bold")
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("IP Address")
    table.add_column("MAC Address")
    table.add_column("SSH User")

    for device in sorted(devices, key=lambda d: d.name):
        table.add_row(
            device.name,
            device.device_type,
            device.ip_address or "-",
            device.mac_address or "-",
            device.ssh_user or "-",
        )

    ctx.console.print()
    ctx.console.print(table)
    ctx.console.print()


@devices_app.command("add")
def add_device(
    name: Annotated[str, typer.Argument(help="Unique name for the device.")],
    ip: Annotated[
        str | None,
        typer.Option("--ip", "-i", help="IP address of the device."),
    ] = None,
    mac: Annotated[
        str | None,
        typer.Option("--mac", "-m", help="MAC address for Wake-on-LAN."),
    ] = None,
    hostname: Annotated[
        str | None,
        typer.Option("--hostname", "-h", help="Hostname of the device."),
    ] = None,
    device_type: Annotated[
        str,
        typer.Option("--type", "-t", help="Device type (server, printer, plug, etc)."),
    ] = "generic",
    ssh_user: Annotated[
        str | None,
        typer.Option("--ssh-user", "-u", help="SSH username."),
    ] = None,
    ssh_port: Annotated[
        int,
        typer.Option("--ssh-port", help="SSH port (default: 22)."),
    ] = 22,
    ssh_key: Annotated[
        str | None,
        typer.Option("--ssh-key", "-k", help="Path to SSH private key."),
    ] = None,
    notes: Annotated[
        str | None,
        typer.Option("--notes", "-n", help="Notes about the device."),
    ] = None,
) -> None:
    """Add or update a saved device.

    Examples:
        lantern devices add myserver --ip 192.168.1.100 --ssh-user admin
        lantern devices add nas --ip 192.168.1.50 --mac AA:BB:CC:DD:EE:FF --type server
        lantern devices add printer --ip 192.168.1.200 --type printer
    """
    ctx = get_context()
    manager = get_config_manager()

    if not ip and not mac and not hostname:
        ctx.error("At least one of --ip, --mac, or --hostname is required.")
        raise typer.Exit(1)

    # Check if device already exists
    existing = manager.get_device(name)
    action = "Updated" if existing else "Added"

    device = DeviceConfig(
        name=name,
        ip_address=ip,
        mac_address=mac,
        hostname=hostname,
        device_type=device_type,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
        ssh_key=ssh_key,
        notes=notes,
    )

    manager.add_device(device)
    ctx.success(f"{action} device '{name}'")

    # Show device details
    ctx.console.print(f"  Type: {device.device_type}")
    if device.ip_address:
        ctx.console.print(f"  IP: {device.ip_address}")
    if device.mac_address:
        ctx.console.print(f"  MAC: {device.mac_address}")
    if device.ssh_user:
        ctx.console.print(f"  SSH: {device.ssh_user}@{device.ip_address or device.hostname}")


@devices_app.command("remove")
def remove_device(
    name: Annotated[str, typer.Argument(help="Name of the device to remove.")],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation."),
    ] = False,
) -> None:
    """Remove a saved device.

    Examples:
        lantern devices remove myserver
        lantern devices remove myserver --force
    """
    ctx = get_context()
    manager = get_config_manager()

    device = manager.get_device(name)
    if not device:
        ctx.error(f"Device '{name}' not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Remove device '{name}'?")
        if not confirm:
            ctx.info("Cancelled.")
            raise typer.Exit(0)

    manager.remove_device(name)
    ctx.success(f"Removed device '{name}'")


@devices_app.command("show")
def show_device(
    name: Annotated[str, typer.Argument(help="Name of the device to show.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Show details of a saved device.

    Examples:
        lantern devices show myserver
        lantern devices show myserver --json
    """
    ctx = get_context()
    ctx.json_output = json_output
    manager = get_config_manager()

    device = manager.get_device(name)
    if not device:
        ctx.error(f"Device '{name}' not found.")
        raise typer.Exit(1)

    if json_output:
        ctx.output(device.to_dict())
        return

    from rich.panel import Panel

    lines = [f"[bold]{device.name}[/bold]", f"Type: {device.device_type}"]

    if device.ip_address:
        lines.append(f"IP Address: [cyan]{device.ip_address}[/cyan]")
    if device.mac_address:
        lines.append(f"MAC Address: {device.mac_address}")
    if device.hostname:
        lines.append(f"Hostname: {device.hostname}")
    if device.ssh_user:
        ssh_info = f"{device.ssh_user}@{device.ip_address or device.hostname}:{device.ssh_port}"
        lines.append(f"SSH: [green]{ssh_info}[/green]")
    if device.ssh_key:
        lines.append(f"SSH Key: {device.ssh_key}")
    if device.notes:
        lines.append(f"Notes: [dim]{device.notes}[/dim]")

    ctx.console.print()
    ctx.console.print(Panel("\n".join(lines), title="Device Details"))
    ctx.console.print()


@devices_app.command("import")
def import_from_scan(
    name: Annotated[str, typer.Argument(help="Name to assign to the device.")],
    ip: Annotated[str, typer.Argument(help="IP address from scan results.")],
    device_type: Annotated[
        str,
        typer.Option("--type", "-t", help="Device type."),
    ] = "generic",
    ssh_user: Annotated[
        str | None,
        typer.Option("--ssh-user", "-u", help="SSH username."),
    ] = None,
) -> None:
    """Import a device from network scan by IP.

    First run 'lantern scan' to see devices, then import:

    Examples:
        lantern devices import myrouter 192.168.1.1
        lantern devices import nas 192.168.1.50 --type server --ssh-user admin
    """
    import asyncio

    from lantern.platforms.factory import get_adapter
    from lantern.services.oui import lookup_vendor

    ctx = get_context()
    manager = get_config_manager()

    # Check if name already exists
    if manager.get_device(name):
        ctx.error(f"Device '{name}' already exists. Use 'lantern devices add' to update.")
        raise typer.Exit(1)

    # Look up MAC address from ARP table
    async def find_mac() -> str | None:
        adapter = get_adapter()
        arp_entries = await adapter.get_arp_table()
        for entry in arp_entries:
            if entry.ip_address == ip:
                return entry.mac_address
        return None

    ctx.info(f"Looking up MAC address for {ip}...")
    mac = asyncio.run(find_mac())

    vendor = None
    if mac:
        vendor = lookup_vendor(mac)
        ctx.console.print(f"  Found MAC: {mac}" + (f" ({vendor})" if vendor else ""))
    else:
        ctx.warning("Could not find MAC address in ARP table.")

    device = DeviceConfig(
        name=name,
        ip_address=ip,
        mac_address=mac,
        device_type=device_type,
        ssh_user=ssh_user,
        notes=f"Imported from scan. Vendor: {vendor}" if vendor else "Imported from scan.",
    )

    manager.add_device(device)
    ctx.success(f"Imported device '{name}'")


@register_tool
def register(app: typer.Typer) -> None:
    """Register the devices command group."""
    app.add_typer(devices_app, name="devices")
