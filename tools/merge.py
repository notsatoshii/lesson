#!/usr/bin/env python3
"""Merge one cycle's critic files into a ranked list (stdlib only): orchestration 3.3, the mechanical part.

Usage: python merge.py <history/cycle-N> [--gate gate.json] [--out ranked.json] [--md ranked.md]

Reads every critic-NN.json in the folder (a ```json fence around the block is tolerated and
reported), validates each (checks, anchor_quoted, weakest, every finding located), maps the blind
comparison back with compare/map.json (better = both reads of the outcome question pick the current
plan and the house-rules question does not pick the previous one in both; worse = both reads of
either question pick the previous plan; else same), adds the gate's severity-1 lint lines as critic
01 findings, gives every finding its id c<N>-<NN>-<k>, ranks by severity, then the number of critics
naming the same segment, then critic number, and lists candidate duplicates (same segment or media
id named by two or more critics) for the orchestrator to merge by judgement. Prints a summary;
exit 1 when a critic file is invalid (re-run that critic once).
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def load(path):
    text = path.read_text(encoding="utf-8-sig").strip()
    fenced = text.startswith("```")
    if fenced:
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    return json.loads(text), fenced


def segs(location):
    return sorted(set(re.findall(r"\b([SM]\d+)\b", location or "")))


def verdict(comp, current):
    if not comp or comp.get("n/a"):
        return "n/a"
    prev = "B" if current == "A" else "A"
    o = comp.get("outcome", {})
    h = comp.get("house_rules", {})
    reads_o = (o.get("first_read"), o.get("second_read"))
    reads_h = (h.get("first_read"), h.get("second_read"))
    if reads_o == (prev, prev) or reads_h == (prev, prev):
        return "worse"
    if reads_o == (current, current) and reads_h != (prev, prev):
        return "better"
    return "same"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder")
    ap.add_argument("--gate")
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    folder = Path(a.folder)
    n = re.search(r"cycle-(\d+)", str(folder.resolve()))
    cycle = int(n.group(1)) if n else 0
    current = None
    mp = folder / "compare" / "map.json"
    if mp.is_file():
        m = json.loads(mp.read_text(encoding="utf-8"))
        current = next((k for k, v in m.items() if v == f"cycle-{cycle}"), None)

    critics, findings, invalid = [], [], []
    for p in sorted(folder.glob("critic-*.json")):
        num = re.search(r"critic-(\d+)", p.name).group(1)
        try:
            d, fenced = load(p)
        except json.JSONDecodeError as e:
            invalid.append(f"{p.name}: not JSON ({e})")
            continue
        problems = []
        if not d.get("checks"):
            problems.append("no checks")
        if not d.get("anchor_quoted"):
            problems.append("no anchor_quoted")
        if not d.get("weakest"):
            problems.append("no weakest")
        for f in d.get("findings", []):
            if not (f.get("location") or "").strip():
                problems.append("a finding without location")
        if problems:
            invalid.append(f"{p.name}: " + ", ".join(problems))
        checks = d.get("checks", [])
        sev = [f.get("severity") for f in d.get("findings", [])]
        critics.append({
            "critic": num, "name": d.get("critic"), "run": d.get("run"), "score": d.get("score"),
            "fenced": fenced, "comparison": verdict(d.get("comparison"), current) if current else "n/a",
            "checks": {r: sum(1 for c in checks if c.get("result") == r) for r in ("pass", "fail", "n/a")},
            "sev": {s: sev.count(s) for s in (1, 2, 3)}, "anchor": d.get("anchor_quoted", ""),
            "weakest": d.get("weakest", {}),
            "closure": d.get("closure", []), "decisions": d.get("decisions", []),
            "proposed_rewrites": d.get("proposed_rewrites", []), "ideas": d.get("ideas", []),
        })
        for k, f in enumerate(d.get("findings", []), 1):
            findings.append({"id": f"c{cycle}-{num}-{k}", "critic": num, **f})

    if a.gate and Path(a.gate).is_file():
        g = json.loads(Path(a.gate).read_text(encoding="utf-8"))
        for k, f in enumerate([f for f in g.get("lint", {}).get("result", {}).get("findings", []) if f.get("severity") == 1], 1):
            findings.append({"id": f"c{cycle}-lint-{k}", "critic": "01", "severity": 1, "location": f.get("location"),
                             "issue": f.get("issue"), "fix": f.get("fix"), "source": "lint"})

    by_seg = defaultdict(set)
    for f in findings:
        for s in segs(f.get("location")):
            by_seg[s].add(f["critic"])
    for f in findings:
        f["votes_hint"] = max([len(by_seg[s]) for s in segs(f.get("location"))] or [1])
    findings.sort(key=lambda f: (f.get("severity", 3), -f["votes_hint"], f["critic"]))
    dupes = {s: sorted(c) for s, c in sorted(by_seg.items()) if len(c) > 1}

    out = {"cycle": cycle, "current_letter": current, "critics": critics, "findings": findings,
           "candidate_duplicates": dupes, "invalid": invalid}
    if a.out:
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.md:
        lines = [f"# Cycle {cycle} · merged findings (mechanical)", "",
                 "| critic | run | score | checks p/f/na | sev 1/2/3 | comparison | weakest |", "|---|---|---|---|---|---|---|"]
        for c in critics:
            ch, sv, w = c["checks"], c["sev"], c["weakest"]
            lines.append(f"| {c['name'] or c['critic']} | {c['run']} | {c['score']} | {ch['pass']}/{ch['fail']}/{ch['n/a']} | "
                         f"{sv[1]}/{sv[2]}/{sv[3]} | {c['comparison']} | {w.get('location', '')} · {w.get('why', '')} |")
        lines += ["", "## Findings, ranked", ""]
        for f in findings:
            lines.append(f"- **{f['id']}** · sev {f.get('severity')} · {f.get('location')}\n  - issue: {f.get('issue')}\n  - fix: {f.get('fix')}")
        lines += ["", "## Candidate duplicates (same segment, several critics)", ""]
        lines += [f"- {s}: critics {', '.join(c)}" for s, c in dupes.items()]
        Path(a.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    for c in critics:
        flag = " (fenced)" if c["fenced"] else ""
        print(f"{c['critic']} {c['name']}: score {c['score']} · sev1 {c['sev'][1]} sev2 {c['sev'][2]} sev3 {c['sev'][3]} · {c['comparison']}{flag}")
    print(f"findings {len(findings)} · sev1 {sum(f.get('severity') == 1 for f in findings)} · "
          f"sev2 {sum(f.get('severity') == 2 for f in findings)} · sev3 {sum(f.get('severity') == 3 for f in findings)}")
    for i in invalid:
        print(f"INVALID {i}")
    sys.exit(1 if invalid else 0)


if __name__ == "__main__":
    main()
