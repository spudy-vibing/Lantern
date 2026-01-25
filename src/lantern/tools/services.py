"""mDNS service discovery commands."""

import asyncio
import re
from dataclasses import dataclass
from typing import Annotated

import typer
from rich.table import Table

from lantern.core.context import get_context
from lantern.tools import register_tool


@dataclass
class ServiceInfo:
    """Information about a discovered service."""

    name: str
    service_type: str
    domain: str
    host: str | None = None
    port: int | None = None
    txt_records: dict[str, str] | None = None

    def to_dict(self) -> dict[str, str | int | dict[str, str] | None]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "service_type": self.service_type,
            "domain": self.domain,
            "host": self.host,
            "port": self.port,
            "txt_records": self.txt_records,
        }


# Common service types with friendly names
SERVICE_TYPES: dict[str, str] = {
    "_http._tcp": "Web Server",
    "_https._tcp": "Secure Web",
    "_ssh._tcp": "SSH",
    "_sftp-ssh._tcp": "SFTP",
    "_smb._tcp": "Windows Share",
    "_afpovertcp._tcp": "Apple Share",
    "_nfs._tcp": "NFS",
    "_ftp._tcp": "FTP",
    "_printer._tcp": "Printer",
    "_ipp._tcp": "Printer (IPP)",
    "_pdl-datastream._tcp": "Printer (PDL)",
    "_airplay._tcp": "AirPlay",
    "_raop._tcp": "AirPlay Audio",
    "_airport._tcp": "AirPort",
    "_homekit._tcp": "HomeKit",
    "_hap._tcp": "HomeKit (HAP)",
    "_companion-link._tcp": "Apple Companion",
    "_googlecast._tcp": "Chromecast",
    "_spotify-connect._tcp": "Spotify Connect",
    "_sonos._tcp": "Sonos",
    "_daap._tcp": "iTunes/DAAP",
    "_dacp._tcp": "iTunes Remote",
    "_touch-able._tcp": "Apple Remote",
    "_workstation._tcp": "Workstation",
    "_device-info._tcp": "Device Info",
    "_rfb._tcp": "VNC/Remote Desktop",
    "_vnc._tcp": "VNC",
    "_rdp._tcp": "Remote Desktop",
    "_mysql._tcp": "MySQL",
    "_postgresql._tcp": "PostgreSQL",
    "_mongodb._tcp": "MongoDB",
    "_redis._tcp": "Redis",
    "_elasticsearch._tcp": "Elasticsearch",
    "_mqtt._tcp": "MQTT",
    "_coap._udp": "CoAP (IoT)",
    "_hue._tcp": "Philips Hue",
    "_elg._tcp": "Elgato",
}


