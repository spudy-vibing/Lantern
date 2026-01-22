"""Runtime context for Lantern commands."""

import json
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console


@dataclass
class Context:
    """Runtime context passed to all commands."""

    console: Console = field(default_factory=Console)
    verbose: bool = False
    quiet: bool = False
    json_output: bool = False
    no_color: bool = False

    def debug(self, message: str) -> None:
        """Print debug message if verbose mode is enabled."""
        if self.verbose and not self.quiet:
            self.console.print(f"[dim]DEBUG: {message}[/dim]")

    def info(self, message: str) -> None:
        """Print info message."""
        if not self.quiet and not self.json_output:
            self.console.print(message)

    def success(self, message: str) -> None:
        """Print success message with green checkmark."""
        if not self.quiet and not self.json_output:
            self.console.print(f"[green]✓[/green] {message}")

    def warning(self, message: str) -> None:
        """Print warning message with yellow indicator."""
        if not self.quiet and not self.json_output:
            self.console.print(f"[yellow]⚠[/yellow] {message}")

    def error(self, message: str, hint: str | None = None) -> None:
        """Print error message with red indicator and optional hint."""
        if not self.json_output:
            self.console.print(f"[red]✗[/red] {message}")
            if hint:
                self.console.print(f"[dim]  Hint: {hint}[/dim]")

    def output(self, data: Any) -> None:
        """Output data in appropriate format (JSON or pretty-printed)."""
        if self.json_output:
            self.console.print_json(json.dumps(data, default=str))
        else:
            self.console.print(data)


_context: Context | None = None


def get_context() -> Context:
    """Get the current runtime context, creating one if necessary."""
    global _context
    if _context is None:
        _context = Context()
    return _context


def set_context(ctx: Context) -> None:
    """Set the current runtime context."""
    global _context
    _context = ctx
