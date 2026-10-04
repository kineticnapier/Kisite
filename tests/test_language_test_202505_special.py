from pathlib import Path
from queue import Empty, Queue
import subprocess
import sys
import threading
import unittest

import kisite


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "atcoder" / "language_test_202505"


class InteractiveProcess:
    def __init__(self, source: Path, *, compiled: bool):
        command = [sys.executable, "kisite.py"]
        if compiled:
            command.append("--compiled")
        command.append(str(source))
        self.process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.lines: Queue[str | None] = Queue()

        def reader():
            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.lines.put(line.rstrip("\r\n"))
            self.lines.put(None)

        threading.Thread(target=reader, daemon=True).start()

    def write(self, line: str):
        assert self.process.stdin is not None
        self.process.stdin.write(line + "\n")
        self.process.stdin.flush()

    def read(self, timeout: float = 3.0) -> str:
        try:
            line = self.lines.get(timeout=timeout)
        except Empty as exc:
            self.kill()
            raise AssertionError("interactive output was not flushed in time") from exc
        if line is None:
            stderr = self.process.stderr.read() if self.process.stderr is not None else ""
            self.close_pipes()
            raise AssertionError(f"interactive process ended early: {stderr}")
        return line

    def close_pipes(self):
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            if stream is not None and not stream.closed:
                stream.close()

    def finish(self, timeout: float = 3.0):
        if self.process.stdin is not None and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            returncode = self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            self.kill()
            raise AssertionError("interactive process did not terminate") from exc
        stderr = self.process.stderr.read() if self.process.stderr is not None else ""
        self.close_pipes()
        if returncode != 0:
            raise AssertionError(f"interactive process failed with {returncode}: {stderr}")

    def kill(self):
        if self.process.poll() is None:
            self.process.kill()
            self.process.wait()
        self.close_pipes()


class LanguageTest202505SpecialTests(unittest.TestCase):
    def run_practice_b(self, *, compiled: bool, order: str, q_limit: int):
        source = EXAMPLES / "practice_b.kis"
        proc = InteractiveProcess(source, compiled=compiled)
        rank = {ch: i for i, ch in enumerate(order)}
        proc.write(f"{len(order)} {q_limit}")
        queries = 0
        while True:
            line = proc.read()
            parts = line.split()
            self.assertTrue(parts)
            if parts[0] == "?":
                self.assertEqual(len(parts), 3)
                a, b = parts[1], parts[2]
                self.assertIn(a, rank)
                self.assertIn(b, rank)
                self.assertNotEqual(a, b)
                queries += 1
                self.assertLessEqual(queries, q_limit)
                proc.write("<" if rank[a] < rank[b] else ">")
            elif parts[0] == "!":
                self.assertEqual(len(parts), 2)
                self.assertEqual(parts[1], order)
                break
            else:
                self.fail(f"invalid PracticeB output: {line}")
        proc.finish()

    def test_practice_b_interactive(self):
        for compiled in (False, True):
            with self.subTest(compiled=compiled, n=5):
                self.run_practice_b(compiled=compiled, order="EDCBA", q_limit=7)
            with self.subTest(compiled=compiled, n=26):
                self.run_practice_b(
                    compiled=compiled,
                    order="ZYXWVUTSRQPONMLKJIHGFEDCBA",
                    q_limit=100,
                )

    def test_abc244_c_interactive(self):
        source = EXAMPLES / "abc244_c.kis"
        n = 4
        for compiled in (False, True):
            with self.subTest(compiled=compiled):
                proc = InteractiveProcess(source, compiled=compiled)
                proc.write(str(n))
                used: set[int] = set()
                while True:
                    mine = int(proc.read())
                    self.assertTrue(1 <= mine <= 2 * n + 1)
                    self.assertNotIn(mine, used)
                    used.add(mine)
                    reply = next((x for x in range(1, 2 * n + 2) if x not in used), 0)
                    proc.write(str(reply))
                    if reply == 0:
                        break
                    used.add(reply)
                proc.finish()
                self.assertEqual(len(used), 2 * n + 1)

    def test_future_contest_2019_final_a_valid_commands(self):
        source = (EXAMPLES / "future_contest_2019_final_a.kis").read_text(encoding="utf-8")
        t = 4
        n = 3
        m = 2
        input_data = """\
4 3 2
1 2 100 0 0 0
2 4 200 1 2 3
"""
        for runner in (kisite.run, kisite.run_compiled):
            output = runner(source, input_data)
            self.assertEqual(len(output), t)
            self.assertTrue(all(line == "3" for line in output))

    def test_ahc040_a_interactive_format(self):
        source = EXAMPLES / "ahc040_a.kis"
        n = 30
        turns = 15
        header = [f"{n} {turns} 1000"]
        header.extend(f"{10000 + i} {20000 + i}" for i in range(n))
        for compiled in (False, True):
            with self.subTest(compiled=compiled):
                proc = InteractiveProcess(source, compiled=compiled)
                for line in header:
                    proc.write(line)
                for _ in range(turns):
                    count = int(proc.read())
                    self.assertEqual(count, n)
                    previous: set[int] = set()
                    for expected_p in range(n):
                        parts = proc.read().split()
                        self.assertEqual(len(parts), 4)
                        p = int(parts[0])
                        r = int(parts[1])
                        d = parts[2]
                        b = int(parts[3])
                        self.assertEqual(p, expected_p)
                        self.assertIn(r, (0, 1))
                        self.assertIn(d, ("U", "L"))
                        self.assertTrue(b == -1 or b in previous)
                        previous.add(p)
                    proc.write("100000 100000")
                proc.finish()


if __name__ == "__main__":
    unittest.main()
