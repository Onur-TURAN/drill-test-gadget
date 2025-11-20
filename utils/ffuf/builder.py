from urllib.parse import urlparse, urlunparse
from typing import Tuple, Optional


def build_request_target(original_url: str, override_ip: Optional[str] = None, host_header: Optional[str] = None) -> Tuple[str, dict]:
    """Build request target URL and headers.

    If `override_ip` is provided, the returned URL will point to that IP with
    the original port preserved; the `Host` header will be set to the original
    hostname unless `host_header` is explicitly provided.
    """
    parsed = urlparse(original_url)
    headers = {"User-Agent": "ffuf-t-tester/1.1"}
    host = parsed.hostname
    if host_header:
        headers['Host'] = host_header
    if override_ip:
        netloc = override_ip
        if parsed.port:
            netloc = f"{override_ip}:{parsed.port}"
        new_parsed = parsed._replace(netloc=netloc)
        target = urlunparse(new_parsed)
        if 'Host' not in headers and host:
            headers['Host'] = host
        return target, headers
    else:
        return original_url, headers
