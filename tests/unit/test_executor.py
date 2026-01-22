"""Tests for command executor."""

import pytest

from lantern.core.executor import CommandExecutor, CommandResult
from lantern.exceptions import CommandNotFoundError


class TestCommandResult:
    """Tests for CommandResult dataclass."""

    def test_success_result(self) -> None:
        """Test successful command result."""
        result = CommandResult(
            command="echo",
            args=("hello",),
            return_code=0,
            stdout="hello\n",
            stderr="",
        )
        assert result.success is True
        assert result.output == "hello"

    def test_failure_result(self) -> None:
        """Test failed command result."""
        result = CommandResult(
            command="false",
            args=(),
            return_code=1,
            stdout="",
            stderr="error message",
        )
        assert result.success is False

    def test_output_strips_whitespace(self) -> None:
        """Test that output property strips whitespace."""
        result = CommandResult(
            command="echo",
            args=(),
            return_code=0,
            stdout="  hello world  \n",
            stderr="",
        )
        assert result.output == "hello world"


class TestCommandExecutor:
    """Tests for CommandExecutor class."""

    def test_allowed_commands(self) -> None:
        """Test that common commands are allowed."""
        executor = CommandExecutor()
        allowed = executor.ALLOWED_COMMANDS

        # macOS commands
        assert "networksetup" in allowed
        assert "scutil" in allowed
        assert "route" in allowed
        assert "ping" in allowed
        assert "arp" in allowed

        # Linux commands
        assert "ip" in allowed
        assert "nmcli" in allowed

        # Cross-platform
        assert "ssh" in allowed
        assert "curl" in allowed

    def test_disallowed_commands(self) -> None:
        """Test that dangerous commands are not allowed."""
        executor = CommandExecutor()
        allowed = executor.ALLOWED_COMMANDS

        # These should NOT be in the allowlist
        assert "rm" not in allowed
        assert "sudo" not in allowed
        assert "chmod" not in allowed
        assert "chown" not in allowed

    def test_find_command_exists(self) -> None:
        """Test finding a command that exists."""
        path = CommandExecutor.find_command("echo")
        assert path is not None
        assert "echo" in path

    def test_find_command_not_exists(self) -> None:
        """Test finding a command that doesn't exist."""
        path = CommandExecutor.find_command("nonexistent_command_xyz")
        assert path is None

    def test_command_exists_true(self) -> None:
        """Test command_exists for existing command."""
        assert CommandExecutor.command_exists("echo") is True

    def test_command_exists_false(self) -> None:
        """Test command_exists for non-existing command."""
        assert CommandExecutor.command_exists("nonexistent_command_xyz") is False

    @pytest.mark.asyncio
    async def test_run_disallowed_command(self) -> None:
        """Test that disallowed commands raise error."""
        executor = CommandExecutor()
        with pytest.raises(CommandNotFoundError):
            await executor.run("rm", "-rf", "/")

    @pytest.mark.asyncio
    async def test_run_allowed_command(self) -> None:
        """Test running an allowed command."""
        executor = CommandExecutor()
        # Use a simple command that exists on all systems
        result = await executor.run("ping", "-c", "1", "127.0.0.1", check=False)
        # Command should complete (success depends on network)
        assert isinstance(result, CommandResult)

    @pytest.mark.asyncio
    async def test_run_with_check_false(self) -> None:
        """Test running command with check=False doesn't raise on failure."""
        executor = CommandExecutor()
        # This should not raise even if it fails
        result = await executor.run("ping", "-c", "1", "192.0.2.1", "-W", "1", check=False)
        assert isinstance(result, CommandResult)

    def test_default_timeout(self) -> None:
        """Test default timeout is set."""
        executor = CommandExecutor()
        assert executor.timeout_ms > 0

    def test_custom_timeout(self) -> None:
        """Test custom timeout."""
        executor = CommandExecutor(timeout_ms=5000)
        assert executor.timeout_ms == 5000
