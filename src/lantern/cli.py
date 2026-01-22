"""Main CLI application for Lantern."""

import typer
from rich.console import Console

from lantern import __app_name__, __version__
from lantern.tools import register_all_tools

app = typer.Typer(
    name=__app_name__,
    help="A powerful network toolkit for developers.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold]{__app_name__}[/bold] version [cyan]{__version__}[/cyan]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Lantern - A powerful network toolkit for developers."""
    pass


# Register all tools
register_all_tools(app)


if __name__ == "__main__":
    app()
