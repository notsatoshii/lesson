#!/usr/bin/env python3
"""Score spread per critic across repeated runs of the control case.

Usage: python evals/spread.py <run dir> <run dir> [...] [--slug eval-control-clean] [--max 1]

Point it at the sandbox folders that `claude plugin eval . --case control-clean --keep-temp` prints
(one per run). It reads docs/lessons/<slug>/history/cycle-1/critic-*.json in each, collects each
critic's score, and flags any critic whose scores on the unchanged control differ by more than --max
points: its anchors are too vague to gate on. Exit 1 when a critic is flagged.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Per-critic score spread on the control across runs.")
    ap.add_argument("runs", nargs="+", help="run workspace folders kept with --keep-temp")
    ap.add_argument("--slug", default="eval-control-clean")
    ap.add_argument("--max", type=float, default=1.0, help="largest allowed max - min score per critic")
    a = ap.parse_args()

    scores, missing = defaultdict(list), []
    for run in a.runs:
        files = sorted(Path(run).rglob(f"docs/lessons/{a.slug}/history/cycle-1/critic-*.json"))
        if not files:
            missing.append(run)
        for f in files:
            try:
                s = json.loads(f.read_text(encoding="utf-8")).get("score")
            except json.JSONDecodeError:
                s = None
            if isinstance(s, (int, float)):
                scores[f.stem.replace("critic-", "")].append(s)
    lines, flagged = [], []
    for critic in sorted(scores):
        v = scores[critic]
        spread = max(v) - min(v)
        flag = len(v) > 1 and spread > a.max
        if flag:
            flagged.append(critic)
        lines.append(f"critic {critic}: {len(v)} runs · scores {', '.join(f'{x:g}' for x in v)} · spread {spread:g}"
                     + ("  FLAG: anchors too vague to gate on" if flag else ""))
    for m in missing:
        lines.append(f"warn: no critic files under {m}")
    if len(a.runs) < 3:
        lines.append("warn: fewer than three runs; the spread rule assumes three")
    lines.append("flagged: " + (", ".join(flagged) if flagged else "none"))
    sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
