# Kisite interpreter microbenchmarks

These small programs are intended to separate the costs that showed up in the
Practice2 B performance probe.

| Benchmark | Purpose | Expected output |
|---|---|---:|
| `loop_increment.kis` | while-loop condition + scalar augmented assignment | `1000000` |
| `array_increment.kis` | loop + indexed read/modify/write | `1000000` |
| `fenwick_fixed.kis` | Fenwick update workload without input parsing | `500000` |

Run all benchmarks from the repository root:

```bash
python benchmarks/run.py
```

Or time one directly. On PowerShell:

```powershell
Measure-Command { python kisite.py benchmarks/loop_increment.kis > $null }
Measure-Command { python kisite.py benchmarks/array_increment.kis > $null }
Measure-Command { python kisite.py benchmarks/fenwick_fixed.kis > $null }
```

`fenwick_fixed.kis` intentionally performs 500,000 Fenwick updates at `p = 1`,
so each update takes the long update path through a size-500,000 tree. It has no
stdin dependency; comparing it with the Practice2 B maximum-query probe helps
separate interpreter execution cost from `readints` / input cost.

These are performance probes, not unit tests, and are intentionally excluded
from the normal test suite.
