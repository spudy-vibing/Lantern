"""Wi-Fi network sharing command."""

import asyncio
from typing import Annotated

import typer
from rich.panel import Panel

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.services.qr import generate_qr_unicode, generate_wifi_qr_data
from lantern.tools import register_tool


def _run_share(
    ssid: str | None = None,
    password: str | None = None,
    invert: bool = False,
    show_password: bool = False,
) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_share_async(ssid, password, invert, show_password))


async def _share_async(
    ssid: str | None,
    password: str | None,
    invert: bool,
    show_password: bool,
) -> None:
    """Generate Wi-Fi QR code for sharing."""
    ctx = get_context()
    adapter = get_adapter()

    # Get current Wi-Fi info if SSID not provided
    if ssid is None:
        wifi_info = await adapter.get_wifi_info()
        if wifi_info is None:
            ctx.error("Not connected to Wi-Fi. Please provide --ssid.")
            raise typer.Exit(1)
        ssid = wifi_info.ssid
        security = wifi_info.security or "WPA"
    else:
        security = "WPA"  # Default assumption

    ctx.info(f"Sharing Wi-Fi network: [bold]{ssid}[/bold]")

    # Get password if not provided
    if password is None:
        ctx.info("Retrieving password from Keychain...")
        password = await adapter.get_wifi_password(ssid)

        if password is None:
            ctx.warning(
                "Could not retrieve password from Keychain.\n"
                "  The password for this network may not be saved in Keychain.\n"
                "  Try: sudo lantern share (requires admin)\n"
                "  Or:  lantern share --password \"your-password\""
            )
            # Still generate QR without password for open networks
            security = "nopass"

    # Generate Wi-Fi QR data
    wifi_data = generate_wifi_qr_data(
        ssid=ssid,
        password=password,
        security=security,
    )

    # Generate QR code
    try:
        qr_art = generate_qr_unicode(wifi_data, border=1, invert=invert)
    except Exception as e:
        ctx.error(f"Failed to generate QR code: {e}")
        raise typer.Exit(1) from None

    # Build subtitle
    if show_password and password:
        subtitle = f"[dim]Password: {password}[/dim]"
    elif password:
        subtitle = "[dim]Password hidden (use --show-password to reveal)[/dim]"
    else:
        subtitle = "[dim]Open network (no password)[/dim]"

    # Display with panel
    panel = Panel(
        qr_art,
        title=f"[bold]Wi-Fi: {ssid}[/bold]",
        subtitle=subtitle,
        border_style="green",
        padding=(1, 2),
    )
    ctx.console.print(panel)
    ctx.console.print("\n[dim]Scan this QR code with your phone's camera to connect.[/dim]")


@register_tool
def register(app: typer.Typer) -> None:
    """Register the share command."""

    @app.command("share")
    def share(
        ssid: Annotated[
            str | None,
            typer.Option("--ssid", "-s", help="Wi-Fi network name (defaults to current)."),
        ] = None,
        password: Annotated[
            str | None,
            typer.Option("--password", "-p", help="Wi-Fi password (retrieved from Keychain if not provided)."),
        ] = None,
        invert: Annotated[
            bool,
            typer.Option("--invert", "-i", help="Invert colors (white on black)."),
        ] = False,
        show_password: Annotated[
            bool,
            typer.Option("--show-password", help="Show password in output."),
        ] = False,
    ) -> None:
        """Share Wi-Fi network via QR code.

        Generates a QR code that can be scanned to connect to a Wi-Fi network.
        By default, uses the current network and retrieves the password from
        the system Keychain.

        Examples:
            lantern share                     # Share current network
            lantern share --show-password     # Show password below QR
            lantern share -s "MyNetwork"      # Share specific network
            lantern share -s "Guest" -p "..."  # Share with explicit password
        """
        _run_share(ssid, password, invert, show_password)
