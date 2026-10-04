from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("loop_increment", ROOT / "benchmarks" / "loop_increment.kis", "1000000"),
    ("array_increment", ROOT / "benchmarks" / "array_increment.kis", "1000000"),
    ("fenwick_fixed", ROOT / "benchmarks" / "fenwick_fixed.kis", "500000"),
]


def main() -> int:
    print(f"python={sys.version.split()[0]}")
    print("case\tseconds\tresult")

    for name, source, expected in CASES:
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, str(ROOT / "kisite.py"), str(source)],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        elapsed = time.perf_counter() - started
        result = completed.stdout.strip()

        if completed.returncode != 0:
            print(f"{name}\t{elapsed:.6f}\tERROR")
            if completed.stderr:
                print(completed.stderr, file=sys.stderr, end="")
            return completed.returncode

        status = "ok" if result == expected else f"unexpected:{result!r}"
        print(f"{name}\t{elapsed:.6f}\t{status}")
        if result != expected:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
