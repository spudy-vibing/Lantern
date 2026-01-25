"""Simple HTTP server for file sharing."""

import asyncio
import mimetypes
import socket
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread


@dataclass
class ServerInfo:
    """Information about a running server."""

    host: str
    port: int
    path: Path
    is_directory: bool

    @property
    def url(self) -> str:
        """Get the server URL."""
        return f"http://{self.host}:{self.port}"

    @property
    def local_url(self) -> str:
        """Get the localhost URL."""
        return f"http://localhost:{self.port}"


def get_local_ip() -> str:
    """Get the local IP address for LAN access."""
    try:
        # Create a socket to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Doesn't actually connect, just determines route
            s.connect(("8.8.8.8", 80))
            ip: str = s.getsockname()[0]
            return ip
    except OSError:
        return "127.0.0.1"


def find_free_port(start: int = 8000, end: int = 9000) -> int:
    """Find a free port in the given range."""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No free port found in range {start}-{end}")


class SingleFileHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves a single file once."""

    file_path: Path
    filename: str
    on_download: Callable[[], None] | None = None
    download_count: int = 0
    max_downloads: int = 1

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Suppress default logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET request."""
        # Parse the path
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Only serve the file at root or with the filename
        if path not in ("/", f"/{self.filename}"):
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        # Check download limit
        if self.download_count >= self.max_downloads:
            self.send_error(HTTPStatus.GONE, "File no longer available")
            return

        try:
            # Read file
            content = self.file_path.read_bytes()
            content_type = mimetypes.guess_type(self.filename)[0] or "application/octet-stream"

            # Send response
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Content-Disposition", f'attachment; filename="{self.filename}"')
            self.end_headers()
            self.wfile.write(content)

            # Track download
            SingleFileHandler.download_count += 1
            if self.on_download:
                self.on_download()

        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND)
        except PermissionError:
            self.send_error(HTTPStatus.FORBIDDEN)


class DirectoryHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves a directory."""

    base_path: Path

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Suppress default logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET request."""
        # Parse and decode the path
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        # Resolve the requested path (remove leading slash and resolve)
        requested_path = self.base_path if path == "/" else self.base_path / path.lstrip("/")

        # Security: ensure path is within base directory
        try:
            requested_path = requested_path.resolve()
            if not str(requested_path).startswith(str(self.base_path.resolve())):
                self.send_error(HTTPStatus.FORBIDDEN)
                return
        except (ValueError, RuntimeError):
            self.send_error(HTTPStatus.BAD_REQUEST)
            return

        if requested_path.is_dir():
            self._serve_directory(requested_path, path)
        elif requested_path.is_file():
            self._serve_file(requested_path)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def _serve_directory(self, dir_path: Path, url_path: str) -> None:
        """Serve a directory listing."""
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        # Build HTML listing
        html_parts = [
            "<!DOCTYPE html>",
            "<html><head>",
            f"<title>Index of {url_path}</title>",
            "<style>",
            "body { font-family: -apple-system, system-ui, sans-serif; margin: 2em; }",
            "h1 { color: #333; }",
            "ul { list-style: none; padding: 0; }",
            "li { padding: 0.5em 0; border-bottom: 1px solid #eee; }",
            "a { color: #0066cc; text-decoration: none; }",
            "a:hover { text-decoration: underline; }",
            ".dir { font-weight: bold; }",
            ".dir::before { content: '📁 '; }",
            ".file::before { content: '📄 '; }",
            ".size { color: #666; margin-left: 1em; }",
            "</style>",
            "</head><body>",
            f"<h1>Index of {url_path}</h1>",
            "<ul>",
        ]

        # Add parent directory link if not at root
        if url_path != "/":
            parent = "/".join(url_path.rstrip("/").split("/")[:-1]) or "/"
            html_parts.append(f'<li><a href="{parent}">⬆️ Parent Directory</a></li>')

        # Add entries
        for entry in entries:
            name = entry.name
            href = f"{url_path.rstrip('/')}/{name}"
            if entry.is_dir():
                html_parts.append(f'<li><a class="dir" href="{href}/">{name}/</a></li>')
            else:
                size = self._format_size(entry.stat().st_size)
                html_parts.append(
                    f'<li><a class="file" href="{href}">{name}</a>'
                    f'<span class="size">{size}</span></li>'
                )

        html_parts.extend(["</ul>", "</body></html>"])
        content = "\n".join(html_parts).encode("utf-8")

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _serve_file(self, file_path: Path) -> None:
        """Serve a file."""
        try:
            content = file_path.read_bytes()
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND)
        except PermissionError:
            self.send_error(HTTPStatus.FORBIDDEN)

    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size in human-readable form."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
            size //= 1024
        return f"{size:.1f} TB"


class FileServer:
    """Async-friendly file server wrapper."""

    def __init__(
        self,
        path: Path,
        port: int | None = None,
        host: str | None = None,
        one_shot: bool = False,
    ):
        self.path = path.resolve()
        self.port = port or find_free_port()
        self.host = host or get_local_ip()
        self.one_shot = one_shot
        self.is_directory = path.is_dir()
        self._server: HTTPServer | None = None
        self._thread: Thread | None = None
        self._stopped = False
        self._download_complete = asyncio.Event()

    @property
    def info(self) -> ServerInfo:
        """Get server information."""
        return ServerInfo(
            host=self.host,
            port=self.port,
            path=self.path,
            is_directory=self.is_directory,
        )

    def _on_download(self) -> None:
        """Called when a download completes (for one-shot mode)."""
        if self.one_shot:
            self._download_complete.set()

    def start(self) -> ServerInfo:
        """Start the server in a background thread."""
        if self.is_directory:
            # Directory server
            handler = type(
                "Handler",
                (DirectoryHandler,),
                {"base_path": self.path},
            )
        else:
            # Single file server
            handler = type(
                "Handler",
                (SingleFileHandler,),
                {
                    "file_path": self.path,
                    "filename": self.path.name,
                    "on_download": self._on_download,
                    "download_count": 0,
                    "max_downloads": 1 if self.one_shot else float("inf"),
                },
            )

        self._server = HTTPServer(("0.0.0.0", self.port), handler)
        self._thread = Thread(target=self._serve, daemon=True)
        self._thread.start()

        return self.info

    def _serve(self) -> None:
        """Serve requests until stopped."""
        if self._server:
            while not self._stopped:
                self._server.handle_request()

    async def wait_for_download(self, timeout: float | None = None) -> bool:
        """Wait for a download to complete (one-shot mode)."""
        try:
            await asyncio.wait_for(self._download_complete.wait(), timeout=timeout)
            return True
        except TimeoutError:
            return False

    def stop(self) -> None:
        """Stop the server."""
        self._stopped = True
        if self._server:
            self._server.shutdown()
            self._server = None
