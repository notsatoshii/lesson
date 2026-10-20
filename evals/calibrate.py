#!/usr/bin/env python3
"""Owner labels on critic findings, and per-critic precision against them.

Usage:
  python evals/calibrate.py add <labels.txt | -> [--root <project dir>] [--model <name>]
  python evals/calibrate.py add --line "<label line>" [--line ...] [--root <project dir>]
  python evals/calibrate.py report [--threshold 0.8] [--min 5] [--json] [--examples]

A label line (one per finding, see taste/calibration.md):

  <slug>/c<cycle>-<critic NN>-<k> valid
  <slug>/c<cycle>-<critic NN>-<k> invalid: <optional note>
  <slug>/c<cycle>-<critic NN>-<k> sev <1|2|3>: <optional note>     (right finding, wrong severity)

  mail-triage-1/c2-05-03 invalid: the brief allows a timer here

`k` is the finding's 1-based position in docs/lessons/<slug>/history/cycle-<N>/critic-<NN>.json.
With --root (the project that holds docs/lessons/), `add` copies the finding's severity, location
and issue from that file into the entry. Blank lines and lines starting with # are ignored. A new
label for an id replaces the old one.

`report` prints, per critic: labels, valid / invalid / wrong severity, precision (valid / all) and
location precision ((valid + wrong severity) / all), and lists critics under the threshold that
have at least --min labels. Entries marked "example": true are ignored unless --examples.
Exit 1 when a critic with enough labels is under the threshold, so a rubric edit can be gated on it.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

EVALS = Path(__file__).resolve().parent
SKILL = EVALS.parent
DEFAULT_FILE = EVALS / "calibration.json"
LINE = re.compile(
    r"^\s*(?P<slug>[\w.-]+)/c(?P<cycle>\d+)-(?P<critic>\d{2})-(?P<k>\d+)\s+"
    r"(?P<label>valid|invalid|(?:sev|severity|wrong-severity)\s*(?P<sev>[123]))\s*(?::\s*(?P<note>.*))?$",
    re.I,
)


def load(path):
    if not path.exists():
        return {"schema": "lesson-calibration/1", "threshold": 0.8, "min_labels": 5, "entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def critic_name(nn):
    hit = sorted((SKILL / "critics").glob(f"{nn}-*.md"))
    return hit[0].stem if hit else nn


def rubric_rev(nn):
    """Short git hash of the last commit that touched this critic's rubric, or '' without git."""
    hit = sorted((SKILL / "critics").glob(f"{nn}-*.md"))
    if not hit:
        return ""
    try:
        p = subprocess.run(["git", "-C", str(SKILL), "log", "-1", "--format=%h", "--", str(hit[0])],
                           capture_output=True, text=True, timeout=10)
        return p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def lookup(root, slug, cycle, nn, k):
    if not root:
        return None
    f = Path(root) / "docs" / "lessons" / slug / "history" / f"cycle-{cycle}" / f"critic-{nn}.json"
    if not f.exists():
        return None
    try:
        findings = json.loads(f.read_text(encoding="utf-8")).get("findings", [])
    except json.JSONDecodeError:
        return None
    return findings[k - 1] if 0 < k <= len(findings) else None


def parse_line(line):
    m = LINE.match(line)
    if not m:
        return None
    label = m.group("label").lower()
    if label.startswith(("sev", "wrong")):
        label, correct = "wrong-severity", int(m.group("sev"))
    else:
        correct = None
    return {
        "lesson": m.group("slug"), "cycle": int(m.group("cycle")), "critic_nn": m.group("critic"),
        "index": int(m.group("k")), "label": label, "correct_severity": correct, "note": (m.group("note") or "").strip(),
    }


def cmd_add(a):
    lines = list(a.line or [])
    if a.source:
        text = sys.stdin.read() if a.source == "-" else Path(a.source).read_text(encoding="utf-8-sig")
        lines += text.splitlines()
    data = load(a.file)
    by_id = {e["id"]: i for i, e in enumerate(data["entries"])}
    added, bad = 0, []
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        p = parse_line(raw)
        if not p:
            bad.append(raw)
            continue
        fid = f"{p['lesson']}/c{p['cycle']}-{p['critic_nn']}-{p['index']}"
        f = lookup(a.root, p["lesson"], p["cycle"], p["critic_nn"], p["index"])
        entry = {
            "id": fid, "lesson": p["lesson"], "cycle": p["cycle"], "critic": critic_name(p["critic_nn"]),
            "index": p["index"],
            "severity": f.get("severity") if f else None,
            "location": f.get("location", "") if f else "",
            "issue": f.get("issue", "") if f else "",
            "label": p["label"], "correct_severity": p["correct_severity"], "note": p["note"],
            "labelled": datetime.date.today().isoformat(),
            "rubric": rubric_rev(p["critic_nn"]), "model": a.model or "",
            "example": False,
        }
        if fid in by_id:
            old = data["entries"][by_id[fid]]
            if not f:  # relabel without the finding file: keep what was captured before
                for key in ("severity", "location", "issue"):
                    entry[key] = old.get(key, entry[key])
            entry["model"] = entry["model"] or old.get("model", "")
            data["entries"][by_id[fid]] = entry
        else:
            by_id[fid] = len(data["entries"])
            data["entries"].append(entry)
        added += 1
    save(a.file, data)
    out = [f"{added} label(s) recorded in {a.file}"]
    out += [f"skipped (not a label line): {b}" for b in bad]
    sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
    sys.exit(1 if bad else 0)


