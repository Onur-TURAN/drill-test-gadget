import time
from typing import List, Tuple

try:
    import requests
except Exception:  # keep import-time failure obvious to integrators
    requests = None


def sample_sync(target_url: str, headers: dict, samples: int, timeout: float = 10.0) -> Tuple[List[float], List[int]]:
    """Perform synchronous sampling of GET requests.

    Returns a tuple (times, sizes).
    """
    if requests is None:
        raise RuntimeError("requests library is required: pip install requests")

    times = []
    sizes = []
    for i in range(samples):
        try:
            t0 = time.perf_counter()
            r = requests.get(target_url, headers=headers, timeout=timeout)
            dt = time.perf_counter() - t0
            times.append(dt)
            sizes.append(len(r.content))
        except Exception:
            # On errors we skip the sample but keep going
            continue
    return times, sizes
