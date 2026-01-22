"""Wi-Fi signal monitoring command."""

import asyncio
from typing import Annotated

import typer
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter

# Sparkline characters for signal visualization (from weakest to strongest)
SPARK_CHARS = "▁▂▃▄▅▆▇█"


def _rssi_to_quality(rssi: int) -> tuple[str, str]:
    """Convert RSSI to quality description and color."""
    if rssi >= -50:
        return "Excellent", "green"
    elif rssi >= -60:
        return "Good", "green"
    elif rssi >= -70:
        return "Fair", "yellow"
    elif rssi >= -80:
        return "Weak", "orange1"
    else:
        return "Poor", "red"


def _rssi_to_spark_index(rssi: int) -> int:
    """Convert RSSI to sparkline character index (0-7)."""
    # Map RSSI (-100 to -30) to index (0-7)
    # -30 dBm = excellent (index 7), -100 dBm = terrible (index 0)
    clamped = max(-100, min(-30, rssi))
    normalized = (clamped + 100) / 70  # 0.0 to 1.0
    return int(normalized * 7)


def _build_sparkline(samples: list[int], width: int = 20) -> str:
    """Build a sparkline string from RSSI samples."""
    if not samples:
        return ""

    # Take the last 'width' samples
    recent = samples[-width:]

    # Build sparkline
    chars = []
    for rssi in recent:
        idx = _rssi_to_spark_index(rssi)
        chars.append(SPARK_CHARS[idx])

    return "".join(chars)


def _run_wifi_signal(interval: float = 1.0, count: int | None = None) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_wifi_signal_async(interval, count))


async def _wifi_signal_async(interval: float, count: int | None) -> None:
    """Monitor Wi-Fi signal strength in real-time."""
    ctx = get_context()
    adapter = get_adapter()

    # Check if we have a Wi-Fi connection first
    wifi = await adapter.get_wifi_info()
    if wifi is None:
        ctx.error("Not connected to Wi-Fi.")
        raise typer.Exit(1) from None

    samples: list[int] = []
    iterations = 0

    ctx.console.print()
    ctx.console.print(f"[dim]Monitoring signal for [cyan]{wifi.ssid}[/cyan]... Press Ctrl+C to stop.[/dim]")
    ctx.console.print()

    try:
        with Live(console=ctx.console, refresh_per_second=4) as live:
            while True:
                # Get current Wi-Fi info
                wifi = await adapter.get_wifi_info()

                if wifi is None or wifi.rssi is None:
                    live.update(Panel("[red]Wi-Fi disconnected[/red]", border_style="red"))
                    await asyncio.sleep(interval)
                    continue

                samples.append(wifi.rssi)
                iterations += 1

                # Calculate stats
                quality, color = _rssi_to_quality(wifi.rssi)
                sparkline = _build_sparkline(samples)

                # Calculate average if we have samples
                avg_rssi = sum(samples[-20:]) / len(samples[-20:])
                min_rssi = min(samples[-20:]) if samples else wifi.rssi
                max_rssi = max(samples[-20:]) if samples else wifi.rssi

                # Build display
                text = Text()
                text.append("Signal: ", style="dim")
                text.append(sparkline, style=color)
                text.append(f"  {wifi.rssi} dBm ", style=f"bold {color}")
                text.append(f"({quality})", style=color)
                text.append("\n\n")
                text.append(f"SSID: {wifi.ssid}  ", style="dim")
                text.append(f"Channel: {wifi.channel or 'N/A'}  ", style="dim")
                text.append(f"Avg: {avg_rssi:.0f} dBm  ", style="dim")
                text.append(f"Range: {max_rssi}/{min_rssi} dBm", style="dim")

                panel = Panel(
                    text,
                    title="[bold]Wi-Fi Signal Monitor[/bold]",
                    border_style=color,
                )
                live.update(panel)

                # Check if we've reached the count limit
                if count is not None and iterations >= count:
                    break

                await asyncio.sleep(interval)

    except KeyboardInterrupt:
        pass

    # Print summary
    if samples:
        ctx.console.print()
        avg = sum(samples) / len(samples)
        quality, color = _rssi_to_quality(int(avg))
        ctx.console.print(
            f"[dim]Sampled {len(samples)} readings. "
            f"Average: [{color}]{avg:.1f} dBm ({quality})[/{color}][/dim]"
        )
        ctx.console.print()


def register(app: typer.Typer) -> None:
    """Register the wifi signal command."""

    @app.command("signal")
    def wifi_signal(
        interval: Annotated[
            float,
            typer.Option("--interval", "-i", help="Sampling interval in seconds."),
        ] = 1.0,
        count: Annotated[
            int | None,
            typer.Option("--count", "-c", help="Number of samples (default: infinite)."),
        ] = None,
    ) -> None:
        """Monitor Wi-Fi signal strength in real-time.

        Displays a live sparkline visualization of signal strength
        with quality indicators. Press Ctrl+C to stop.

        Example:
            lantern wifi signal
            lantern wifi signal --interval 0.5 --count 30
        """
        _run_wifi_signal(interval, count)
