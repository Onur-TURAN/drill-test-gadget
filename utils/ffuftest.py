#!/usr/bin/env python3
import argparse
import asyncio
import time
import statistics
from typing import List, Tuple
import sys
import socket
from urllib.parse import urlparse, urlunparse

try:
    import requests
except Exception:
    print("Please install 'requests': pip install requests")
    sys.exit(1)

try:
    import aiohttp
except Exception:
    print("Please install 'aiohttp': pip install aiohttp")
    sys.exit(1)


# Check if a hostname resolves via system DNS
def can_resolve(hostname: str) -> bool:
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False


# Synchronous sampling of GET requests; returns (times, sizes)
def sample_sync(target_url: str, headers: dict, samples: int, timeout: float = 10.0) -> Tuple[List[float], List[int]]:
    times = []
    sizes = []
    for i in range(samples):
        try:
            t0 = time.perf_counter()
            r = requests.get(target_url, headers=headers, timeout=timeout)
            dt = time.perf_counter() - t0
            times.append(dt)
            sizes.append(len(r.content))
            print(f"[{i+1}/{samples}] status={r.status_code} time={dt:.3f}s size={len(r.content)}")
        except Exception as e:
            print(f"[{i+1}/{samples}] Error: {e}")
    return times, sizes


# Worker coroutine for a single request; appends (elapsed, status, size) to results
async def _worker(session: aiohttp.ClientSession, url: str, headers: dict, q: asyncio.Queue, results: List[Tuple[float, int, int]]):
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


# Run repeated batches of concurrent requests for a duration; returns stats and results
async def concurrency_test(url: str, headers: dict, concurrency: int, duration: int) -> Tuple[int, int, float, List[Tuple[float,int,int]]]:
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


# Estimate bandwidth (bytes/sec) from t-factor, average size and response time
def estimate_bandwidth(t: float, avg_size_bytes: float, avg_response_time: float) -> float:
    if avg_response_time <= 0:
        return 0.0
    return t * (avg_size_bytes / avg_response_time)


# Human-readable bytes/sec string
def human_readable_bytes(b: float) -> str:
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    v = b
    idx = 0
    while v > 1024 and idx < len(units)-1:
        v /= 1024
        idx += 1
    return f"{v:.2f} {units[idx]}"


# Build request target URL and headers, optionally overriding DNS with an IP and Host header
def build_request_target(original_url: str, override_ip: str = None, host_header: str = None) -> Tuple[str, dict]:
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


def main():
    p = argparse.ArgumentParser(description="ffuf -t calculator and small test utility")
    p.add_argument("--url", required=True, help="Full URL to test (e.g. http://converse.example.com/)")
    p.add_argument("--ip", help="If the target DNS does not resolve, provide the IP here (e.g. 10.10.10.5)")
    p.add_argument("--host-header", help="Explicit Host header to send (e.g. converse.example.com)")
    p.add_argument("--samples", type=int, default=8, help="Number of samples to collect for average response time")
    p.add_argument("--rps", type=float, default=30.0, help="Target RPS (requests per second)")
    p.add_argument("--safety", type=float, default=0.5, help="Safety factor (e.g. 0.5 = +50%)")
    p.add_argument("--test-concurrency", action="store_true", help="Run a short concurrency test with the computed or given concurrency")
    p.add_argument("--concurrency", type=int, default=None, help="Concurrency to use for the test; if not set the calculated value is used")
    p.add_argument("--duration", type=int, default=8, help="Duration of the concurrency test in seconds")
    args = p.parse_args()

    print("\n*** ffuf -t tester (use only against authorized targets) ***\n")
    print(f"Target URL: {args.url}")
    parsed = urlparse(args.url)
    hostname = parsed.hostname

    if hostname and not can_resolve(hostname) and not args.ip:
        print(f"WARNING: '{hostname}' does not resolve via DNS and --ip was not provided.")
        print("Options:")
        print("  1) Ensure you are connected to the required network (e.g. VPN).")
        print("  2) Add a hosts entry, for example:")
        print("       <target_ip>  converse.example.com")
        print("  3) If you know the IP, provide it with --ip 10.10.10.5")
        print("  4) Quick test with curl: curl -H 'Host: converse.example.com' http://<IP>/")
        print("Run again with --ip or add a hosts entry.\n")
        return

    target_url, headers = build_request_target(args.url, override_ip=args.ip, host_header=args.host_header)
    print(f"Request URL: {target_url}")
    print(f"Host header to be sent: {headers.get('Host','(none)')}")

    times, sizes = sample_sync(target_url, headers, args.samples)

    if not times:
        print("No samples collected — connection errors or no response.")
        return

    avg = statistics.mean(times)
    med = statistics.median(times)
    stdev = statistics.pstdev(times) if len(times) > 1 else 0.0
    avg_size = statistics.mean(sizes) if sizes else 0

    print("\n--- Summary (sampling) ---")
    print(f"Average response time: {avg:.3f} s (median {med:.3f} s, stdev {stdev:.3f})")
    print(f"Average response size: {avg_size:.0f} bytes")

    t_base = args.rps * avg
    t_adjusted = t_base * (1.0 + args.safety)

    print("\n--- Calculation ---")
    print(f"Target RPS: {args.rps} req/s")
    print(f"Base t = RPS * avg_response_time = {args.rps} * {avg:.3f} = {t_base:.2f}")
    print(f"Safety factor ({args.safety*100:.0f}%) applied: t_adjusted = {t_adjusted:.2f}")
    print(f"Approx t (integer): {max(1, int(round(t_adjusted)))}")

    bw = estimate_bandwidth(t_adjusted, avg_size, avg)
    print(f"Estimated bandwidth requirement: {human_readable_bytes(bw)}")

    if args.test_concurrency:
        concurrency = args.concurrency if args.concurrency is not None else max(1, int(round(t_adjusted)))
        print(f"\nStarting: concurrency test (concurrency={concurrency}, duration={args.duration}s) — run only against authorized targets")
        try:
            total, successful, achieved_rps, results = asyncio.run(concurrency_test(target_url, headers, concurrency, args.duration))
            print(f"Test completed: sent={total}, successful={successful}, achieved_rps={achieved_rps:.2f}")
            err = (total - successful) / total if total>0 else 0
            print(f"Error rate: {err*100:.1f}%")
            if results:
                sample_times = [t for (t,_,_) in results]
                print(f"Test avg response time: {statistics.mean(sample_times):.3f}s (n={len(sample_times)})")
        except Exception as e:
            print(f"Error during concurrency test: {e}")

    print("\nDone. Re-run with different --rps or --safety to test other settings.")


if __name__ == '__main__':
    main()
