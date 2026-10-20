#!/usr/bin/env python3
"""Timing and attention check of a lesson plan (stdlib only).

Usage: python timing.py <plan.md> [--mode live|online|video|guide|talk] [--band A..G] [--json]

Reads the plan's header line (total, mode, age band, optional "buffer: N %") and its Segments table, then reports: segment
minutes against the total and the mode buffer, active vs passive minutes, the longest passive
stretch and the longest segment against the age-band caps, beats present and missing, and how
many segments use each channel. Exit 1 when a check fails so a loop can gate on it. The editor
still reads the plan; this gives it numbers to point at.
"""
import argparse
import json
import re
import sys

BUFFER = {"live": 0.10, "talk": 0.05, "online": 0.0, "video": 0.0, "guide": 0.0}
# mirrors taste/age-bands.md: longest passive stretch / longest single segment, in minutes
CAPS = {"A": (3, 8), "B": (5, 12), "C": (7, 15), "D": (10, 20), "E": (12, 20), "F": (15, 25), "G": (10, 15)}
# active : passive floor from the same file (2:1 in A-C, 1:1 from D up); reported as a warning only
RATIO_FLOOR = {"A": 2.0, "B": 2.0, "C": 2.0, "D": 1.0, "E": 1.0, "F": 1.0, "G": 1.0}
BEATS = ["hook", "learn", "try", "apply", "check", "reward"]
# "open": a break, free talk or Q&A the learners lead. Neither active nor passive: it ends a passive
# stretch, is exempt from the single-segment cap, and is reported on its own line.
OPEN_BEATS = {"open"}
ACTIVE_BEATS = {"try", "apply", "check"}
CHANNELS = ["do", "see", "read", "listen"]
TOLERANCE = 1.0  # minutes of slack on the total before OVER / UNDER fails


def clean(cell):
    return re.sub(r"\*\*|__|`", "", cell).strip()


def num(text):
    m = re.search(r"\d+(?:[.,]\d+)?", text or "")
    return float(m.group(0).replace(",", ".")) if m else None


def fmt(n):
    return str(int(n)) if float(n).is_integer() else f"{n:.1f}"


def parse_header(text):
    head = {"total": None, "mode": None, "band": None, "buffer": None}
    for line in text.splitlines():
        m = re.search(r"total\s*:\s*\**\s*(\d+)\s*\**\s*min", line, re.I)
        if not m:
            continue
        head["total"] = int(m.group(1))
        m = re.search(r"\bmode\s*:\s*\**\s*([a-z]+)", line, re.I)
        if m and m.group(1).lower() in BUFFER:
            head["mode"] = m.group(1).lower()
        m = re.search(r"\bband\s*:\s*\**\s*([A-G])\b", line, re.I)
        if m:
            head["band"] = m.group(1).upper()
        # "buffer: 0 %" overrides the mode default, for a fixed program rhythm with no slack
        m = re.search(r"\bbuffer\s*:\s*\**\s*(\d+(?:\.\d+)?)\s*%", line, re.I)
        if m:
            head["buffer"] = float(m.group(1)) / 100
        break
    return head


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [clean(c) for c in line.split("|")]


def is_separator(line):
    return re.match(r"^\s*\|[\s:\-|]+\|?\s*$", line) is not None


def modalities_of(cell):
    tokens = re.split(r"[·/,+\s]+", cell.lower())
    return [c for c in CHANNELS if c in tokens]


