"""Router/gateway information command."""

import asyncio
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.tools import register_tool

# Create a sub-app for router commands
router_app = typer.Typer(help="Router and gateway commands.")


def _run_router_info(json_output: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_router_info_async(json_output))


async def _router_info_async(json_output: bool) -> None:
    """Show router/gateway information."""
    ctx = get_context()
    ctx.json_output = json_output
    adapter = get_adapter()

    try:
        router = await adapter.get_router_info()
    except Exception as e:
        ctx.error(f"Failed to get router info: {e}")
        raise typer.Exit(1) from None

    if not router:
        ctx.warning("No default gateway found.")
        return

    if ctx.json_output:
        ctx.output(router.to_dict())
    else:
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Property", style="dim")
        table.add_column("Value", style="cyan")

        table.add_row("IP Address", router.ip_address)
        table.add_row("Interface", router.interface)
        if router.mac_address:
            table.add_row("MAC Address", router.mac_address)
        if router.hostname:
            table.add_row("Hostname", router.hostname)

        panel = Panel(table, title="[bold]Default Gateway[/bold]", border_style="blue")
        ctx.console.print(panel)


@router_app.command("info")
def router_info(
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Show default gateway/router information.

    Displays the IP address, interface, and MAC address of the default gateway.
    """
    _run_router_info(json_output)


@register_tool
def register(app: typer.Typer) -> None:
    """Register the router commands."""
    app.add_typer(router_app, name="router")
