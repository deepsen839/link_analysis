import ipaddress
import socket
from urllib.parse import urlsplit
from fastapi import HTTPException

def validate_public_url(url: str, allowed_ports: set[int] | None = None) -> str:
    """Reject non-HTTP(S), credentials, local/private IPs and unsafe ports."""
    allowed_ports = allowed_ports or {80, 443}
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"}:
        raise HTTPException(400, "Only http and https URLs are allowed.")
    if not parts.hostname or parts.username or parts.password:
        raise HTTPException(400, "URL must contain a hostname and must not contain credentials.")
    try:
        port = parts.port or (443 if parts.scheme == "https" else 80)
    except ValueError:
        raise HTTPException(400, "Invalid URL port.")
    if port not in allowed_ports:
        raise HTTPException(400, "Only ports 80 and 443 are allowed.")
    host = parts.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".localhost"):
        raise HTTPException(400, "Localhost URLs are not allowed.")
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            addresses = list({ipaddress.ip_address(item[4][0].split("%")[0]) for item in answers})
        except socket.gaierror:
            raise HTTPException(400, "Hostname could not be resolved.")
    if not addresses:
        raise HTTPException(400, "Hostname has no address records.")
    for addr in addresses:
        if not addr.is_global:
            raise HTTPException(400, "Private, loopback, link-local and reserved IP addresses are not allowed.")
    return url