async def browse_services(
    service_type: str,
    timeout: float = 5.0,
) -> list[ServiceInfo]:
    """Browse for mDNS services of a given type.

    Uses dns-sd command on macOS.
    """
    services: list[ServiceInfo] = []

    # Run dns-sd browse command with timeout
    try:
        process = await asyncio.create_subprocess_exec(
            "dns-sd",
            "-B",
            service_type,
            "local.",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except TimeoutError:
            process.terminate()
            await process.wait()
            stdout = process.stdout.read() if process.stdout else b""

        # Parse output
        # Format: Timestamp  A/R    Flags  if Domain  Service Type  Instance Name
        for line in stdout.decode().split("\n"):
            if line.startswith("Browsing") or line.startswith("DATE:") or not line.strip():
                continue

            # Match lines like: 14:32:15.123  Add        2   4 local.  _http._tcp.  My Web Server
            match = re.match(
                r"\d+:\d+:\d+\.\d+\s+Add\s+\d+\s+\d+\s+(\S+)\s+(\S+)\s+(.+)",
                line,
            )
            if match:
                domain, svc_type, name = match.groups()
                services.append(
                    ServiceInfo(
                        name=name.strip(),
                        service_type=svc_type.rstrip("."),
                        domain=domain.rstrip("."),
                    )
                )

    except FileNotFoundError:
        # dns-sd not available
        pass

    return services


async def resolve_service(service: ServiceInfo, timeout: float = 3.0) -> ServiceInfo:
    """Resolve service details (host, port, TXT records)."""
    try:
        process = await asyncio.create_subprocess_exec(
            "dns-sd",
            "-L",
            service.name,
            service.service_type,
            service.domain,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
        except TimeoutError:
            process.terminate()
            await process.wait()
            stdout = process.stdout.read() if process.stdout else b""

        output = stdout.decode()

        # Parse host and port
        # Format: hostname.local.:port
        host_match = re.search(r"can be reached at\s+(\S+):(\d+)", output)
        if host_match:
            service.host = host_match.group(1).rstrip(".")
            service.port = int(host_match.group(2))

    except FileNotFoundError:
        pass

    return service


def _run_services(
    service_type: str | None,
    timeout: float,
    resolve: bool,
    json_output: bool,
) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_services_async(service_type, timeout, resolve, json_output))


async def _services_async(
    service_type: str | None,
    timeout: float,
    resolve: bool,
    json_output: bool,
) -> None:
    """Browse for network services using mDNS."""
    ctx = get_context()
    ctx.json_output = json_output

    if service_type:
        # Browse specific service type
        if not service_type.startswith("_"):
            service_type = f"_{service_type}"
        if "._tcp" not in service_type and "._udp" not in service_type:
            service_type = f"{service_type}._tcp"

        types_to_scan = [service_type]
    else:
        # Browse common service types
        types_to_scan = list(SERVICE_TYPES.keys())

    if not json_output:
        ctx.info("Scanning for network services...")

    all_services: list[ServiceInfo] = []

    # Scan all service types concurrently
    tasks = [browse_services(st, timeout=timeout) for st in types_to_scan]
    results = await asyncio.gather(*tasks)

    for services in results:
        all_services.extend(services)

    # Remove duplicates
    seen: set[tuple[str, str]] = set()
    unique_services: list[ServiceInfo] = []
    for svc in all_services:
        key = (svc.name, svc.service_type)
        if key not in seen:
            seen.add(key)
            unique_services.append(svc)

    # Optionally resolve service details
    if resolve and unique_services:
        if not json_output:
            ctx.info("Resolving service details...")
        resolve_tasks = [resolve_service(svc) for svc in unique_services]
        unique_services = await asyncio.gather(*resolve_tasks)

    if json_output:
        ctx.output([s.to_dict() for s in unique_services])
        return

    if not unique_services:
        ctx.warning("No services found.")
        return

    # Group by service type
    by_type: dict[str, list[ServiceInfo]] = {}
    for svc in unique_services:
        by_type.setdefault(svc.service_type, []).append(svc)

    ctx.console.print()

    for svc_type, services in sorted(by_type.items()):
        friendly_name = SERVICE_TYPES.get(svc_type, svc_type)
        table = Table(
            title=f"{friendly_name} ({svc_type})",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Name", style="cyan")

        if resolve:
            table.add_column("Host")
            table.add_column("Port")

        for svc in sorted(services, key=lambda s: s.name):
            if resolve:
                table.add_row(
                    svc.name,
                    svc.host or "-",
                    str(svc.port) if svc.port else "-",
                )
            else:
                table.add_row(svc.name)

        ctx.console.print(table)
        ctx.console.print()


@register_tool
def register(app: typer.Typer) -> None:
    """Register the services command."""

    @app.command("services")
    def services(
        service_type: Annotated[
            str | None,
            typer.Argument(help="Service type to browse (e.g., http, ssh, printer)."),
        ] = None,
        timeout: Annotated[
            float,
            typer.Option("--timeout", "-t", help="Browse timeout in seconds."),
        ] = 5.0,
        resolve: Annotated[
            bool,
            typer.Option("--resolve", "-r", help="Resolve host and port for each service."),
        ] = False,
        json_output: Annotated[
            bool,
            typer.Option("--json", "-j", help="Output in JSON format."),
        ] = False,
    ) -> None:
        """Browse network services using mDNS/Bonjour.

        Discovers services advertised on the local network like printers,
        web servers, SSH servers, media devices, and more.

        Examples:
            lantern services                    # Browse all common services
            lantern services http               # Browse HTTP services
            lantern services ssh --resolve      # Browse SSH with host details
            lantern services printer --json     # Printers as JSON
        """
        _run_services(service_type, timeout, resolve, json_output)
