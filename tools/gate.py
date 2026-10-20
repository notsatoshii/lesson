#!/usr/bin/env python3
"""Run the cycle gate (timing.py and lint.py) and save both results as one gate.json (stdlib only).

Usage: python gate.py <plan.md> --out <history/cycle-N/gate.json> [--mode M] [--band B] [--house lesson.md]

Writes {"timing": {...}, "lint": {...}} with each tool's exit code, run time in seconds and parsed
JSON, plus "short_cycle": true when either tool exits 1 (orchestration 3.1, step 5). Prints a
one-line summary per tool. Exit 1 when the cycle must be short, 0 otherwise, 2 on a tool crash.
Both tools run with PYTHONIOENCODING=utf-8 so Korean survives the pipe on Windows.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(name, args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    t = time.time()
    r = subprocess.run([sys.executable, str(HERE / name), *args, "--json"], capture_output=True, env=env)
    took = round(time.time() - t, 2)
    text = r.stdout.decode("utf-8", "replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"error": (text + r.stderr.decode("utf-8", "replace")).strip()}
    return {"exit": r.returncode, "seconds": took, "result": data}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("plan")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode")
    ap.add_argument("--band")
    ap.add_argument("--house")
    a = ap.parse_args()
    common = [a.plan] + (["--band", a.band] if a.band else [])
    timing = run("timing.py", common + (["--mode", a.mode] if a.mode else []))
    lint = run("lint.py", common + (["--house", a.house] if a.house else []))
    gate = {"plan": a.plan, "timing": timing, "lint": lint,
            "short_cycle": timing["exit"] == 1 or lint["exit"] == 1}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(gate, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    t = timing["result"]
    if "error" in t:
        print(f"timing: crashed ({timing['seconds']} s): {t['error'][:200]}")
    else:
        print(f"timing: {t['timing']['status']} · longest passive {t['longest_passive']['min']:g} min "
              f"{' '.join(t['longest_passive']['segments'])} · failures {len(t['failures'])} ({timing['seconds']} s)")
    s = lint["result"].get("stats", {})
    if "error" in lint["result"]:
        print(f"lint: crashed ({lint['seconds']} s): {lint['result']['error'][:200]}")
    else:
        print(f"lint: {s.get('sev1', 0)} sev-1, {s.get('sev2', 0)} sev-2 · needs fact {s.get('needs_fact', 0)} "
              f"· forbidden {', '.join(s.get('forbidden_words', [])) or '-'} ({lint['seconds']} s)")
    print("short cycle" if gate["short_cycle"] else "gate passed")
    if timing["exit"] not in (0, 1) or lint["exit"] not in (0, 1):
        sys.exit(2)
    sys.exit(1 if gate["short_cycle"] else 0)


if __name__ == "__main__":
    main()
