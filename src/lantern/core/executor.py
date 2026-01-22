"""Async subprocess execution with safety measures."""

import asyncio
import os
import shutil
from dataclasses import dataclass

from lantern.constants import COMMAND_TIMEOUT_MS
from lantern.exceptions import CommandExecutionError, CommandNotFoundError


@dataclass
class CommandResult:
    """Result of a command execution."""

    command: str
    args: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.return_code == 0

    @property
    def output(self) -> str:
        """Get trimmed stdout output."""
        return self.stdout.strip()


class CommandExecutor:
    """Async command executor with safety features."""

    # Allowlist of commands that can be executed
    ALLOWED_COMMANDS: set[str] = {
        # macOS
        "networksetup",
        "scutil",
        "ipconfig",
        "system_profiler",
        "airport",
        "arp",
        "netstat",
        "route",
        "ping",
        "traceroute",
        "host",
        "nslookup",
        "dig",
        "dscacheutil",
        "sw_vers",
        "sysctl",
        "lsof",
        "defaults",
        "security",
        # Linux
        "nmcli",
        "ip",
        "iw",
        "iwconfig",
        "iwlist",
        "ss",
        "resolvectl",
        "systemd-resolve",
        "hostnamectl",
        "uname",
        "cat",
        "hostname",
        # Cross-platform
        "ssh",
        "ssh-copy-id",
        "curl",
        "wget",
    }

    def __init__(self, timeout_ms: int = COMMAND_TIMEOUT_MS) -> None:
        self.timeout_ms = timeout_ms

    @staticmethod
    def find_command(name: str) -> str | None:
        """Find the full path of a command."""
        return shutil.which(name)

    @staticmethod
    def command_exists(name: str) -> bool:
        """Check if a command exists in PATH."""
        return shutil.which(name) is not None

    async def run(
        self,
        command: str,
        *args: str,
        timeout_ms: int | None = None,
        check: bool = True,
    ) -> CommandResult:
        """Execute a command asynchronously.

        Args:
            command: The command to execute.
            *args: Arguments to pass to the command.
            timeout_ms: Optional timeout in milliseconds.
            check: If True, raise CommandExecutionError on non-zero exit.

        Returns:
            CommandResult with command output and status.

        Raises:
            CommandNotFoundError: If command is not in allowlist or not found.
            CommandExecutionError: If command fails and check is True.
        """
        base_command = command.split("/")[-1]
        if base_command not in self.ALLOWED_COMMANDS:
            raise CommandNotFoundError(command, f"Command '{base_command}' is not allowed.")

        # Handle absolute paths vs command names
        full_path: str
        if command.startswith("/"):
            # Absolute path - check if file exists and is executable
            if os.path.isfile(command) and os.access(command, os.X_OK):
                full_path = command
            else:
                raise CommandNotFoundError(command)
        else:
            # Command name - find in PATH
            found_path = self.find_command(command)
            if found_path is None:
                raise CommandNotFoundError(command)
            full_path = found_path

        timeout = (timeout_ms or self.timeout_ms) / 1000.0

        try:
            process = await asyncio.create_subprocess_exec(
                full_path,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            result = CommandResult(
                command=command,
                args=args,
                return_code=process.returncode or 0,
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else "",
            )

            if check and not result.success:
                raise CommandExecutionError(
                    f"{command} {' '.join(args)}",
                    result.return_code,
                    result.stderr or result.stdout,
                )
            return result

        except TimeoutError:
            raise CommandExecutionError(
                f"{command} {' '.join(args)}", -1, f"Command timed out after {timeout}s"
            ) from None


# Default executor instance
executor = CommandExecutor()
