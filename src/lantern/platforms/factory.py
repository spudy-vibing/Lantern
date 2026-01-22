"""Platform adapter factory."""

from lantern.constants import IS_LINUX, IS_MACOS, IS_WINDOWS, PLATFORM
from lantern.exceptions import PlatformNotSupportedError
from lantern.platforms.base import PlatformAdapter


def get_platform_adapter() -> PlatformAdapter:
    """Get the appropriate platform adapter for the current OS.

    Returns:
        A PlatformAdapter instance for the current platform.

    Raises:
        PlatformNotSupportedError: If the current platform is not supported.
    """
    if IS_MACOS:
        from lantern.platforms.macos import MacOSAdapter

        return MacOSAdapter()
    elif IS_LINUX:
        from lantern.platforms.linux import LinuxAdapter

        return LinuxAdapter()
    elif IS_WINDOWS:
        from lantern.platforms.windows import WindowsAdapter

        return WindowsAdapter()
    else:
        raise PlatformNotSupportedError(PLATFORM)


_adapter: PlatformAdapter | None = None


def get_adapter() -> PlatformAdapter:
    """Get the cached platform adapter.

    Returns:
        The cached PlatformAdapter instance.
    """
    global _adapter
    if _adapter is None:
        _adapter = get_platform_adapter()
    return _adapter


def reset_adapter() -> None:
    """Reset the cached adapter (useful for testing)."""
    global _adapter
    _adapter = None
