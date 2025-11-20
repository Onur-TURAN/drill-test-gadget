import asyncio
import time
from typing import List, Tuple

try:
    import aiohttp
except Exception:
    aiohttp = None


async def _worker(session: 'aiohttp.ClientSession', url: str, headers: dict, q: asyncio.Queue, results: List[Tuple[float, int, int]]):
    while True:
        try:
            _ = q.get_nowait()
        except asyncio.QueueEmpty:
            return
        t0 = time.perf_counter()
        try:
            async with session.get(url, headers=headers) as resp:
                b = await resp.read()
                dt = time.perf_counter() - t0
                results.append((dt, resp.status, len(b)))
        except Exception:
            dt = time.perf_counter() - t0
            results.append((dt, 0, 0))


async def concurrency_test(url: str, headers: dict, concurrency: int, duration: int) -> Tuple[int, int, float, List[Tuple[float,int,int]]]:
    """Run repeated batches of concurrent requests for a duration.

    Returns: (total_requests_sent, successful_count, achieved_rps, results_list)
    """
    if aiohttp is None:
        raise RuntimeError("aiohttp library is required: pip install aiohttp")

    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=0)
    results: List[Tuple[float,int,int]] = []
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        end = time.time() + duration
        total = 0
        while time.time() < end:
            tasks = []
            q = asyncio.Queue()
            for _ in range(concurrency):
                q.put_nowait(1)
            for _ in range(concurrency):
                tasks.append(asyncio.create_task(_worker(session, url, headers, q, results)))
            await asyncio.gather(*tasks)
            total += concurrency
            await asyncio.sleep(0)
        successful = sum(1 for (_, status, size) in results if status != 0)
        achieved_rps = len(results) / duration if duration > 0 else 0.0
        return len(results), successful, achieved_rps, results
