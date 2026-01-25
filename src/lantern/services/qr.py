"""QR code generation service."""

import qrcode  # type: ignore[import-untyped]
from qrcode.main import QRCode  # type: ignore[import-untyped]


def generate_qr_ascii(data: str, border: int = 1) -> str:
    """Generate a QR code as ASCII art for terminal display.

    Args:
        data: The data to encode in the QR code
        border: Border size (default 1)

    Returns:
        ASCII art string representation of the QR code
    """
    qr = QRCode(
        version=None,  # Auto-determine size
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Use half-block characters for compact display
    # Upper half block: ▀, Lower half block: ▄, Full block: █, Space: ' '
    modules = qr.get_matrix()
    lines: list[str] = []

    # Process two rows at a time using half-block characters
    for row in range(0, len(modules), 2):
        line = ""
        for col in range(len(modules[0])):
            top = modules[row][col]
            bottom = modules[row + 1][col] if row + 1 < len(modules) else False

            if top and bottom:
                line += "█"  # Full block (both dark)
            elif top and not bottom:
                line += "▀"  # Upper half block
            elif not top and bottom:
                line += "▄"  # Lower half block
            else:
                line += " "  # Space (both light)
        lines.append(line)

    return "\n".join(lines)


def generate_qr_unicode(data: str, border: int = 1, invert: bool = False) -> str:
    """Generate a QR code using Unicode block characters.

    Uses a more visible rendering with explicit black/white blocks.

    Args:
        data: The data to encode
        border: Border size
        invert: If True, swap black and white (better for light terminals)

    Returns:
        Unicode string representation
    """
    qr = QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    modules = qr.get_matrix()
    lines: list[str] = []

    # Use two characters per module for better aspect ratio
    black = "  " if invert else "██"
    white = "██" if invert else "  "

    for row in modules:
        line = ""
        for cell in row:
            line += black if cell else white
        lines.append(line)

    return "\n".join(lines)


def generate_wifi_qr_data(
    ssid: str,
    password: str | None = None,
    security: str = "WPA",
    hidden: bool = False,
) -> str:
    """Generate Wi-Fi configuration string for QR code.

    Format: WIFI:T:<security>;S:<ssid>;P:<password>;H:<hidden>;;

    Args:
        ssid: Network name
        password: Network password (None for open networks)
        security: Security type (WPA, WEP, nopass)
        hidden: Whether the network is hidden

    Returns:
        Wi-Fi configuration string for QR encoding
    """
    # Escape special characters in SSID and password
    def escape(s: str) -> str:
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace('"', '\\"')

    # Normalize security type
    sec = security.upper()
    if "WPA" in sec or "WPA2" in sec or "WPA3" in sec:
        sec_type = "WPA"
    elif "WEP" in sec:
        sec_type = "WEP"
    elif password is None or sec in ("NONE", "OPEN", "NOPASS"):
        sec_type = "nopass"
    else:
        sec_type = "WPA"  # Default to WPA if password provided

    parts = [
        f"T:{sec_type}",
        f"S:{escape(ssid)}",
    ]

    if password and sec_type != "nopass":
        parts.append(f"P:{escape(password)}")

    if hidden:
        parts.append("H:true")

    return "WIFI:" + ";".join(parts) + ";;"
