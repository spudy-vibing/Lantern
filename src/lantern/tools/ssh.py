"""SSH connection commands."""

import os
import subprocess
from typing import Annotated

import typer
from rich.table import Table

from lantern.config import get_config_manager
from lantern.core.context import get_context
from lantern.tools import register_tool

ssh_app = typer.Typer(help="SSH connection tools.")


def _build_ssh_command(
    host: str,
    user: str | None = None,
    port: int = 22,
    key: str | None = None,
    extra_args: list[str] | None = None,
) -> list[str]:
    """Build SSH command arguments."""
    cmd = ["ssh"]

    if port != 22:
        cmd.extend(["-p", str(port)])

    if key:
        cmd.extend(["-i", os.path.expanduser(key)])

    if user:
        cmd.append(f"{user}@{host}")
    else:
        cmd.append(host)

    if extra_args:
        cmd.extend(extra_args)

    return cmd


@ssh_app.command("list")
def list_ssh_devices(
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output in JSON format."),
    ] = False,
) -> None:
    """List devices with SSH configuration.

    Shows all saved devices that have SSH settings configured.

    Examples:
        lantern ssh list
        lantern ssh list --json
    """
    ctx = get_context()
    ctx.json_output = json_output
    manager = get_config_manager()

    devices = [d for d in manager.list_devices() if d.ssh_user or d.ip_address or d.hostname]

    if json_output:
        ctx.output([
            {
                "name": d.name,
                "host": d.ip_address or d.hostname,
                "user": d.ssh_user,
                "port": d.ssh_port,
                "key": d.ssh_key,
            }
            for d in devices
        ])
        return

    if not devices:
        ctx.info("No devices with SSH configuration found.")
        ctx.info("Add one with: lantern devices add myserver --ip 192.168.1.100 --ssh-user admin")
        return

    table = Table(title="SSH Devices", show_header=True, header_style="bold")
    table.add_column("Name", style="cyan")
    table.add_column("Host")
    table.add_column("User")
    table.add_column("Port")
    table.add_column("Key")

    for device in sorted(devices, key=lambda d: d.name):
        host = device.ip_address or device.hostname or "-"
        table.add_row(
            device.name,
            host,
            device.ssh_user or "[dim]-[/dim]",
            str(device.ssh_port) if device.ssh_port != 22 else "[dim]22[/dim]",
            device.ssh_key or "[dim]-[/dim]",
        )

    ctx.console.print()
    ctx.console.print(table)
    ctx.console.print()
    ctx.console.print("[dim]Connect with: lantern ssh connect <name>[/dim]")


