"""High-level API that ties ffuf helper modules together.

This module provides `analyze_target` which performs synchronous sampling
and returns a summary dictionary, and `run_concurrency_test` which runs the
async concurrency test and returns its results. No CLI logic or top-level
execution happens here.
"""
from typing import Optional, Dict, Any
import statistics
import asyncio

from .resolver import can_resolve
from .builder import build_request_target
from .sync import sample_sync
from .concurrency import concurrency_test
from .calc import estimate_bandwidth, human_readable_bytes


def analyze_target(url: str, ip: Optional[str] = None, host_header: Optional[str] = None,
                   samples: int = 8, rps: float = 30.0, safety: float = 0.5, timeout: float = 10.0) -> Dict[str, Any]:
    """Collect samples and return a structured analysis dict.

    The return dictionary contains sampling results and derived metrics.
    """
    parsed_host = None
    try:
        from urllib.parse import urlparse
        parsed_host = urlparse(url).hostname
    except Exception:
        parsed_host = None

    # Note: do not perform network checks here unless caller requested.
    target_url, headers = build_request_target(url, override_ip=ip, host_header=host_header)

    times, sizes = sample_sync(target_url, headers, samples, timeout=timeout)

    if not times:
        return {"error": "no_samples", "message": "No samples collected — connection errors or no response."}

    avg = statistics.mean(times)
    med = statistics.median(times)
    stdev = statistics.pstdev(times) if len(times) > 1 else 0.0
    avg_size = statistics.mean(sizes) if sizes else 0

    t_base = rps * avg
    t_adjusted = t_base * (1.0 + safety)
    t_approx = max(1, int(round(t_adjusted)))

    bw = estimate_bandwidth(t_adjusted, avg_size, avg)

    return {
        "target_url": target_url,
        "host_header": headers.get('Host'),
        "samples": len(times),
        "times": times,
        "sizes": sizes,
        "avg_response_time": avg,
        "median_response_time": med,
        "stdev_response_time": stdev,
        "avg_response_size": avg_size,
        "t_base": t_base,
        "t_adjusted": t_adjusted,
        "t_approx": t_approx,
        "rps": rps,
        "safety": safety,
        "estimated_bandwidth_bps": bw,
        "estimated_bandwidth_human": human_readable_bytes(bw),
        "resolves_via_dns": can_resolve(parsed_host)
    }


def run_concurrency_test(target_url: str, headers: dict, concurrency: int, duration: int):
    """Run the concurrency test and return the raw results.

    This function is synchronous from the caller perspective; it uses
    `asyncio.run` to execute the async test.
    """
    return asyncio.run(concurrency_test(target_url, headers, concurrency, duration))
