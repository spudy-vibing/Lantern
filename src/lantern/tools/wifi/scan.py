"""Wi-Fi network scanning command."""

import asyncio
from typing import Annotated

import typer
from rich.table import Table

from lantern.core.context import get_context
from lantern.core.output import format_signal_strength
from lantern.platforms.factory import get_adapter


def _run_wifi_scan(json_output: bool = False, do_scan: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_wifi_scan_async(json_output, do_scan))


async def _wifi_scan_async(json_output: bool, do_scan: bool) -> None:
    """Scan for available Wi-Fi networks."""
    ctx = get_context()
    ctx.json_output = json_output
    adapter = get_adapter()

    if not do_scan:
        if ctx.json_output:
            ctx.output({"error": "Use --scan flag to perform network scan"})
        else:
            ctx.warning(
                "Network scanning requires explicit permission.\n"
                "Use [cyan]lantern wifi scan --scan[/cyan] to scan for networks."
            )
        return

    ctx.info("Scanning for Wi-Fi networks...") if not ctx.json_output else None

    try:
        networks = await adapter.scan_wifi()
    except Exception as e:
        ctx.error(f"Failed to scan Wi-Fi networks: {e}")
        raise typer.Exit(1) from None

    if not networks:
        if ctx.json_output:
            ctx.output([])
        else:
            ctx.warning(
                "No networks found. This may be because:\n"
                "  • The airport command is not available (macOS Sequoia+)\n"
                "  • Wi-Fi is disabled\n"
                "  • No networks are in range"
            )
        return

    if ctx.json_output:
        ctx.output([n.to_dict() for n in networks])
        return

    # Sort by signal strength (strongest first)
    networks.sort(key=lambda n: n.rssi if n.rssi else -100, reverse=True)

    # Build rich output
    table = Table(title="Available Wi-Fi Networks", show_header=True, header_style="bold")
    table.add_column("", width=2)  # Current indicator
    table.add_column("SSID", style="cyan")
    table.add_column("Signal", justify="left")
    table.add_column("Channel", justify="center")
    table.add_column("Security")

    for network in networks:
        # Current network indicator
        indicator = "[green]●[/green]" if network.is_current else ""

        # SSID (handle hidden networks)
        ssid = network.ssid if network.ssid else "[dim](Hidden)[/dim]"
        if network.is_current:
            ssid = f"[bold]{ssid}[/bold]"

        # Signal strength
        signal = format_signal_strength(network.rssi) if network.rssi else "-"

        # Channel with band indication
        if network.channel:
            band = "5G" if network.channel > 14 else "2.4G"
            channel = f"{network.channel} ({band})"
        else:
            channel = "-"

        # Security
        security = network.security or "Open"

        table.add_row(indicator, ssid, signal, channel, security)

    ctx.console.print()
    ctx.console.print(table)
    ctx.console.print()
    ctx.console.print(f"[dim]Found {len(networks)} network(s)[/dim]")
    ctx.console.print()


def register(app: typer.Typer) -> None:
    """Register the wifi scan command."""

    @app.command("scan")
    def wifi_scan(
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
        do_scan: Annotated[
            bool,
            typer.Option("--scan", "-s", help="Perform network scan (required)."),
        ] = False,
    ) -> None:
        """Scan for available Wi-Fi networks.

        Lists nearby Wi-Fi networks with signal strength, channel,
        and security information.

        Note: Requires the --scan flag for explicit permission.
        On macOS Sequoia and later, this command may not work as
        the airport utility has been removed.

        Example:
            lantern wifi scan --scan
        """
        _run_wifi_scan(json_output, do_scan)
