"""Smart plug control commands."""

import asyncio
from typing import Annotated

import typer
from rich.table import Table

from lantern.config import get_config_manager
from lantern.core.context import get_context
from lantern.tools import register_tool

plug_app = typer.Typer(help="Smart plug control (Kasa/TP-Link).")


def _check_kasa() -> None:
    """Check if python-kasa is available."""
    try:
        import kasa  # noqa: F401
    except ImportError:
        ctx = get_context()
        ctx.error("python-kasa is required for smart plug support.")
        ctx.info("Install with: pip install lantern-net[power]")
        raise typer.Exit(1) from None


def _resolve_target(target: str) -> str:
    """Resolve target (device name or IP) to IP address."""
    manager = get_config_manager()
    device = manager.get_device(target)
    if device and device.ip_address:
        return device.ip_address
    return target


@plug_app.command("discover")
def discover_plugs(
    timeout: Annotated[
        float,
        typer.Option("--timeout", "-t", help="Discovery timeout in seconds."),
    ] = 5.0,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Discover smart plugs on the network.

    Examples:
        lantern plug discover
        lantern plug discover --timeout 10
    """
    _check_kasa()
    ctx = get_context()
    ctx.json_output = json_output

    from lantern.services.smart_plugs.kasa import discover_devices

    async def run() -> None:
        if not json_output:
            ctx.info("Discovering smart plugs...")

        devices = await discover_devices(timeout=timeout)

        if json_output:
            ctx.output([d.to_dict() for d in devices])
            return

        if not devices:
            ctx.warning("No smart plugs found on the network.")
            return

        table = Table(
            title=f"Smart Plugs ({len(devices)} found)",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Name", style="cyan")
        table.add_column("Host")
        table.add_column("Model")
        table.add_column("State")
        table.add_column("Power")

        for device in sorted(devices, key=lambda d: d.name):
            state = "[green]ON[/green]" if device.is_on else "[dim]OFF[/dim]"
            power = f"{device.current_power:.1f}W" if device.current_power else "-"
            table.add_row(device.name, device.host, device.model, state, power)

        ctx.console.print()
        ctx.console.print(table)
        ctx.console.print()

    asyncio.run(run())


@plug_app.command("on")
def plug_on(
    target: Annotated[str, typer.Argument(help="Device name or IP address.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Turn on a smart plug.

    Examples:
        lantern plug on 192.168.1.50
        lantern plug on livingroom-lamp
    """
    _check_kasa()
    ctx = get_context()
    ctx.json_output = json_output

    from lantern.services.smart_plugs.kasa import turn_on

    host = _resolve_target(target)

    async def run() -> None:
        try:
            await turn_on(host)
            if json_output:
                ctx.output({"host": host, "state": "on", "success": True})
            else:
                ctx.success(f"Turned ON: {target}")
        except Exception as e:
            if json_output:
                ctx.output({"host": host, "success": False, "error": str(e)})
            else:
                ctx.error(f"Failed to turn on {target}: {e}")
            raise typer.Exit(1) from None

    asyncio.run(run())


@plug_app.command("off")
def plug_off(
    target: Annotated[str, typer.Argument(help="Device name or IP address.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Turn off a smart plug.

    Examples:
        lantern plug off 192.168.1.50
        lantern plug off livingroom-lamp
    """
    _check_kasa()
    ctx = get_context()
    ctx.json_output = json_output

    from lantern.services.smart_plugs.kasa import turn_off

    host = _resolve_target(target)

    async def run() -> None:
        try:
            await turn_off(host)
            if json_output:
                ctx.output({"host": host, "state": "off", "success": True})
            else:
                ctx.success(f"Turned OFF: {target}")
        except Exception as e:
            if json_output:
                ctx.output({"host": host, "success": False, "error": str(e)})
            else:
                ctx.error(f"Failed to turn off {target}: {e}")
            raise typer.Exit(1) from None

    asyncio.run(run())


@plug_app.command("toggle")
def plug_toggle(
    target: Annotated[str, typer.Argument(help="Device name or IP address.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Toggle a smart plug on/off.

    Examples:
        lantern plug toggle 192.168.1.50
        lantern plug toggle livingroom-lamp
    """
    _check_kasa()
    ctx = get_context()
    ctx.json_output = json_output

    from lantern.services.smart_plugs.kasa import toggle

    host = _resolve_target(target)

    async def run() -> None:
        try:
            new_state = await toggle(host)
            state_str = "on" if new_state else "off"
            if json_output:
                ctx.output({"host": host, "state": state_str, "success": True})
            else:
                state_display = "[green]ON[/green]" if new_state else "[dim]OFF[/dim]"
                ctx.success(f"Toggled {target}: {state_display}")
        except Exception as e:
            if json_output:
                ctx.output({"host": host, "success": False, "error": str(e)})
            else:
                ctx.error(f"Failed to toggle {target}: {e}")
            raise typer.Exit(1) from None

    asyncio.run(run())


@plug_app.command("status")
def plug_status(
    target: Annotated[str, typer.Argument(help="Device name or IP address.")],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """Show status and power usage of a smart plug.

    Examples:
        lantern plug status 192.168.1.50
        lantern plug status livingroom-lamp
    """
    _check_kasa()
    ctx = get_context()
    ctx.json_output = json_output

    from lantern.services.smart_plugs.kasa import get_device

    host = _resolve_target(target)

    async def run() -> None:
        try:
            device = await get_device(host)

            power = None
            energy = None
            if device.has_emeter:
                emeter = device.emeter_realtime
                if emeter:
                    power = emeter.get("power")
                energy = device.emeter_today

            if json_output:
                ctx.output({
                    "host": host,
                    "name": device.alias,
                    "model": device.model,
                    "is_on": device.is_on,
                    "has_emeter": device.has_emeter,
                    "current_power": power,
                    "today_energy": energy,
                })
                return

            from rich.panel import Panel

            state = "[green]ON[/green]" if device.is_on else "[dim]OFF[/dim]"
            lines = [
                f"[bold]{device.alias or host}[/bold]",
                f"Model: {device.model}",
                f"State: {state}",
            ]

            if device.has_emeter:
                if power is not None:
                    lines.append(f"Power: [cyan]{power:.1f}W[/cyan]")
                if energy is not None:
                    lines.append(f"Today: [cyan]{energy:.2f} kWh[/cyan]")
            else:
                lines.append("[dim]No energy monitoring[/dim]")

            ctx.console.print()
            ctx.console.print(Panel("\n".join(lines), title="Smart Plug"))
            ctx.console.print()

        except Exception as e:
            if json_output:
                ctx.output({"host": host, "success": False, "error": str(e)})
            else:
                ctx.error(f"Failed to get status for {target}: {e}")
            raise typer.Exit(1) from None

    asyncio.run(run())


@register_tool
def register(app: typer.Typer) -> None:
    """Register the plug command group."""
    app.add_typer(plug_app, name="plug")
