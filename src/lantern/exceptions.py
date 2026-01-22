"""Custom exceptions for Lantern."""


class LanternError(Exception):
    """Base exception for all Lantern errors."""

    def __init__(self, message: str, hint: str | None = None) -> None:
        self.message = message
        self.hint = hint
        super().__init__(message)


class CommandNotFoundError(LanternError):
    """Raised when a required system command is not found."""

    def __init__(self, command: str, install_hint: str | None = None) -> None:
        self.command = command
        super().__init__(
            f"Command not found: {command}",
            hint=install_hint or f"Please install '{command}' to use this feature.",
        )


class CommandExecutionError(LanternError):
    """Raised when a command execution fails."""

    def __init__(self, command: str, return_code: int, stderr: str | None = None) -> None:
        self.command = command
        self.return_code = return_code
        self.stderr = stderr
        super().__init__(
            f"Command failed with exit code {return_code}: {command}",
            hint=stderr,
        )


class PlatformNotSupportedError(LanternError):
    """Raised when the current platform is not supported."""

    def __init__(self, platform: str, feature: str | None = None) -> None:
        self.platform = platform
        self.feature = feature
        msg = f"Platform not supported: {platform}"
        if feature:
            msg = f"Feature '{feature}' not supported on {platform}"
        super().__init__(msg)


class DeviceNotFoundError(LanternError):
    """Raised when a device is not found in the registry."""

    def __init__(self, device_name: str) -> None:
        self.device_name = device_name
        super().__init__(
            f"Device not found: {device_name}",
            hint="Use 'lantern devices' to see available devices.",
        )


class ConfigurationError(LanternError):
    """Raised when there's a configuration issue."""

    pass


class NetworkError(LanternError):
    """Raised for network-related errors."""

    pass
