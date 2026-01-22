"""Wi-Fi info command."""

import asyncio
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from lantern.core.context import get_context
from lantern.core.output import format_signal_strength
from lantern.platforms.factory import get_adapter


def _run_wifi_info(json_output: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_wifi_info_async(json_output))


async def _wifi_info_async(json_output: bool) -> None:
    """Show current Wi-Fi connection info."""
    ctx = get_context()
    ctx.json_output = json_output
    adapter = get_adapter()

    try:
        wifi = await adapter.get_wifi_info()
    except Exception as e:
        ctx.error(f"Failed to get Wi-Fi info: {e}")
        raise typer.Exit(1) from None

    if wifi is None:
        if ctx.json_output:
            ctx.output({"connected": False})
        else:
            ctx.warning("Not connected to Wi-Fi.")
        return

    if ctx.json_output:
        ctx.output({"connected": True, **wifi.to_dict()})
        return

    # Build rich output
    table = Table(show_header=False, box=None, expand=True, padding=(0, 2))
    table.add_column("Property", style="dim")
    table.add_column("Value")

    table.add_row("SSID", f"[bold cyan]{wifi.ssid}[/bold cyan]")

    if wifi.bssid:
        table.add_row("BSSID", wifi.bssid)

    if wifi.rssi is not None:
        table.add_row("Signal", format_signal_strength(wifi.rssi))

    if wifi.noise is not None:
        snr = wifi.rssi - wifi.noise if wifi.rssi else None
        noise_str = f"{wifi.noise} dBm"
        if snr:
            noise_str += f" (SNR: {snr} dB)"
        table.add_row("Noise", noise_str)

    if wifi.channel is not None:
        # Determine band based on channel
        band = "5 GHz" if wifi.channel > 14 else "2.4 GHz"
        table.add_row("Channel", f"{wifi.channel} ({band})")

    if wifi.tx_rate is not None:
        table.add_row("TX Rate", f"{wifi.tx_rate} Mbps")

    if wifi.security:
        table.add_row("Security", wifi.security)

    if wifi.interface:
        table.add_row("Interface", wifi.interface)

    panel = Panel(
        table,
        title="[bold]Wi-Fi Connection[/bold]",
        border_style="green",
    )
    ctx.console.print()
    ctx.console.print(panel)
    ctx.console.print()


def register(app: typer.Typer) -> None:
    """Register the wifi info command."""

    @app.command("info")
    def wifi_info(
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Show current Wi-Fi connection details.

        Displays SSID, signal strength, channel, security type,
        and other connection information.
        """
        _run_wifi_info(json_output)