def cmd_report(a):
    data = load(a.file)
    threshold = a.threshold if a.threshold is not None else data.get("threshold", 0.8)
    min_n = a.min if a.min is not None else data.get("min_labels", 5)
    rows = defaultdict(lambda: {"n": 0, "valid": 0, "invalid": 0, "wrong-severity": 0, "rubrics": set()})
    for e in data.get("entries", []):
        if e.get("example") and not a.examples:
            continue
        r = rows[e["critic"]]
        r["n"] += 1
        r[e["label"]] += 1
        if e.get("rubric"):
            r["rubrics"].add(e["rubric"])
    table, under = [], []
    for critic in sorted(rows):
        r = rows[critic]
        prec = r["valid"] / r["n"]
        loc = (r["valid"] + r["wrong-severity"]) / r["n"]
        enough = r["n"] >= min_n
        flag = enough and prec < threshold
        if flag:
            under.append(critic)
        table.append({"critic": critic, "labels": r["n"], "valid": r["valid"], "invalid": r["invalid"],
                      "wrong_severity": r["wrong-severity"], "precision": round(prec, 3),
                      "location_precision": round(loc, 3), "enough_labels": enough, "under_threshold": flag,
                      "rubric_revisions": sorted(r["rubrics"])})
    if a.json:
        out = json.dumps({"threshold": threshold, "min_labels": min_n, "critics": table, "under": under},
                         ensure_ascii=False, indent=1)
    else:
        lines = [f"threshold {threshold:.0%} · min {min_n} labels per critic · file {a.file}"]
        if not table:
            lines.append("no labels yet" + ("" if a.examples else " (examples ignored; --examples to include them)"))
        for t in table:
            note = "" if t["enough_labels"] else f"  (fewer than {min_n} labels, not judged)"
            mixed = f"  (labels span rubric revisions {', '.join(t['rubric_revisions'])})" if len(t["rubric_revisions"]) > 1 else ""
            lines.append(f"{t['critic']:<20} {t['labels']:>3} labels · valid {t['valid']} · invalid {t['invalid']} · "
                         f"wrong severity {t['wrong_severity']} · precision {t['precision']:.0%} · "
                         f"location {t['location_precision']:.0%}{' · UNDER' if t['under_threshold'] else ''}{note}{mixed}")
        lines.append("under threshold: " + (", ".join(under) if under else "none"))
        if under:
            lines.append("next: rewrite those critics' Checks and anchors (critics/NN-*.md, critics/examples/), not the loop; re-label after.")
        out = "\n".join(lines)
    sys.stdout.buffer.write((out + "\n").encode("utf-8"))
    sys.exit(1 if under else 0)


def main():
    ap = argparse.ArgumentParser(description="Owner labels on critic findings and per-critic precision.")
    ap.add_argument("--file", type=Path, default=DEFAULT_FILE, help="calibration file (default evals/calibration.json)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ad = sub.add_parser("add", help="record label lines")
    ad.add_argument("source", nargs="?", help="a text file of label lines, or - for stdin")
    ad.add_argument("--line", action="append", help="one label line (repeatable)")
    ad.add_argument("--root", help="project folder that holds docs/lessons/, to copy each finding's text")
    ad.add_argument("--model", help="model that ran the critics, recorded with each label")
    rp = sub.add_parser("report", help="per-critic precision")
    rp.add_argument("--threshold", type=float)
    rp.add_argument("--min", type=int)
    rp.add_argument("--json", action="store_true")
    rp.add_argument("--examples", action="store_true", help="include entries marked as examples")
    a = ap.parse_args()
    if a.cmd == "add" and not (a.source or a.line):
        ap.error("add needs a file, - or --line")
    (cmd_add if a.cmd == "add" else cmd_report)(a)


if __name__ == "__main__":
    main()
