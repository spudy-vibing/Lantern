"""Base classes for the universal device control system.

This module defines the core abstractions:
- ControllableDevice: ABC for any device that can be controlled
- Capability: A feature of a device (e.g., volume, power, playback)
- Parameter: Input/output parameter for capabilities
- DeviceState: Current state of a device
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ParameterType(str, Enum):
    """Types of parameters for device capabilities."""

    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    ENUM = "enum"  # Choice from a list of options
    PERCENTAGE = "percentage"  # 0-100
    VOLUME = "volume"  # 0-100, with mute support


@dataclass
class Parameter:
    """A parameter for a device capability.

    Parameters define the inputs and outputs for device actions.
    They include type information, validation constraints, and metadata.
    """

    name: str
    param_type: ParameterType
    description: str = ""
    required: bool = False
    default: Any = None

    # Constraints
    min_value: float | int | None = None
    max_value: float | int | None = None
    choices: list[str] | None = None  # For ENUM type
    step: float | int | None = None  # Increment step

    def validate(self, value: Any) -> tuple[bool, str | None]:
        """Validate a value against this parameter's constraints.

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        if value is None:
            if self.required:
                return False, f"Parameter '{self.name}' is required"
            return True, None

        # Type validation
        if self.param_type == ParameterType.INTEGER:
            if not isinstance(value, int):
                return False, f"Expected integer for '{self.name}'"
        elif self.param_type == ParameterType.FLOAT:
            if not isinstance(value, (int, float)):
                return False, f"Expected number for '{self.name}'"
        elif self.param_type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False, f"Expected boolean for '{self.name}'"
        elif self.param_type == ParameterType.STRING:
            if not isinstance(value, str):
                return False, f"Expected string for '{self.name}'"
        elif self.param_type in (ParameterType.PERCENTAGE, ParameterType.VOLUME):
            if not isinstance(value, (int, float)):
                return False, f"Expected number for '{self.name}'"
            if value < 0 or value > 100:
                return False, f"'{self.name}' must be between 0 and 100"
        elif self.param_type == ParameterType.ENUM and self.choices and value not in self.choices:
            return False, f"'{self.name}' must be one of: {', '.join(self.choices)}"

        # Range validation
        if self.min_value is not None and value < self.min_value:
            return False, f"'{self.name}' must be >= {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return False, f"'{self.name}' must be <= {self.max_value}"

        return True, None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type": self.param_type.value,
            "description": self.description,
            "required": self.required,
            "default": self.default,
            "min": self.min_value,
            "max": self.max_value,
            "choices": self.choices,
            "step": self.step,
        }


@dataclass
class Capability:
    """A capability of a controllable device.

    Capabilities represent features like volume control, power management,
    playback control, etc. Each capability has a set of actions that can
    be performed.
    """

    name: str
    description: str
    actions: list[str] = field(default_factory=list)  # e.g., ["get", "set", "up", "down"]
    parameters: list[Parameter] = field(default_factory=list)
    category: str = "general"  # For grouping: audio, video, power, etc.

    def get_parameter(self, name: str) -> Parameter | None:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def has_action(self, action: str) -> bool:
        """Check if this capability supports an action."""
        return action in self.actions

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "actions": self.actions,
            "parameters": [p.to_dict() for p in self.parameters],
            "category": self.category,
        }


@dataclass
class ActionResult:
    """Result of executing a device action."""

    success: bool
    value: Any = None  # For get operations
    error: str | None = None
    raw_response: Any = None  # Protocol-specific response

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result: dict[str, Any] = {"success": self.success}
        if self.value is not None:
            result["value"] = self.value
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class DeviceState:
    """Current state of a controllable device."""

    is_online: bool = False
    last_seen: str | None = None
    values: dict[str, Any] = field(default_factory=dict)  # capability -> current value
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, capability: str, default: Any = None) -> Any:
        """Get the current value of a capability."""
        return self.values.get(capability, default)

    def set(self, capability: str, value: Any) -> None:
        """Set the current value of a capability."""
        self.values[capability] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_online": self.is_online,
            "last_seen": self.last_seen,
            "values": self.values,
            "metadata": self.metadata,
        }


