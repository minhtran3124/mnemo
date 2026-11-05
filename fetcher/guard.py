"""Link and address checks that run before any request (SSRF guard).

check_url and check_host return None when the target is allowed, or a short
reason when it is refused. They run again on every redirect hop.
"""

import ipaddress
import socket
from urllib.parse import urlsplit

import config


def resolve(host: str, port: int) -> list[str]:
    """Resolve a host to its IP address strings. The only DNS lookup (easy to fake)."""
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return [str(info[4][0]) for info in infos]


def is_allowed_address(address: str) -> bool:
    """True only for a global address. IPv4-mapped IPv6 is unwrapped first."""
    try:
        ip = ipaddress.ip_address(address.split("%", 1)[0])
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_global


def check_url(url: str) -> str | None:
    """Check scheme, credentials, port and length. Returns a reason or None."""
    if len(url) > config.FETCH_MAX_URL_CHARS:
        return "link is too long"
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return "link is not valid"
    if parts.scheme not in ("http", "https"):
        return "only http and https links are allowed"
    if not parts.hostname:
        return "link has no host"
    if parts.username is not None or parts.password is not None:
        return "link must not contain a user name or password"
    if port is None:
        port = 443 if parts.scheme == "https" else 80
    if port not in config.FETCH_ALLOWED_PORTS:
        return "port is not allowed"
    return None


def check_host(url: str) -> str | None:
    """Resolve the host and refuse unless every address is global. Reason or None."""
    parts = urlsplit(url)
    host = parts.hostname or ""
    port = parts.port or (443 if parts.scheme == "https" else 80)
    try:
        addresses = resolve(host, port)
    except OSError:
        return "could not look up the host"
    if not addresses:
        return "could not look up the host"
    if not all(is_allowed_address(a) for a in addresses):
        return "address is not allowed"
    return None
