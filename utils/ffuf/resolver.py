import socket
from typing import Optional


def can_resolve(hostname: Optional[str]) -> bool:
    """Return True if `hostname` resolves via system DNS, False otherwise."""
    if not hostname:
        return False
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False