def parse_segments(text):
    lines = text.splitlines()
    segs, warnings = [], []
    header = None
    for i, line in enumerate(lines):
        if not re.match(r"^\s*\|\s*\**\s*S\d+\b", line):
            continue
        if header is None:
            header = []
            for j in range(i - 1, max(-1, i - 6), -1):
                if lines[j].strip().startswith("|") and not is_separator(lines[j]):
                    header = [c.lower() for c in split_row(lines[j])]
                    break
        cells = split_row(line)
        col = {name: k for k, name in enumerate(header)}

        def cell(name, default_idx):
            k = col.get(name, default_idx)
            return cells[k] if k < len(cells) else ""

        seg_id = cells[0].upper()
        minutes = num(cell("min", 1))
        beat_cell = cell("beat", 2)
        beat = (re.split(r"[\s(/·]+", beat_cell.lower().strip()) or [""])[0]
        title = cell("title", 3)
        mod_idx = next((k for k, name in enumerate(header) if "modalit" in name), None)
        mod_cell = None
        if mod_idx is not None and mod_idx < len(cells):
            mod_cell = cells[mod_idx]
        else:  # no header match: take the first cell that reads like a channel list
            for c in cells[4:]:
                if modalities_of(c):
                    mod_cell = c
                    break
        mods = modalities_of(mod_cell or "")
        if minutes is None:
            warnings.append(f"{seg_id}: no minutes found, counted as 0")
            minutes = 0.0
        if beat not in BEATS and beat not in OPEN_BEATS:
            warnings.append(f"{seg_id}: beat '{beat_cell}' is not one of {', '.join(BEATS)}")
        if not mods and beat not in OPEN_BEATS:
            warnings.append(f"{seg_id}: no modalities cell (do/see/read/listen), treated as passive")
        is_open = beat in OPEN_BEATS
        active = not is_open and ("do" in mods or beat in ACTIVE_BEATS)
        segs.append({"id": seg_id, "min": minutes, "beat": beat, "title": title, "modalities": mods,
                     "active": active, "open": is_open})
    return segs, warnings


def longest_passive(segs):
    best, cur = (0.0, []), (0.0, [])
    for s in segs + [None]:
        if s is None or s["active"] or s["open"]:
            if cur[0] > best[0]:
                best = cur
            cur = (0.0, [])
        else:
            cur = (cur[0] + s["min"], cur[1] + [s["id"]])
    return best


def analyse(text, mode=None, band=None):
    head = parse_header(text)
    mode = mode or head["mode"]
    band = band or head["band"]
    segs, warnings = parse_segments(text)
    failures = []
    if not segs:
        failures.append("no segment rows found (rows must start with '| S1 |')")
    if head["total"] is None:
        warnings.append("no 'total: N min' in the header line")
    if mode is None:
        warnings.append("mode unknown (header or --mode); buffer 0 assumed")
    if band is None:
        warnings.append("age band unknown (header or --band); band caps not checked")

    total = head["total"]
    buf = head["buffer"] if head["buffer"] is not None else BUFFER.get(mode or "", 0.0)
    budget = round(total * (1 - buf), 1) if total else None
    s_sum = sum(s["min"] for s in segs)
    timing = {"sum": s_sum, "total": total, "mode": mode, "buffer_pct": int(buf * 100), "budget": budget}
    if budget is not None:
        diff = s_sum - budget
        if abs(diff) <= 0.5:
            timing["status"] = "OK"
        elif diff > 0:
            timing["status"] = f"OVER by {fmt(diff)}"
        else:
            timing["status"] = f"UNDER by {fmt(-diff)}"
        if abs(diff) > TOLERANCE:
            failures.append(
                f"segments sum to {fmt(s_sum)} min, budget is {fmt(budget)} "
                f"({total} min minus {int(buf * 100)} % {mode or ''} buffer): {timing['status']}"
            )
    else:
        timing["status"] = "unknown"

    active = sum(s["min"] for s in segs if s["active"])
    open_min = sum(s["min"] for s in segs if s["open"])
    passive = s_sum - active - open_min
    ratio = round(active / passive, 2) if passive else None
    stretch_min, stretch_ids = longest_passive(segs)
    capped = [s for s in segs if not s["open"]]
    longest_seg = max(capped, key=lambda s: s["min"]) if capped else None

    caps = CAPS.get(band or "")
    if caps:
        cap_passive, cap_seg = caps
        if stretch_min > cap_passive:
            failures.append(
                f"longest passive stretch {fmt(stretch_min)} min ({' '.join(stretch_ids)}) "
                f"is over the band {band} cap of {cap_passive} min"
            )
        if longest_seg and longest_seg["min"] > cap_seg:
            failures.append(
                f"longest segment {longest_seg['id']} is {fmt(longest_seg['min'])} min, "
                f"over the band {band} cap of {cap_seg} min"
            )
        floor = RATIO_FLOOR[band]
        if passive and (ratio or 0) < floor:
            warnings.append(f"active:passive {fmt(active)}:{fmt(passive)} is under the band {band} floor of {floor:g}:1")

    present = [b for b in BEATS if any(s["beat"] == b for s in segs)]
    missing = [b for b in BEATS if b not in present]
    if missing:
        warnings.append(f"beats missing: {', '.join(missing)}")
    coverage = {c: sum(1 for s in segs if c in s["modalities"]) for c in CHANNELS}

    return {
        "ok": not failures,
        "mode": mode,
        "band": band,
        "timing": timing,
        "active_min": active,
        "open_min": open_min,
        "passive_min": passive,
        "active_to_passive": ratio,
        "longest_passive": {"min": stretch_min, "segments": stretch_ids, "cap": caps[0] if caps else None},
        "longest_segment": (
            {"id": longest_seg["id"], "min": longest_seg["min"], "cap": caps[1] if caps else None} if longest_seg else None
        ),
        "beats": {"present": present, "missing": missing},
        "channels": coverage,
        "segments": segs,
        "failures": failures,
        "warnings": warnings,
    }


