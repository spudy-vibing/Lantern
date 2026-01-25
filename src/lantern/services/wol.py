"""Wake-on-LAN service.

Sends magic packets to wake up devices over the network.
"""

from __future__ import annotations

import re
import socket
from dataclasses import dataclass


@dataclass
class WolResult:
    """Result of a Wake-on-LAN attempt."""

    mac_address: str
    broadcast_address: str
    port: int
    success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, str | int | bool | None]:
        """Convert to dictionary."""
        return {
            "mac_address": self.mac_address,
            "broadcast_address": self.broadcast_address,
            "port": self.port,
            "success": self.success,
            "error": self.error,
        }


def normalize_mac(mac: str) -> str:
    """Normalize a MAC address to XX:XX:XX:XX:XX:XX format.

    Accepts formats:
        - AA:BB:CC:DD:EE:FF
        - AA-BB-CC-DD-EE-FF
        - AABBCCDDEEFF
        - aa:bb:cc:dd:ee:ff
        - 0:c:8a:91:3e:b3 (without leading zeros)
    """
    # Handle MAC addresses with missing leading zeros (e.g., "0:c:8a" -> "00:0c:8a")
    parts = mac.replace("-", ":").replace(".", ":").split(":")

    if len(parts) == 6:
        # Pad each part to 2 characters and join
        mac_clean = "".join(p.zfill(2) for p in parts).upper()
    else:
        # Remove common separators and convert to uppercase
        mac_clean = re.sub(r"[:\-\.]", "", mac.upper())

    if len(mac_clean) != 12:
        raise ValueError(f"Invalid MAC address: {mac}")

    if not all(c in "0123456789ABCDEF" for c in mac_clean):
        raise ValueError(f"Invalid MAC address: {mac}")

    # Format as XX:XX:XX:XX:XX:XX
    return ":".join(mac_clean[i : i + 2] for i in range(0, 12, 2))


def create_magic_packet(mac: str) -> bytes:
    """Create a Wake-on-LAN magic packet.

    The magic packet consists of:
    - 6 bytes of 0xFF (the synchronization stream)
    - 16 repetitions of the target MAC address (6 bytes each)

    Total: 6 + (16 * 6) = 102 bytes
    """
    # Normalize and convert MAC to bytes
    mac_normalized = normalize_mac(mac)
    mac_bytes = bytes.fromhex(mac_normalized.replace(":", ""))

    # Create magic packet: 6 x 0xFF + 16 x MAC
    magic = b"\xff" * 6 + mac_bytes * 16

    return magic


def send_magic_packet(
    mac: str,
    broadcast: str = "255.255.255.255",
    port: int = 9,
) -> WolResult:
    """Send a Wake-on-LAN magic packet.

    Args:
        mac: Target MAC address
        broadcast: Broadcast address (default: 255.255.255.255)
        port: UDP port to send to (default: 9, also common: 7)

    Returns:
        WolResult with success status
    """
    try:
        mac_normalized = normalize_mac(mac)
        packet = create_magic_packet(mac_normalized)

        # Create UDP socket with broadcast enabled
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            sock.sendto(packet, (broadcast, port))
            return WolResult(
                mac_address=mac_normalized,
                broadcast_address=broadcast,
                port=port,
                success=True,
            )
        finally:
            sock.close()

    except ValueError as e:
        return WolResult(
            mac_address=mac,
            broadcast_address=broadcast,
            port=port,
            success=False,
            error=str(e),
        )
    except OSError as e:
        return WolResult(
            mac_address=mac,
            broadcast_address=broadcast,
            port=port,
            success=False,
            error=f"Network error: {e}",
        )


def get_subnet_broadcast(ip_address: str, netmask: str = "255.255.255.0") -> str:
    """Calculate the broadcast address for a subnet.

    Args:
        ip_address: An IP address in the subnet
        netmask: Subnet mask (default: /24)

    Returns:
        Broadcast address for the subnet
    """
    ip_parts = [int(x) for x in ip_address.split(".")]
    mask_parts = [int(x) for x in netmask.split(".")]

    # Broadcast = IP | ~Netmask
    broadcast_parts = [ip | (~mask & 0xFF) for ip, mask in zip(ip_parts, mask_parts, strict=True)]

    return ".".join(str(x) for x in broadcast_parts)
