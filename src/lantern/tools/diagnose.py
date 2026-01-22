"""Network diagnostics command."""

import asyncio
from typing import Annotated, Any

import typer
from rich.panel import Panel
from rich.table import Table

from lantern.core.context import get_context
from lantern.core.output import format_latency, format_signal_strength
from lantern.platforms.factory import get_adapter
from lantern.tools import register_tool


def _run_diagnose(json_output: bool = False, quick: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_diagnose_async(json_output, quick))


async def _diagnose_async(json_output: bool, quick: bool) -> None:
    """Run comprehensive network diagnostics."""
    ctx = get_context()
    ctx.json_output = json_output
    adapter = get_adapter()

    results: dict[str, Any] = {
        "platform": adapter.name,
        "interfaces": [],
        "wifi": None,
        "router": None,
        "dns": None,
        "connectivity": None,
    }

    # Gather all info concurrently
    try:
        interfaces, wifi, router, dns = await asyncio.gather(
            adapter.get_interfaces(),
            adapter.get_wifi_info(),
            adapter.get_router_info(),
            adapter.get_dns_info(),
        )
    except Exception as e:
        ctx.error(f"Failed to gather network info: {e}")
        raise typer.Exit(1) from None

    results["interfaces"] = [i.to_dict() for i in interfaces]
    results["wifi"] = wifi.to_dict() if wifi else None
    results["router"] = router.to_dict() if router else None
    results["dns"] = dns.to_dict()

    # Run connectivity test unless quick mode
    if not quick:
        try:
            ping_result = await adapter.ping("8.8.8.8", count=3)
            results["connectivity"] = {
                "target": "8.8.8.8",
                "success": ping_result.success,
                "avg_ms": ping_result.avg_ms,
                "packet_loss": ping_result.packet_loss_percent,
            }
        except Exception:
            results["connectivity"] = {"target": "8.8.8.8", "success": False}

    if ctx.json_output:
        ctx.output(results)
        return

    # Build rich output
    panels = []

    # Network Interfaces
    iface_table = Table(show_header=True, header_style="bold", expand=True)
    iface_table.add_column("Interface", style="cyan")
    iface_table.add_column("Type")
    iface_table.add_column("IP Address")
    iface_table.add_column("Status")

    for iface in interfaces:
        if iface.ipv4_address or iface.is_default:
            status = "[green]●[/green]" if iface.status.value == "up" else "[red]○[/red]"
            name = f"[bold]{iface.name}[/bold]" if iface.is_default else iface.name
            iface_table.add_row(
                name,
                iface.type.value,
                iface.ipv4_address or "-",
                status,
            )

    panels.append(Panel(iface_table, title="[bold]Network Interfaces[/bold]", border_style="blue"))

    # Wi-Fi Info
    if wifi:
        wifi_table = Table(show_header=False, box=None, expand=True)
        wifi_table.add_column("Property", style="dim")
        wifi_table.add_column("Value")

        wifi_table.add_row("SSID", f"[cyan]{wifi.ssid}[/cyan]")
        if wifi.rssi:
            wifi_table.add_row("Signal", format_signal_strength(wifi.rssi))
        if wifi.channel:
            wifi_table.add_row("Channel", str(wifi.channel))
        if wifi.security:
            wifi_table.add_row("Security", wifi.security)
        if wifi.tx_rate:
            wifi_table.add_row("TX Rate", f"{wifi.tx_rate} Mbps")

        panels.append(Panel(wifi_table, title="[bold]Wi-Fi[/bold]", border_style="green"))

    # Router Info
    if router:
        router_table = Table(show_header=False, box=None, expand=True)
        router_table.add_column("Property", style="dim")
        router_table.add_column("Value")

        router_table.add_row("Gateway", f"[cyan]{router.ip_address}[/cyan]")
        router_table.add_row("Interface", router.interface)
        if router.mac_address:
            router_table.add_row("MAC", router.mac_address)

        panels.append(Panel(router_table, title="[bold]Router[/bold]", border_style="yellow"))

    # DNS Info
    if dns.servers:
        dns_servers = ", ".join(s.address for s in dns.servers[:3])
        if len(dns.servers) > 3:
            dns_servers += f" (+{len(dns.servers) - 3} more)"

        dns_table = Table(show_header=False, box=None, expand=True)
        dns_table.add_column("Property", style="dim")
        dns_table.add_column("Value")
        dns_table.add_row("Servers", dns_servers)
        if dns.search_domains:
            dns_table.add_row("Search", ", ".join(dns.search_domains[:2]))

        panels.append(Panel(dns_table, title="[bold]DNS[/bold]", border_style="magenta"))

    # Connectivity
    if results["connectivity"]:
        conn = results["connectivity"]
        if conn["success"]:
            latency = format_latency(conn["avg_ms"]) if conn.get("avg_ms") else "N/A"
            conn_status = f"[green]● Connected[/green]  Latency: {latency}"
        else:
            conn_status = "[red]○ No connectivity[/red]"

        panels.append(
            Panel(conn_status, title="[bold]Internet Connectivity[/bold]", border_style="cyan")
        )

    # Print all panels
    ctx.console.print()
    for panel in panels:
        ctx.console.print(panel)
        ctx.console.print()


@register_tool
def register(app: typer.Typer) -> None:
    """Register the diagnose command."""

    @app.command("diagnose")
    def diagnose(
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
        quick: Annotated[
            bool,
            typer.Option("--quick", "-q", help="Skip connectivity test."),
        ] = False,
    ) -> None:
        """Run comprehensive network diagnostics.

        Displays a summary of network interfaces, Wi-Fi connection,
        router info, DNS configuration, and internet connectivity.
        """
        _run_diagnose(json_output, quick)