class ControllableDevice(ABC):
    """Abstract base class for controllable devices.

    Subclasses implement device-specific logic for different protocols
    and device types (UPnP speakers, REST-based TVs, etc.).
    """

    def __init__(
        self,
        device_id: str,
        name: str,
        ip_address: str,
        device_type: str = "unknown",
        manufacturer: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize a controllable device.

        Args:
            device_id: Unique identifier for this device
            name: Human-friendly name
            ip_address: Device IP address
            device_type: Type of device (speaker, tv, light, etc.)
            manufacturer: Device manufacturer
            model: Device model
        """
        self.device_id = device_id
        self.name = name
        self.ip_address = ip_address
        self.device_type = device_type
        self.manufacturer = manufacturer
        self.model = model
        self._capabilities: list[Capability] = []
        self._state = DeviceState()

    @property
    def capabilities(self) -> list[Capability]:
        """Get the list of capabilities this device supports."""
        return self._capabilities

    @property
    def state(self) -> DeviceState:
        """Get the current device state."""
        return self._state

    def get_capability(self, name: str) -> Capability | None:
        """Get a capability by name."""
        for cap in self._capabilities:
            if cap.name == name:
                return cap
        return None

    def add_capability(self, capability: Capability) -> None:
        """Add a capability to this device."""
        self._capabilities.append(capability)

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the device.

        Returns:
            True if connection successful
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the device."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the device is reachable.

        Returns:
            True if device responds to probe
        """
        ...

    @abstractmethod
    async def execute(
        self,
        capability: str,
        action: str,
        **kwargs: Any,
    ) -> ActionResult:
        """Execute an action on a capability.

        Args:
            capability: Name of the capability (e.g., "volume", "power")
            action: Action to perform (e.g., "get", "set", "up", "down")
            **kwargs: Action-specific parameters

        Returns:
            ActionResult with success status and value/error
        """
        ...

    @abstractmethod
    async def refresh_state(self) -> DeviceState:
        """Refresh and return the current device state.

        Queries the device for current values of all capabilities.

        Returns:
            Updated DeviceState
        """
        ...

    def get_all_commands(self) -> list[dict[str, Any]]:
        """Get a list of all available commands for this device.

        Returns:
            List of command dictionaries with capability, action, and parameters
        """
        commands = []
        for cap in self._capabilities:
            for action in cap.actions:
                cmd = {
                    "capability": cap.name,
                    "action": action,
                    "command": f"{cap.name}.{action}",
                    "description": f"{action.title()} {cap.description.lower()}",
                    "category": cap.category,
                    "parameters": [p.to_dict() for p in cap.parameters if p.required or action == "set"],
                }
                commands.append(cmd)
        return commands

    def to_dict(self) -> dict[str, Any]:
        """Convert device to dictionary for serialization."""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "capabilities": [c.to_dict() for c in self._capabilities],
            "state": self._state.to_dict(),
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} {self.name} ({self.ip_address})>"


# Common capability definitions for reuse across adapters

VOLUME_CAPABILITY = Capability(
    name="volume",
    description="Audio volume control",
    actions=["get", "set", "up", "down", "mute", "unmute"],
    parameters=[
        Parameter(
            name="level",
            param_type=ParameterType.VOLUME,
            description="Volume level (0-100)",
            min_value=0,
            max_value=100,
        ),
        Parameter(
            name="step",
            param_type=ParameterType.INTEGER,
            description="Volume step for up/down",
            default=5,
            min_value=1,
            max_value=20,
        ),
    ],
    category="audio",
)

POWER_CAPABILITY = Capability(
    name="power",
    description="Power control",
    actions=["get", "on", "off", "toggle"],
    parameters=[],
    category="power",
)

PLAYBACK_CAPABILITY = Capability(
    name="playback",
    description="Media playback control",
    actions=["play", "pause", "stop", "next", "previous"],
    parameters=[],
    category="media",
)

INPUT_CAPABILITY = Capability(
    name="input",
    description="Input source selection",
    actions=["get", "set", "list"],
    parameters=[
        Parameter(
            name="source",
            param_type=ParameterType.STRING,
            description="Input source name",
        ),
    ],
    category="media",
)
