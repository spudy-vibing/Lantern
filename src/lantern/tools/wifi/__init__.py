"""Wi-Fi related commands."""

import typer

from lantern.tools import register_tool
from lantern.tools.wifi import info, scan, signal

wifi_app = typer.Typer(help="Wi-Fi information and management commands.")


@register_tool
def register(app: typer.Typer) -> None:
    """Register the Wi-Fi commands."""
    info.register(wifi_app)
    signal.register(wifi_app)
    scan.register(wifi_app)
    app.add_typer(wifi_app, name="wifi")
