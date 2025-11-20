from typing import Optional


def estimate_bandwidth(t: float, avg_size_bytes: float, avg_response_time: float) -> float:
    """Estimate bandwidth (bytes/sec) from t-factor, average size and response time."""
    if avg_response_time <= 0:
        return 0.0
    return t * (avg_size_bytes / avg_response_time)


def human_readable_bytes(b: Optional[float]) -> str:
    """Return human-readable bandwidth string like '1.23 MB/s'."""
    if not b:
        return "0.00 B/s"
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    v = float(b)
    idx = 0
    while v > 1024 and idx < len(units)-1:
        v /= 1024
        idx += 1
    return f"{v:.2f} {units[idx]}"
