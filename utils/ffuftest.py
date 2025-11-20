"""Legacy shim: use the modular `ffuf` package instead.

This file used to contain a standalone CLI. It has been converted to a
lightweight shim that exposes the new package. There is intentionally no
`if __name__ == '__main__'` entry point to prevent accidental execution.

Use from Python:

    from drill_test_gadget.utils.ffuf import analyze_target, run_concurrency_test

Or import the package directly:

    from utils.ffuf import analyze_target

"""

from .ffuf.api import analyze_target, run_concurrency_test

__all__ = ["analyze_target", "run_concurrency_test"]
