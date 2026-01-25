"""CLI commands and tools for Lantern."""

from collections.abc import Callable

import typer

# List of tool registration functions
_tool_registrations: list[Callable[[typer.Typer], None]] = []


def register_tool(func: Callable[[typer.Typer], None]) -> Callable[[typer.Typer], None]:
    """Decorator to register a tool's setup function.

    Usage:
        @register_tool
        def register(app: typer.Typer) -> None:
            @app.command("my-command")
            def my_command() -> None:
                ...
    """
    _tool_registrations.append(func)
    return func


def register_all_tools(app: typer.Typer) -> None:
    """Register all discovered tools with the main app."""
    # Import all tool modules to trigger registration
    from lantern.tools import (  # noqa: F401
        diagnose,
        dns,
        drop,
        interfaces,
        port,
        qr,
        router,
        scan,
        serve,
        share,
        sonar,
        whoami,
        wifi,
    )

    for register_func in _tool_registrations:
        register_func(app)
