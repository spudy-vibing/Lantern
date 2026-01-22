"""Network interfaces command."""

import asyncio
from typing import Annotated

import typer
from rich.table import Table

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.tools import register_tool


def _run_interfaces(json_output: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_interfaces_async(json_output))


async def _interfaces_async(json_output: bool) -> None:
    """List all network interfaces."""
    ctx = get_context()
    ctx.json_output = json_output
    adapter = get_adapter()

    try:
        interfaces = await adapter.get_interfaces()
    except Exception as e:
        ctx.error(f"Failed to get interfaces: {e}")
        raise typer.Exit(1) from None

    if not interfaces:
        ctx.warning("No network interfaces found.")
        return

    if ctx.json_output:
        ctx.output([iface.to_dict() for iface in interfaces])
    else:
        table = Table(title="Network Interfaces", show_header=True, header_style="bold")
        table.add_column("Name", style="cyan")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("IPv4 Address")
        table.add_column("MAC Address")
        table.add_column("Default", justify="center")

        for iface in interfaces:
            status_style = "green" if iface.status.value == "up" else "red"
            default_mark = "[green]✓[/green]" if iface.is_default else ""

            table.add_row(
                iface.name,
                iface.type.value,
                f"[{status_style}]{iface.status.value}[/{status_style}]",
                iface.ipv4_address or "-",
                iface.mac_address or "-",
                default_mark,
            )

        ctx.console.print(table)


@register_tool
def register(app: typer.Typer) -> None:
    """Register the interfaces command."""

    @app.command("interfaces")
    def interfaces(
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """List all network interfaces.

        Shows information about network interfaces including name, type,
        status, IP address, and MAC address.
        """
        _run_interfaces(json_output)
