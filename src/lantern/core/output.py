"""Output formatting utilities."""

from collections.abc import Sequence
from typing import Any

from rich.console import Console
from rich.table import Table


def print_table(
    console: Console,
    columns: Sequence[str],
    rows: Sequence[Sequence[Any]],
    title: str | None = None,
) -> None:
    """Print a formatted table.

    Args:
        console: Rich console to print to.
        columns: Column headers.
        rows: Table rows (each row is a sequence of cell values).
        title: Optional table title.
    """
    table = Table(title=title, show_header=True, header_style="bold")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)


def format_bytes(num_bytes: int) -> str:
    """Format bytes into human-readable string.

    Args:
        num_bytes: Number of bytes.

    Returns:
        Human-readable string like "1.5 MB".
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes //= 1024
    return f"{num_bytes:.1f} PB"


def format_latency(ms: float) -> str:
    """Format latency with color coding.

    Args:
        ms: Latency in milliseconds.

    Returns:
        Color-coded latency string (green < 20ms, yellow < 100ms, red >= 100ms).
    """
    if ms < 20:
        return f"[green]{ms:.1f}ms[/green]"
    elif ms < 100:
        return f"[yellow]{ms:.1f}ms[/yellow]"
    return f"[red]{ms:.1f}ms[/red]"


def format_status(online: bool) -> str:
    """Format online/offline status.

    Args:
        online: Whether the device is online.

    Returns:
        Color-coded status string.
    """
    return "[green]● Online[/green]" if online else "[red]○ Offline[/red]"


def format_signal_strength(rssi: int) -> str:
    """Format Wi-Fi signal strength with color coding.

    Args:
        rssi: Signal strength in dBm.

    Returns:
        Color-coded signal strength string.
    """
    if rssi >= -50:
        quality = "Excellent"
        color = "green"
    elif rssi >= -60:
        quality = "Good"
        color = "green"
    elif rssi >= -70:
        quality = "Fair"
        color = "yellow"
    else:
        quality = "Weak"
        color = "red"

    return f"[{color}]{rssi} dBm ({quality})[/{color}]"


def signal_bars(rssi: int, max_bars: int = 5) -> str:
    """Generate signal strength bars.

    Args:
        rssi: Signal strength in dBm.
        max_bars: Maximum number of bars to show.

    Returns:
        Signal bars string like "▂▄▆█░".
    """
    # Map RSSI to 0-100 quality
    quality = min(max(2 * (rssi + 100), 0), 100)
    filled = int((quality / 100) * max_bars)

    bars = ["▂", "▄", "▆", "█"]
    result = ""
    for i in range(max_bars):
        if i < filled:
            bar_idx = min(i, len(bars) - 1)
            result += f"[green]{bars[bar_idx]}[/green]"
        else:
            result += "[dim]░[/dim]"

    return result