def report(r):
    t = r["timing"]
    budget = fmt(t["budget"]) if t["budget"] is not None else "?"
    lines = [
        f"mode {r['mode'] or '?'} · band {r['band'] or '?'} · {len(r['segments'])} segments",
        f"timing: {fmt(t['sum'])} min of {budget} budget ({t['total'] or '?'} total, {t['buffer_pct']} % buffer) -> {t['status']}",
    ]
    ratio = f"{r['active_to_passive']}:1" if r["active_to_passive"] is not None else "all active"
    open_part = f" / open {fmt(r['open_min'])}" if r["open_min"] else ""
    lines.append(f"active {fmt(r['active_min'])} / passive {fmt(r['passive_min'])}{open_part} min ({ratio})")
    lp = r["longest_passive"]
    cap = f" (cap {lp['cap']})" if lp["cap"] else ""
    lines.append(f"longest passive stretch: {fmt(lp['min'])} min {' '.join(lp['segments']) or '-'}{cap}")
    ls = r["longest_segment"]
    if ls:
        cap = f" (cap {ls['cap']})" if ls["cap"] else ""
        lines.append(f"longest segment: {ls['id']} {fmt(ls['min'])} min{cap}")
    b = r["beats"]
    lines.append(f"beats: {' '.join(b['present']) or '-'}" + (f" · missing: {' '.join(b['missing'])}" if b["missing"] else ""))
    lines.append("channels: " + " · ".join(f"{c} {n}" for c, n in r["channels"].items()))
    for w in r["warnings"]:
        lines.append(f"warn: {w}")
    for f in r["failures"]:
        lines.append(f"FAIL: {f}")
    lines.append("OK" if r["ok"] else f"{len(r['failures'])} check(s) failed")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--mode", choices=sorted(BUFFER))
    ap.add_argument("--band", type=str.upper, choices=sorted(CAPS))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.plan, encoding="utf-8") as f:
        text = f.read()
    r = analyse(text, a.mode, a.band)
    if a.json:
        out = json.dumps(r, ensure_ascii=False, indent=1) + "\n"
    else:
        out = report(r) + "\n"
    sys.stdout.buffer.write(out.encode("utf-8"))
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
