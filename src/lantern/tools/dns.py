"""DNS information and management commands."""

import asyncio
from typing import Annotated

import typer
from rich.table import Table

from lantern.core.context import get_context
from lantern.platforms.factory import get_adapter
from lantern.tools import register_tool

# Create a sub-app for DNS commands
dns_app = typer.Typer(help="DNS information and management commands.")


def _run_dns_info(json_output: bool = False) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_dns_info_async(json_output))


async def _dns_info_async(json_output: bool) -> None:
    """Show DNS configuration."""
    ctx = get_context()
    ctx.json_output = json_output
    adapter = get_adapter()

    try:
        dns = await adapter.get_dns_info()
    except Exception as e:
        ctx.error(f"Failed to get DNS info: {e}")
        raise typer.Exit(1) from None

    if ctx.json_output:
        ctx.output(dns.to_dict())
    else:
        # DNS Servers table
        if dns.servers:
            table = Table(title="DNS Servers", show_header=True, header_style="bold")
            table.add_column("Address", style="cyan")
            table.add_column("Interface")
            table.add_column("Default", justify="center")

            for server in dns.servers:
                default_mark = "[green]✓[/green]" if server.is_default else ""
                table.add_row(
                    server.address,
                    server.interface or "-",
                    default_mark,
                )

            ctx.console.print(table)
        else:
            ctx.warning("No DNS servers configured.")

        # Search domains
        if dns.search_domains:
            ctx.console.print()
            domains_str = ", ".join(dns.search_domains)
            ctx.console.print(f"[bold]Search Domains:[/bold] {domains_str}")


def _run_dns_flush() -> None:
    """Sync wrapper for async command."""
    asyncio.run(_dns_flush_async())


async def _dns_flush_async() -> None:
    """Flush DNS cache."""
    ctx = get_context()
    adapter = get_adapter()

    ctx.info("Flushing DNS cache...")

    try:
        success = await adapter.flush_dns_cache()
    except Exception as e:
        ctx.error(f"Failed to flush DNS cache: {e}")
        raise typer.Exit(1) from None

    if success:
        ctx.success("DNS cache flushed successfully.")
    else:
        ctx.error("Failed to flush DNS cache.")
        raise typer.Exit(1) from None


@dns_app.command("info")
def dns_info(
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Show DNS configuration.

    Displays configured DNS servers and search domains.
    """
    _run_dns_info(json_output)


@dns_app.command("flush")
def dns_flush() -> None:
    """Flush the DNS cache.

    Clears the local DNS resolver cache. This can help resolve
    DNS-related issues or force fresh lookups.
    """
    _run_dns_flush()


@register_tool
def register(app: typer.Typer) -> None:
    """Register the DNS commands."""
    app.add_typer(dns_app, name="dns")
