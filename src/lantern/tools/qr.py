"""QR code generation command."""

from typing import Annotated

import typer
from rich.panel import Panel

from lantern.core.context import get_context
from lantern.services.qr import generate_qr_unicode
from lantern.tools import register_tool


def _run_qr(
    text: str,
    invert: bool = False,
    border: int = 1,
) -> None:
    """Generate and display a QR code."""
    ctx = get_context()

    if not text:
        ctx.error("No text provided to encode.")
        raise typer.Exit(1)

    # Generate QR code
    try:
        qr_art = generate_qr_unicode(text, border=border, invert=invert)
    except Exception as e:
        ctx.error(f"Failed to generate QR code: {e}")
        raise typer.Exit(1) from None

    # Display with panel
    panel = Panel(
        qr_art,
        title="[bold]QR Code[/bold]",
        subtitle=f"[dim]{text[:50]}{'...' if len(text) > 50 else ''}[/dim]",
        border_style="blue",
        padding=(1, 2),
    )
    ctx.console.print(panel)


@register_tool
def register(app: typer.Typer) -> None:
    """Register the qr command."""

    @app.command("qr")
    def qr(
        text: Annotated[
            str,
            typer.Argument(help="Text or URL to encode in the QR code."),
        ],
        invert: Annotated[
            bool,
            typer.Option("--invert", "-i", help="Invert colors (white on black)."),
        ] = False,
        border: Annotated[
            int,
            typer.Option("--border", "-b", help="Border size around QR code."),
        ] = 1,
    ) -> None:
        """Generate a QR code from text or URL.

        Examples:
            lantern qr "https://example.com"
            lantern qr "Hello World" --invert
            lantern qr "Contact info" --border 2
        """
        _run_qr(text, invert=invert, border=border)