@ssh_app.command("connect")
def ssh_connect(
    target: Annotated[str, typer.Argument(help="Device name or host.")],
    user: Annotated[
        str | None,
        typer.Option("--user", "-u", help="Override SSH username."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option("--port", "-p", help="Override SSH port."),
    ] = None,
    key: Annotated[
        str | None,
        typer.Option("--key", "-i", help="Path to SSH private key."),
    ] = None,
    command: Annotated[
        str | None,
        typer.Option("--command", "-c", help="Command to run remotely."),
    ] = None,
) -> None:
    """Connect to a device via SSH.

    Target can be a saved device name or a direct host.

    Examples:
        lantern ssh connect myserver
        lantern ssh connect myserver --user root
        lantern ssh connect 192.168.1.100 --user admin
        lantern ssh connect myserver -c "uptime"
    """
    ctx = get_context()
    manager = get_config_manager()

    # Resolve target
    device = manager.get_device(target)

    if device:
        host = device.ip_address or device.hostname
        ssh_user = user or device.ssh_user
        ssh_port = port or device.ssh_port
        ssh_key = key or device.ssh_key

        if not host:
            ctx.error(f"Device '{target}' has no IP address or hostname configured.")
            raise typer.Exit(1)
    else:
        # Direct host
        host = target
        ssh_user = user
        ssh_port = port or 22
        ssh_key = key

    # Build SSH command
    extra_args = [command] if command else None
    ssh_cmd = _build_ssh_command(
        host=host,
        user=ssh_user,
        port=ssh_port,
        key=ssh_key,
        extra_args=extra_args,
    )

    # Display connection info
    user_display = f"{ssh_user}@" if ssh_user else ""
    port_display = f":{ssh_port}" if ssh_port != 22 else ""
    ctx.info(f"Connecting to {user_display}{host}{port_display}...")

    # Execute SSH (replace current process)
    if command:
        # Run command and return
        result = subprocess.run(ssh_cmd)
        raise typer.Exit(result.returncode)
    else:
        # Interactive session - replace process
        os.execvp("ssh", ssh_cmd)


@ssh_app.command("copy-id")
def ssh_copy_id(
    target: Annotated[str, typer.Argument(help="Device name or host.")],
    user: Annotated[
        str | None,
        typer.Option("--user", "-u", help="Override SSH username."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option("--port", "-p", help="Override SSH port."),
    ] = None,
    key: Annotated[
        str | None,
        typer.Option("--key", "-i", help="Path to public key to copy."),
    ] = None,
) -> None:
    """Copy SSH public key to a device for passwordless auth.

    Examples:
        lantern ssh copy-id myserver
        lantern ssh copy-id myserver --key ~/.ssh/id_ed25519.pub
    """
    ctx = get_context()
    manager = get_config_manager()

    # Resolve target
    device = manager.get_device(target)

    if device:
        host = device.ip_address or device.hostname
        ssh_user = user or device.ssh_user
        ssh_port = port or device.ssh_port

        if not host:
            ctx.error(f"Device '{target}' has no IP address or hostname configured.")
            raise typer.Exit(1)
    else:
        host = target
        ssh_user = user
        ssh_port = port or 22

    # Build ssh-copy-id command
    cmd = ["ssh-copy-id"]

    if ssh_port != 22:
        cmd.extend(["-p", str(ssh_port)])

    if key:
        cmd.extend(["-i", os.path.expanduser(key)])

    if ssh_user:
        cmd.append(f"{ssh_user}@{host}")
    else:
        cmd.append(host)

    ctx.info(f"Copying SSH key to {host}...")
    result = subprocess.run(cmd)
    raise typer.Exit(result.returncode)


@ssh_app.command("tunnel")
def ssh_tunnel(
    target: Annotated[str, typer.Argument(help="Device name or host.")],
    mapping: Annotated[
        str,
        typer.Argument(help="Port mapping: local:remote or local:host:remote"),
    ],
    user: Annotated[
        str | None,
        typer.Option("--user", "-u", help="Override SSH username."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option("--port", "-p", help="Override SSH port."),
    ] = None,
    key: Annotated[
        str | None,
        typer.Option("--key", "-i", help="Path to SSH private key."),
    ] = None,
    reverse: Annotated[
        bool,
        typer.Option("--reverse", "-R", help="Create reverse tunnel."),
    ] = False,
    background: Annotated[
        bool,
        typer.Option("--background", "-b", help="Run in background."),
    ] = False,
) -> None:
    """Create an SSH tunnel for port forwarding.

    Mapping format:
        local:remote     - Forward local port to remote localhost:port
        local:host:port  - Forward local port to remote host:port

    Examples:
        lantern ssh tunnel myserver 8080:80
        lantern ssh tunnel myserver 3306:localhost:3306
        lantern ssh tunnel myserver 8080:internal.host:80
        lantern ssh tunnel myserver 8080:80 --reverse
        lantern ssh tunnel myserver 8080:80 --background
    """
    ctx = get_context()
    manager = get_config_manager()

    # Resolve target
    device = manager.get_device(target)

    if device:
        host = device.ip_address or device.hostname
        ssh_user = user or device.ssh_user
        ssh_port = port or device.ssh_port
        ssh_key = key or device.ssh_key

        if not host:
            ctx.error(f"Device '{target}' has no IP address or hostname configured.")
            raise typer.Exit(1)
    else:
        host = target
        ssh_user = user
        ssh_port = port or 22
        ssh_key = key

    # Parse mapping
    parts = mapping.split(":")
    if len(parts) == 2:
        local_port = parts[0]
        remote_host = "localhost"
        remote_port = parts[1]
    elif len(parts) == 3:
        local_port = parts[0]
        remote_host = parts[1]
        remote_port = parts[2]
    else:
        ctx.error("Invalid mapping format. Use local:remote or local:host:remote")
        raise typer.Exit(1)

    # Build SSH command
    cmd = ["ssh", "-N"]  # -N = no remote command

    if background:
        cmd.append("-f")  # -f = go to background

    if reverse:
        cmd.extend(["-R", f"{local_port}:{remote_host}:{remote_port}"])
        direction = "reverse"
    else:
        cmd.extend(["-L", f"{local_port}:{remote_host}:{remote_port}"])
        direction = "forward"

    if ssh_port != 22:
        cmd.extend(["-p", str(ssh_port)])

    if ssh_key:
        cmd.extend(["-i", os.path.expanduser(ssh_key)])

    if ssh_user:
        cmd.append(f"{ssh_user}@{host}")
    else:
        cmd.append(host)

    ctx.info(f"Creating {direction} tunnel: localhost:{local_port} → {remote_host}:{remote_port}")

    if background:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            ctx.success("Tunnel running in background")
            ctx.console.print(f"  Local: localhost:{local_port}")
            ctx.console.print(f"  Remote: {remote_host}:{remote_port}")
        raise typer.Exit(result.returncode)
    else:
        ctx.console.print("[dim]Press Ctrl+C to close the tunnel[/dim]")
        try:
            result = subprocess.run(cmd)
            raise typer.Exit(result.returncode)
        except KeyboardInterrupt:
            ctx.info("Tunnel closed.")


@register_tool
def register(app: typer.Typer) -> None:
    """Register the ssh command group."""
    app.add_typer(ssh_app, name="ssh")
