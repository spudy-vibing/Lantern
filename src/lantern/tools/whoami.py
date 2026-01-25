"""Public IP and geolocation command."""

import asyncio
from typing import Annotated

import httpx
import typer
from rich.panel import Panel

from lantern.core.context import get_context
from lantern.tools import register_tool

# Free IP info APIs (no API key required)
IP_INFO_URL = "https://ipinfo.io/json"
IP_API_URL = "http://ip-api.com/json"


async def _fetch_ip_info() -> dict[str, str | None]:
    """Fetch public IP and geolocation info."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Try ipinfo.io first (HTTPS, more reliable)
        try:
            response = await client.get(IP_INFO_URL)
            if response.status_code == 200:
                data = response.json()
                return {
                    "ip": data.get("ip"),
                    "city": data.get("city"),
                    "region": data.get("region"),
                    "country": data.get("country"),
                    "location": data.get("loc"),  # lat,lon
                    "org": data.get("org"),
                    "timezone": data.get("timezone"),
                    "source": "ipinfo.io",
                }
        except (httpx.RequestError, httpx.HTTPStatusError):
            pass

        # Fallback to ip-api.com
        try:
            response = await client.get(IP_API_URL)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    lat = data.get("lat")
                    lon = data.get("lon")
                    location = f"{lat},{lon}" if lat and lon else None
                    return {
                        "ip": data.get("query"),
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "country": data.get("countryCode"),
                        "location": location,
                        "org": data.get("isp"),
                        "timezone": data.get("timezone"),
                        "source": "ip-api.com",
                    }
        except (httpx.RequestError, httpx.HTTPStatusError):
            pass

        return {}


def _run_whoami(json_output: bool = False, short: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_whoami_async(json_output, short))


async def _whoami_async(json_output: bool, short: bool) -> None:
    """Display public IP and geolocation."""
    ctx = get_context()
    ctx.json_output = json_output

    ctx.info("Fetching public IP info...")

    try:
        info = await _fetch_ip_info()
    except Exception as e:
        ctx.error(f"Failed to fetch IP info: {e}")
        raise typer.Exit(1) from None

    if not info or not info.get("ip"):
        ctx.error("Could not determine public IP address.")
        ctx.info("Check your internet connection.")
        raise typer.Exit(1)

    if json_output:
        ctx.output(info)
        return

    if short:
        ctx.console.print(info["ip"])
        return

    # Build nice display
    ip = info.get("ip", "Unknown")
    city = info.get("city", "")
    region = info.get("region", "")
    country = info.get("country", "")
    org = info.get("org", "")
    timezone = info.get("timezone", "")
    location = info.get("location", "")

    # Location string
    loc_parts = [p for p in [city, region, country] if p]
    location_str = ", ".join(loc_parts) if loc_parts else "Unknown"

    # Create panel
    content_lines = [
        f"[bold cyan]{ip}[/bold cyan]",
        "",
        f"[dim]Location:[/dim]  {location_str}",
    ]

    if org:
        content_lines.append(f"[dim]Provider:[/dim]  {org}")
    if timezone:
        content_lines.append(f"[dim]Timezone:[/dim]  {timezone}")
    if location:
        content_lines.append(f"[dim]Coords:[/dim]    {location}")

    panel = Panel(
        "\n".join(content_lines),
        title="[bold]Public IP[/bold]",
        border_style="green",
        padding=(1, 2),
    )
    ctx.console.print()
    ctx.console.print(panel)


@register_tool
def register(app: typer.Typer) -> None:
    """Register the whoami command."""

    @app.command("whoami")
    def whoami(
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
        short: Annotated[
            bool,
            typer.Option("--short", "-s", help="Output only the IP address."),
        ] = False,
    ) -> None:
        """Show your public IP address and location.

        Displays your public IP address along with geolocation
        information like city, country, and ISP.

        Examples:
            lantern whoami              # Full info with panel
            lantern whoami --short      # Just the IP address
            lantern whoami --json       # JSON output
        """
        _run_whoami(json_output, short)
