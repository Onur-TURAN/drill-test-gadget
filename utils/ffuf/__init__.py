"""ffuf utilities package.

This package breaks the original `ffuftest.py` into modular pieces suitable
for importing by other programs (for example a Go tool that invokes these
scripts). No module executes on import.
"""
from .api import analyze_target, run_concurrency_test

__all__ = ["analyze_target", "run_concurrency_test"]
