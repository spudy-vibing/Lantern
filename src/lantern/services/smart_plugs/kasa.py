"""Kasa smart plug adapter.

Supports TP-Link Kasa smart plugs, switches, and power strips.
Requires the optional 'power' dependency: pip install lantern-net[power]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kasa import SmartDevice


@dataclass
class PlugInfo:
    """Information about a smart plug."""

    name: str
    host: str
    model: str
    is_on: bool
    alias: str | None = None
    has_emeter: bool = False
    current_power: float | None = None  # Watts
    today_energy: float | None = None  # kWh

    def to_dict(self) -> dict[str, str | bool | float | None]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "host": self.host,
            "model": self.model,
            "is_on": self.is_on,
            "alias": self.alias,
            "has_emeter": self.has_emeter,
            "current_power": self.current_power,
            "today_energy": self.today_energy,
        }


def _check_kasa_installed() -> None:
    """Check if python-kasa is installed."""
    try:
        import kasa  # noqa: F401
    except ImportError:
        raise ImportError(
            "python-kasa is required for smart plug support. "
            "Install with: pip install lantern-net[power]"
        ) from None


async def discover_devices(timeout: float = 5.0) -> list[PlugInfo]:
    """Discover Kasa smart devices on the network.

    Args:
        timeout: Discovery timeout in seconds

    Returns:
        List of discovered devices
    """
    _check_kasa_installed()

    from kasa import Discover

    devices: list[PlugInfo] = []

    discovered = await Discover.discover(timeout=timeout)

    for host, device in discovered.items():
        await device.update()

        power = None
        energy = None
        has_emeter = device.has_emeter

        if has_emeter:
            try:
                emeter = device.emeter_realtime
                if emeter:
                    power = emeter.get("power")
                    # Get today's energy if available
                    today = device.emeter_today
                    if today is not None:
                        energy = today
            except Exception:
                pass

        devices.append(
            PlugInfo(
                name=device.alias or host,
                host=host,
                model=device.model,
                is_on=device.is_on,
                alias=device.alias,
                has_emeter=has_emeter,
                current_power=power,
                today_energy=energy,
            )
        )

    return devices


async def get_device(host: str) -> SmartDevice:
    """Get a Kasa device by host/IP.

    Args:
        host: IP address or hostname

    Returns:
        SmartDevice instance
    """
    _check_kasa_installed()

    from kasa import Discover

    device = await Discover.discover_single(host)
    await device.update()
    return device


async def turn_on(host: str) -> bool:
    """Turn on a device.

    Args:
        host: IP address or hostname

    Returns:
        True if successful
    """
    device = await get_device(host)
    await device.turn_on()
    return True


async def turn_off(host: str) -> bool:
    """Turn off a device.

    Args:
        host: IP address or hostname

    Returns:
        True if successful
    """
    device = await get_device(host)
    await device.turn_off()
    return True


async def toggle(host: str) -> bool:
    """Toggle device state.

    Args:
        host: IP address or hostname

    Returns:
        New state (True = on, False = off)
    """
    device = await get_device(host)
    if device.is_on:
        await device.turn_off()
        return False
    else:
        await device.turn_on()
        return True


async def get_power_usage(host: str) -> dict[str, float | None]:
    """Get current power usage.

    Args:
        host: IP address or hostname

    Returns:
        Dict with power (watts) and today_energy (kWh)
    """
    device = await get_device(host)

    if not device.has_emeter:
        return {"power": None, "today_energy": None, "has_emeter": False}

    emeter = device.emeter_realtime
    power = emeter.get("power") if emeter else None
    today = device.emeter_today

    return {
        "power": power,
        "today_energy": today,
        "has_emeter": True,
    }
