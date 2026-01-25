"""Visual ping command with sparkline display."""

import asyncio
import time
from typing import Annotated

import typer
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.tools import register_tool

# Sparkline characters (8 levels)
SPARK_CHARS = " ▁▂▃▄▅▆▇█"


def _latency_to_spark(latency_ms: float | None, max_latency: float = 200.0) -> str:
    """Convert latency to sparkline character."""
    if latency_ms is None:
        return "×"  # Timeout/failure
    # Clamp and scale to 0-8
    normalized = min(latency_ms / max_latency, 1.0)
    index = int(normalized * (len(SPARK_CHARS) - 1))
    return SPARK_CHARS[index]


def _latency_color(latency_ms: float | None) -> str:
    """Get color for latency value."""
    if latency_ms is None:
        return "red"
    if latency_ms < 20:
        return "green"
    if latency_ms < 50:
        return "bright_green"
    if latency_ms < 100:
        return "yellow"
    if latency_ms < 200:
        return "orange1"
    return "red"


def _format_stats(samples: list[float | None]) -> str:
    """Format statistics from samples."""
    valid = [s for s in samples if s is not None]
    if not valid:
        return "[red]No successful pings[/red]"

    min_ms = min(valid)
    max_ms = max(valid)
    avg_ms = sum(valid) / len(valid)
    loss = (len(samples) - len(valid)) / len(samples) * 100

    parts = [
        f"[dim]min[/dim] [{_latency_color(min_ms)}]{min_ms:.1f}ms[/]",
        f"[dim]avg[/dim] [{_latency_color(avg_ms)}]{avg_ms:.1f}ms[/]",
        f"[dim]max[/dim] [{_latency_color(max_ms)}]{max_ms:.1f}ms[/]",
    ]

    if loss > 0:
        parts.append(f"[dim]loss[/dim] [red]{loss:.0f}%[/red]")

    return "  ".join(parts)


def _run_sonar(
    host: str,
    count: int | None = None,
    interval: float = 1.0,
) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_sonar_async(host, count, interval))


async def _sonar_async(
    host: str,
    count: int | None,
    interval: float,
) -> None:
    """Visual ping with sparkline display."""
    ctx = get_context()
    adapter = get_adapter()

    samples: list[float | None] = []
    max_samples = 60  # Keep last 60 samples for display
    ping_count = 0

    ctx.console.print(f"\n[bold]SONAR[/bold] {host}")
    ctx.console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    def build_display() -> Panel:
        """Build the display panel."""
        # Build sparkline
        display_samples = samples[-max_samples:]
        sparkline = "".join(_latency_to_spark(s) for s in display_samples)

        # Current latency
        current = samples[-1] if samples else None
        if current is not None:
            current_str = f"[{_latency_color(current)}]{current:.1f}ms[/]"
        else:
            current_str = "[red]timeout[/red]"

        # Build content
        content = Text()
        content.append(sparkline, style="cyan")
        content.append(f"  {current_str}\n\n")
        content.append(_format_stats(samples))

        return Panel(
            content,
            title=f"[bold]{host}[/bold]",
            subtitle=f"[dim]{ping_count} pings[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )

    try:
        with Live(build_display(), console=ctx.console, refresh_per_second=2) as live:
            while count is None or ping_count < count:
                start = time.monotonic()

                # Perform single ping
                result = await adapter.ping(host, count=1, timeout=2.0)

                if result.success and result.avg_ms is not None:
                    samples.append(result.avg_ms)
                else:
                    samples.append(None)

                ping_count += 1

                # Trim samples if too many
                if len(samples) > max_samples * 2:
                    samples[:] = samples[-max_samples:]

                # Update display
                live.update(build_display())

                # Wait for interval (accounting for ping time)
                elapsed = time.monotonic() - start
                if elapsed < interval:
                    await asyncio.sleep(interval - elapsed)

    except KeyboardInterrupt:
        pass

    # Final summary
    ctx.console.print()
    ctx.console.print(f"[bold]Summary:[/bold] {_format_stats(samples)}")
    ctx.console.print()


@register_tool
def register(app: typer.Typer) -> None:
    """Register the sonar command."""

    @app.command("sonar")
    def sonar(
        host: Annotated[
            str,
            typer.Argument(help="Host to ping."),
        ],
        count: Annotated[
            int | None,
            typer.Option("--count", "-c", help="Number of pings (default: unlimited)."),
        ] = None,
        interval: Annotated[
            float,
            typer.Option("--interval", "-i", help="Interval between pings in seconds."),
        ] = 1.0,
    ) -> None:
        """Visual ping with live sparkline display.

        Continuously pings a host and displays latency as a live
        sparkline graph. Great for monitoring connection quality.

        Examples:
            lantern sonar google.com           # Continuous ping
            lantern sonar 8.8.8.8 -c 30        # 30 pings then stop
            lantern sonar router -i 0.5        # Ping every 0.5 seconds
        """
        _run_sonar(host, count, interval)
