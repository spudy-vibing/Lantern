"""One-shot file transfer command."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel

from lantern.core.context import get_context
from lantern.services.http_server import FileServer
from lantern.services.qr import generate_qr_unicode
from lantern.tools import register_tool


def _run_drop(
    file_path: Path,
    port: int | None = None,
    timeout: int = 300,
    no_qr: bool = False,
) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_drop_async(file_path, port, timeout, no_qr))


async def _drop_async(
    file_path: Path,
    port: int | None,
    timeout: int,
    no_qr: bool,
) -> None:
    """Share a file via one-shot HTTP server with QR code."""
    ctx = get_context()

    # Validate file
    if not file_path.exists():
        ctx.error(f"File not found: {file_path}")
        raise typer.Exit(1)

    if not file_path.is_file():
        ctx.error(f"Not a file: {file_path}")
        ctx.info("Use 'lantern serve' to share a directory.")
        raise typer.Exit(1)

    # Get file size
    file_size = file_path.stat().st_size
    size_str = _format_size(file_size)

    # Start server
    server = FileServer(file_path, port=port, one_shot=True)
    info = server.start()

    ctx.console.print()
    ctx.success(f"Sharing [bold]{file_path.name}[/bold] ({size_str})")
    ctx.console.print()

    # Show URL
    ctx.console.print(f"  [bold]URL:[/bold] {info.url}/{file_path.name}")
    ctx.console.print(f"  [dim]Local:[/dim] {info.local_url}/{file_path.name}")
    ctx.console.print()

    # Generate and display QR code
    if not no_qr:
        download_url = f"{info.url}/{file_path.name}"
        qr_art = generate_qr_unicode(download_url, border=1)
        panel = Panel(
            qr_art,
            title="[bold]Scan to Download[/bold]",
            subtitle=f"[dim]{file_path.name}[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
        ctx.console.print(panel)

    ctx.console.print()
    ctx.console.print(f"[dim]Waiting for download (timeout: {timeout}s)...[/dim]")
    ctx.console.print("[dim]Press Ctrl+C to cancel[/dim]")
    ctx.console.print()

    try:
        # Wait for download or timeout
        downloaded = await server.wait_for_download(timeout=float(timeout))

        if downloaded:
            ctx.success("File downloaded successfully!")
        else:
            ctx.warning("Timeout reached. No download occurred.")
    except KeyboardInterrupt:
        ctx.info("\nCancelled.")
    finally:
        server.stop()


def _format_size(size: int) -> str:
    """Format file size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size //= 1024
    return f"{size:.1f} TB"


@register_tool
def register(app: typer.Typer) -> None:
    """Register the drop command."""

    @app.command("drop")
    def drop(
        file: Annotated[
            Path,
            typer.Argument(
                help="File to share.",
                exists=True,
                file_okay=True,
                dir_okay=False,
                resolve_path=True,
            ),
        ],
        port: Annotated[
            int | None,
            typer.Option("--port", "-p", help="Port to serve on (default: auto)."),
        ] = None,
        timeout: Annotated[
            int,
            typer.Option("--timeout", "-t", help="Timeout in seconds (default: 300)."),
        ] = 300,
        no_qr: Annotated[
            bool,
            typer.Option("--no-qr", help="Don't display QR code."),
        ] = False,
    ) -> None:
        """Share a file via one-shot HTTP download.

        Creates a temporary HTTP server that serves the file once.
        A QR code is displayed for easy mobile access.

        Examples:
            lantern drop myfile.zip
            lantern drop photo.jpg --port 8080
            lantern drop document.pdf --timeout 60
        """
        _run_drop(file, port, timeout, no_qr)
