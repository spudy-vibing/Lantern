"""Device control commands.

Provides unified interface to discover and control networked devices
like TVs, speakers, lights, and more.
"""

import asyncio
from typing import Annotated

import typer
from rich.table import Table

from lantern.core.context import get_context
from lantern.services.control.base import ControllableDevice
from lantern.services.control.discovery import DeviceDiscovery
from lantern.tools import register_tool

# Cache of discovered devices
_device_cache: dict[str, ControllableDevice] = {}


def _run_async(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


async def _discover_devices(timeout: float = 5.0) -> list[ControllableDevice]:
    """Discover and cache devices."""
    global _device_cache

    discovery = DeviceDiscovery(timeout=timeout)
    devices = await discovery.discover_and_create_devices()

    # Cache by name (lowercase, normalized)
    _device_cache.clear()
    for device in devices:
        key = device.name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        # Also add by IP for direct access
        _device_cache[key] = device
        _device_cache[device.ip_address] = device

    return devices


def _get_device(name_or_ip: str) -> ControllableDevice | None:
    """Get a device from cache by name or IP."""
    key = name_or_ip.lower().replace(" ", "-")
    return _device_cache.get(key) or _device_cache.get(name_or_ip)


def _get_or_discover_device(name_or_ip: str) -> ControllableDevice | None:
    """Get a device from cache, or discover it by IP if it looks like an IP address."""
    # First check cache
    device = _get_device(name_or_ip)
    if device:
        return device

    # If it looks like an IP address, try to discover it directly
    import re
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    if re.match(ip_pattern, name_or_ip):
        # Try to discover this specific device
        from lantern.services.control.discovery import DeviceDiscovery

        async def discover_single():
            discovery = DeviceDiscovery(timeout=3.0)
            devices = await discovery.discover_and_create_devices()
            for d in devices:
                if d.ip_address == name_or_ip:
                    return d
            return None

        device = _run_async(discover_single())
        if device:
            # Cache it for subsequent calls
            _device_cache[device.ip_address] = device
            key = device.name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            _device_cache[key] = device
        return device

    return None


@register_tool
def register(app: typer.Typer) -> None:
    """Register control commands."""

    control_app = typer.Typer(help="Control networked devices (TVs, speakers, etc.)")
    app.add_typer(control_app, name="control")

    @control_app.command("discover")
    def discover(
        timeout: Annotated[
            float,
            typer.Option("--timeout", "-t", help="Discovery timeout in seconds."),
        ] = 5.0,
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Discover controllable devices on the network.

        Scans for UPnP/DLNA devices, Roku players, and other controllable
        devices. Discovered devices can then be controlled with other
        control commands.

        Examples:
            lantern control discover
            lantern control discover --timeout 10
            lantern control discover --json
        """
        ctx = get_context()
        ctx.json_output = json_output

        if not json_output:
            ctx.info(f"Discovering devices (timeout: {timeout}s)...")

        devices = _run_async(_discover_devices(timeout))

        if json_output:
            ctx.output([d.to_dict() for d in devices])
            return

        if not devices:
            ctx.warning("No controllable devices found.")
            ctx.info("Try increasing the timeout: lantern control discover --timeout 10")
            return

        table = Table(title=f"Controllable Devices ({len(devices)} found)")
        table.add_column("Name", style="cyan")
        table.add_column("Type")
        table.add_column("IP Address")
        table.add_column("Manufacturer")
        table.add_column("Capabilities")

        for device in devices:
            caps = ", ".join(c.name for c in device.capabilities[:4])
            if len(device.capabilities) > 4:
                caps += f" (+{len(device.capabilities) - 4})"

            table.add_row(
                device.name,
                device.device_type,
                device.ip_address,
                device.manufacturer or "-",
                caps or "-",
            )

        ctx.console.print()
        ctx.console.print(table)
        ctx.console.print()
        ctx.info("Use 'lantern control <device> commands' to see available commands")

    @control_app.command("list")
    def list_devices(
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """List previously discovered devices.

        Shows devices from the last discovery. Run 'discover' first to
        find devices on the network.

        Examples:
            lantern control list
            lantern control list --json
        """
        ctx = get_context()
        ctx.json_output = json_output

        if not _device_cache:
            ctx.warning("No devices in cache. Run 'lantern control discover' first.")
            return

        # Filter to unique devices (by device_id)
        seen = set()
        devices = []
        for device in _device_cache.values():
            if device.device_id not in seen:
                seen.add(device.device_id)
                devices.append(device)

        if json_output:
            ctx.output([d.to_dict() for d in devices])
            return

        table = Table(title=f"Cached Devices ({len(devices)})")
        table.add_column("Name", style="cyan")
        table.add_column("Type")
        table.add_column("IP Address")
        table.add_column("Manufacturer")

        for device in devices:
            table.add_row(
                device.name,
                device.device_type,
                device.ip_address,
                device.manufacturer or "-",
            )

        ctx.console.print()
        ctx.console.print(table)
        ctx.console.print()

    @control_app.command("info")
    def device_info(
        device: Annotated[
            list[str],
            typer.Argument(help="Device name or IP address."),
        ],
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Show detailed information about a device.

        Examples:
            lantern control info Family Room
            lantern control info 192.168.1.167
        """
        ctx = get_context()
        ctx.json_output = json_output

        device_name = " ".join(device)
        dev = _get_or_discover_device(device_name)
        if not dev:
            ctx.error(f"Device not found: {device_name}")
            ctx.info("Run 'lantern control discover' to find devices.")
            raise typer.Exit(1)

        if json_output:
            ctx.output(dev.to_dict())
            return

        ctx.console.print()
        ctx.console.print(f"[bold cyan]{dev.name}[/bold cyan]")
        ctx.console.print(f"  Type: {dev.device_type}")
        ctx.console.print(f"  IP: {dev.ip_address}")
        if dev.manufacturer:
            ctx.console.print(f"  Manufacturer: {dev.manufacturer}")
        if dev.model:
            ctx.console.print(f"  Model: {dev.model}")

        if dev.capabilities:
            ctx.console.print()
            ctx.console.print("[bold]Capabilities:[/bold]")
            for cap in dev.capabilities:
                actions = ", ".join(cap.actions)
                ctx.console.print(f"  [cyan]{cap.name}[/cyan]: {cap.description}")
                ctx.console.print(f"    Actions: {actions}")

        ctx.console.print()

    @control_app.command("commands")
    def list_commands(
        device: Annotated[
            list[str],
            typer.Argument(help="Device name or IP address."),
        ],
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """List all available commands for a device.

        Examples:
            lantern control commands Family Room
            lantern control commands Family Room --json
        """
        ctx = get_context()
        ctx.json_output = json_output

        device_name = " ".join(device)
        dev = _get_or_discover_device(device_name)
        if not dev:
            ctx.error(f"Device not found: {device_name}")
            ctx.info("Run 'lantern control discover' to find devices.")
            raise typer.Exit(1)

        commands = dev.get_all_commands()

        if json_output:
            ctx.output(commands)
            return

        ctx.console.print()
        ctx.console.print(f"[bold]Commands for {dev.name}[/bold]")
        ctx.console.print()

        # Group by category
        by_category: dict[str, list] = {}
        for cmd in commands:
            cat = cmd["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(cmd)

        for category, cmds in by_category.items():
            ctx.console.print(f"[bold cyan]{category.title()}[/bold cyan]")
            for cmd in cmds:
                params = ""
                if cmd["parameters"]:
                    param_strs = []
                    for p in cmd["parameters"]:
                        if p["required"]:
                            param_strs.append(f"<{p['name']}>")
                        else:
                            param_strs.append(f"[{p['name']}]")
                    params = " " + " ".join(param_strs)

                ctx.console.print(f"  [green]{cmd['command']}[/green]{params}")
                ctx.console.print(f"    {cmd['description']}")
            ctx.console.print()

    @control_app.command("run")
    def run_command(
        device: Annotated[
            str,
            typer.Argument(help="Device name or IP address."),
        ],
        command: Annotated[
            str,
            typer.Argument(help="Command to run (capability.action format)."),
        ],
        args: Annotated[
            list[str] | None,
            typer.Argument(help="Command arguments (key=value format)."),
        ] = None,
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Execute a command on a device.

        Commands are in the format capability.action, e.g. volume.set or power.on.

        Examples:
            lantern control run "Family Room" volume.get
            lantern control run "Family Room" volume.set level=50
            lantern control run "Family Room" power.on
            lantern control run "Roku" app.launch name=netflix
        """
        ctx = get_context()
        ctx.json_output = json_output

        dev = _get_or_discover_device(device)
        if not dev:
            ctx.error(f"Device not found: {device}")
            ctx.info("Run 'lantern control discover' to find devices.")
            raise typer.Exit(1)

        # Parse command
        if "." not in command:
            ctx.error(f"Invalid command format: {command}")
            ctx.info("Use capability.action format, e.g. volume.set")
            raise typer.Exit(1)

        capability, action = command.split(".", 1)

        # Parse arguments
        kwargs = {}
        if args:
            for arg in args:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    # Try to convert to appropriate type
                    try:
                        kwargs[key] = int(value)
                    except ValueError:
                        try:
                            kwargs[key] = float(value)
                        except ValueError:
                            if value.lower() in ("true", "false"):
                                kwargs[key] = value.lower() == "true"
                            else:
                                kwargs[key] = value

        # Execute command
        async def execute():
            return await dev.execute(capability, action, **kwargs)

        result = _run_async(execute())

        if json_output:
            ctx.output(result.to_dict())
            return

        if result.success:
            if result.value is not None:
                if isinstance(result.value, dict):
                    for k, v in result.value.items():
                        ctx.console.print(f"  {k}: {v}")
                else:
                    ctx.success(f"{capability}.{action} = {result.value}")
            else:
                ctx.success(f"{capability}.{action}: OK")
        else:
            ctx.error(f"Command failed: {result.error}")
            raise typer.Exit(1)

    @control_app.command("status")
    def device_status(
        device: Annotated[
            list[str],
            typer.Argument(help="Device name or IP address."),
        ],
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Get current status of a device.

        Queries the device for its current state (volume, power, etc.).

        Examples:
            lantern control status Family Room
            lantern control status Family Room --json
        """
        ctx = get_context()
        ctx.json_output = json_output

        device_name = " ".join(device)
        dev = _get_or_discover_device(device_name)
        if not dev:
            ctx.error(f"Device not found: {device_name}")
            ctx.info("Run 'lantern control discover' to find devices.")
            raise typer.Exit(1)

        async def refresh():
            return await dev.refresh_state()

        state = _run_async(refresh())

        if json_output:
            ctx.output(state.to_dict())
            return

        ctx.console.print()
        ctx.console.print(f"[bold cyan]{dev.name}[/bold cyan]")
        status = "[green]online[/green]" if state.is_online else "[red]offline[/red]"
        ctx.console.print(f"  Status: {status}")

        if state.values:
            ctx.console.print()
            ctx.console.print("[bold]Current State:[/bold]")
            for key, value in state.values.items():
                ctx.console.print(f"  {key}: {value}")

        ctx.console.print()

    # Shortcut commands for common operations

    @control_app.command("volume")
    def volume(
        device: Annotated[
            str,
            typer.Option("--device", "-d", help="Device name or IP address."),
        ],
        action: Annotated[
            str,
            typer.Argument(help="Action: get, set, up, down, mute, unmute."),
        ] = "get",
        level: Annotated[
            int | None,
            typer.Argument(help="Volume level (0-100) for 'set' action."),
        ] = None,
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Control device volume.

        Examples:
            lantern control volume -d "Family Room"
            lantern control volume -d "Family Room" set 50
            lantern control volume -d "Family Room" up
            lantern control volume -d "Family Room" mute
        """
        ctx = get_context()
        ctx.json_output = json_output

        dev = _get_or_discover_device(device)
        if not dev:
            ctx.error(f"Device not found: {device}")
            raise typer.Exit(1)

        kwargs = {}
        if level is not None:
            kwargs["level"] = level

        async def execute():
            return await dev.execute("volume", action, **kwargs)

        result = _run_async(execute())

        if json_output:
            ctx.output(result.to_dict())
            return

        if result.success:
            if result.value is not None:
                ctx.success(f"Volume: {result.value}")
            else:
                ctx.success(f"Volume {action}: OK")
        else:
            ctx.error(f"Volume control failed: {result.error}")
            raise typer.Exit(1)

    @control_app.command("power")
    def power(
        device: Annotated[
            str,
            typer.Option("--device", "-d", help="Device name or IP address."),
        ],
        action: Annotated[
            str,
            typer.Argument(help="Action: get, on, off, toggle."),
        ] = "get",
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Control device power.

        Examples:
            lantern control power -d "Roku TV"
            lantern control power -d "Roku TV" on
            lantern control power -d "Roku TV" off
        """
        ctx = get_context()
        ctx.json_output = json_output

        dev = _get_or_discover_device(device)
        if not dev:
            ctx.error(f"Device not found: {device}")
            raise typer.Exit(1)

        async def execute():
            return await dev.execute("power", action)

        result = _run_async(execute())

        if json_output:
            ctx.output(result.to_dict())
            return

        if result.success:
            if result.value is not None:
                ctx.success(f"Power: {result.value}")
            else:
                ctx.success(f"Power {action}: OK")
        else:
            ctx.error(f"Power control failed: {result.error}")
            raise typer.Exit(1)
