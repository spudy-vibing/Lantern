"""Directory HTTP server command."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel

from lantern.core.context import get_context
from lantern.services.http_server import FileServer
from lantern.services.qr import generate_qr_unicode
from lantern.tools import register_tool


def _run_serve(
    directory: Path,
    port: int | None = None,
    no_qr: bool = False,
) -> None:
    """Sync wrapper for async command."""
    asyncio.run(_serve_async(directory, port, no_qr))


async def _serve_async(
    directory: Path,
    port: int | None,
    no_qr: bool,
) -> None:
    """Serve a directory via HTTP."""
    ctx = get_context()

    # Validate directory
    if not directory.exists():
        ctx.error(f"Directory not found: {directory}")
        raise typer.Exit(1)

    if not directory.is_dir():
        ctx.error(f"Not a directory: {directory}")
        ctx.info("Use 'lantern drop' to share a single file.")
        raise typer.Exit(1)

    # Count files in directory
    file_count = sum(1 for _ in directory.rglob("*") if _.is_file())

    # Start server
    server = FileServer(directory, port=port, one_shot=False)
    info = server.start()

    ctx.console.print()
    ctx.success(f"Serving [bold]{directory.name}/[/bold] ({file_count} files)")
    ctx.console.print()

    # Show URL
    ctx.console.print(f"  [bold]URL:[/bold] {info.url}")
    ctx.console.print(f"  [dim]Local:[/dim] {info.local_url}")
    ctx.console.print()

    # Generate and display QR code
    if not no_qr:
        qr_art = generate_qr_unicode(info.url, border=1)
        panel = Panel(
            qr_art,
            title="[bold]Scan to Browse[/bold]",
            subtitle=f"[dim]{directory.name}/[/dim]",
            border_style="green",
            padding=(1, 2),
        )
        ctx.console.print(panel)

    ctx.console.print()
    ctx.console.print("[dim]Press Ctrl+C to stop server[/dim]")
    ctx.console.print()

    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        ctx.info("\nStopping server...")
    finally:
        server.stop()
        ctx.success("Server stopped.")


@register_tool
def register(app: typer.Typer) -> None:
    """Register the serve command."""

    @app.command("serve")
    def serve(
        directory: Annotated[
            Path,
            typer.Argument(
                help="Directory to serve (default: current directory).",
                exists=True,
                file_okay=False,
                dir_okay=True,
                resolve_path=True,
            ),
        ] = Path("."),
        port: Annotated[
            int | None,
            typer.Option("--port", "-p", help="Port to serve on (default: auto)."),
        ] = None,
        no_qr: Annotated[
            bool,
            typer.Option("--no-qr", help="Don't display QR code."),
        ] = False,
    ) -> None:
        """Serve a directory via HTTP.

        Creates an HTTP server that serves files from the directory.
        Browse files from any device on the same network.

        Examples:
            lantern serve                    # Serve current directory
            lantern serve ~/Downloads        # Serve specific directory
            lantern serve . --port 9000      # Use specific port
        """
        _run_serve(directory, port, no_qr)
