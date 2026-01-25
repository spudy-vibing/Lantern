"""Port checking command."""

import asyncio
from typing import Annotated

import httpx
import typer

from lantern.core.context import get_context
from lantern.tools import register_tool

# Service to check if port is open from outside
PORT_CHECK_SERVICES = [
    "https://portchecker.co/check",  # Returns JSON
    "https://www.yougetsignal.com/tools/open-ports/",
]

# Common port names
COMMON_PORTS: dict[int, str] = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    465: "SMTPS",
    587: "SMTP Submission",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP Alt",
    8443: "HTTPS Alt",
    27017: "MongoDB",
}


async def _check_port_local(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open locally (can connect to it)."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (OSError, TimeoutError, ConnectionRefusedError):
        return False


async def _check_port_external(port: int) -> dict[str, bool | str | None]:
    """Check if a port is accessible from the internet."""
    # Use canyouseeme.org style check
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # Use a public port checker API
            response = await client.get(
                "https://portchecker.co/checking",
                params={"port": port},
                headers={"Accept": "application/json"},
            )
            if response.status_code == 200:
                # Parse response (this is a simplified check)
                text = response.text.lower()
                if "open" in text:
                    return {"open": True, "source": "portchecker.co"}
                elif "closed" in text or "filtered" in text:
                    return {"open": False, "source": "portchecker.co"}
        except (httpx.RequestError, httpx.HTTPStatusError):
            pass

        # Fallback: try to connect to our own public IP
        try:
            ip_response = await client.get("https://api.ipify.org")
            if ip_response.status_code == 200:
                public_ip = ip_response.text.strip()
                is_open = await _check_port_local(public_ip, port, timeout=5.0)
                return {"open": is_open, "source": "direct", "ip": public_ip}
        except (httpx.RequestError, httpx.HTTPStatusError):
            pass

    return {"open": None, "source": None}


def _run_port(
    port: int,
    host: str | None = None,
    external: bool = False,
    json_output: bool = False,
) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_port_async(port, host, external, json_output))


async def _port_async(
    port: int,
    host: str | None,
    external: bool,
    json_output: bool,
) -> None:
    """Check if a port is open."""
    ctx = get_context()
    ctx.json_output = json_output

    service_name = COMMON_PORTS.get(port, "")

    if external:
        # Check if port is accessible from internet
        ctx.info(f"Checking if port {port} is accessible from the internet...")
        result = await _check_port_external(port)

        if json_output:
            ctx.output({
                "port": port,
                "service": service_name,
                "external": True,
                "open": result.get("open"),
                "source": result.get("source"),
            })
            return

        if result.get("open") is None:
            ctx.warning(f"Could not determine if port {port} is externally accessible.")
            ctx.info("Try checking manually at https://portchecker.co/")
        elif result["open"]:
            ctx.success(f"Port {port} is [green]OPEN[/green] from the internet")
            if service_name:
                ctx.info(f"  Service: {service_name}")
        else:
            ctx.info(f"Port {port} is [red]CLOSED[/red] from the internet")
            if service_name:
                ctx.info(f"  Service: {service_name}")
            ctx.info("\n[dim]This could mean:[/dim]")
            ctx.info("  - Nothing is listening on this port")
            ctx.info("  - Your router/firewall is blocking it")
            ctx.info("  - Your ISP is blocking the port")
    else:
        # Check local port
        target_host = host or "localhost"
        ctx.info(f"Checking port {port} on {target_host}...")

        is_open = await _check_port_local(target_host, port)

        if json_output:
            ctx.output({
                "port": port,
                "host": target_host,
                "service": service_name,
                "external": False,
                "open": is_open,
            })
            return

        if is_open:
            ctx.success(f"Port {port} is [green]OPEN[/green] on {target_host}")
            if service_name:
                ctx.info(f"  Service: {service_name}")
        else:
            ctx.info(f"Port {port} is [red]CLOSED[/red] on {target_host}")
            if service_name:
                ctx.info(f"  Service: {service_name}")


@register_tool
def register(app: typer.Typer) -> None:
    """Register the port command."""

    @app.command("port")
    def port(
        port_number: Annotated[
            int,
            typer.Argument(help="Port number to check (1-65535)."),
        ],
        host: Annotated[
            str | None,
            typer.Option("--host", "-h", help="Host to check (default: localhost)."),
        ] = None,
        external: Annotated[
            bool,
            typer.Option("--external", "-e", help="Check if port is accessible from internet."),
        ] = False,
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Check if a port is open.

        By default, checks if a port is open on localhost.
        Use --external to check if the port is accessible from the internet.

        Examples:
            lantern port 8080                # Check localhost:8080
            lantern port 22 --host server    # Check server:22
            lantern port 80 --external       # Check if port 80 is internet-accessible
        """
        if not 1 <= port_number <= 65535:
            ctx = get_context()
            ctx.error("Port must be between 1 and 65535")
            raise typer.Exit(1)

        _run_port(port_number, host, external, json_output)
