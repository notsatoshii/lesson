#!/usr/bin/env python3
"""Guide-mode plan -> step deck (Marp: PDF and phone PNGs) and an optional printable handout (Typst).

Usage:
  python guide.py <plan.md> --out guide.pdf [--png-dir dir] [--handout [handout.pdf]] [--steps S1,S2] [--json]

Reads the plan's title, header line and Segments table. Every segment row becomes one step, in table
order (--steps picks a subset). For each step:
  - headline = the segment detail's `- instruction: "..."` line (#### S<n> block); missing -> a visible
    [needs instruction: S<n>] placeholder and a warning
  - expected result = the `- expected: "..."` line (also read: `expected result:`, `result:`); missing
    -> the slide has no result line and a warning is printed
  - image = the highlighted screenshot of the segment's media id (media column, e.g. M2): a *.hl.png
    named in media/M2.md, else media/M2.hl.png, media/M2-*.hl.png, media/M2/*.hl.png, else any
    media/M2.png; missing -> a visible [needs media: M2] placeholder and a warning

Writes <out stem>.md (the Marp deck, editable and re-renderable) and <out stem>.theme.css beside the
PDF, renders the PDF with marp-cli, and with --png-dir one portrait PNG per slide (1080x1920).
--handout fills tools/templates/handout.typ (lang "ko", Malgun Gothic then Noto Sans KR, writing
lines under each step) and compiles an A4 PDF with Typst (default name <out stem>-handout.pdf).
Needs marp-cli (npm i -g @marp-team/marp-cli, or npx) and the installed Chrome or Edge; --handout
needs typst. Exit 1 when a render fails.
"""
import argparse
import glob
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "templates" / "handout.typ"
SLIDE_W, SLIDE_H, IMAGE_SCALE = 720, 1280, 1.5

THEME = """/* @theme lesson-guide */
/* One step per slide, phone portrait. Korean first; keep-all stops mid-word line breaks. */
section {
  width: %(w)dpx; height: %(h)dpx; box-sizing: border-box; padding: 56px 48px 48px;
  background: #FFFFFF; color: #1A1D21;
  font-family: "Malgun Gothic", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
  word-break: keep-all; overflow-wrap: break-word; line-height: 1.4;
  display: flex; flex-direction: column; justify-content: flex-start; gap: 22px;
}
section .num { font-size: 22px; font-weight: 700; color: #FF4D2E; letter-spacing: 0.02em; }
section h1 { font-size: 52px; line-height: 1.25; margin: 0; }
section h2 { font-size: 40px; line-height: 1.3; margin: 0; font-weight: 800; }
section .shot { flex: 1 1 auto; min-height: 0; display: flex; align-items: center; justify-content: center; }
section .shot img { max-width: 100%%; max-height: 100%%; object-fit: contain; border-radius: 18px;
  border: 1px solid #D9DCE1; box-shadow: 0 6px 24px rgba(26,29,33,0.10); }
section .missing { border: 3px dashed #C4C8CF; border-radius: 18px; padding: 40px; color: #6B7280; font-size: 26px; text-align: center; }
section .expect { font-size: 28px; background: #EEF7F1; color: #17633A; border-radius: 14px; padding: 18px 22px; }
section.title { justify-content: center; }
section.title .meta { font-size: 26px; color: #6B7280; }
"""


def out(obj):
    sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"“'" and s[-1] in "\"”'":
        s = s[1:-1]
    return s.replace('\\"', '"').strip()


def parse_plan(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    rows = text.splitlines()
    title = next((r[2:].strip() for r in rows if r.startswith("# ")), pathlib.Path(path).stem)
    header = {}
    meta_line = next((r for r in rows if re.match(r"^\s*slug\s*:", r, re.I)), "")
    for part in re.split(r"\s+·\s+", meta_line):
        k, _, v = part.partition(":")
        if v:
            header[k.strip().lower()] = v.strip()
    # Segments table: header row with an "id" column, then | S<n> | rows
    segs, cols = [], None
    for r in rows:
        if not r.strip().startswith("|"):
            continue
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        low = [c.lower() for c in cells]
        if "id" in low and ("beat" in low or "media" in low):
            cols = {name: low.index(name) for name in low}
            continue
        if cols and re.match(r"^S\d+[a-z]?$", cells[0]):
            get = lambda name, d="": cells[cols[name]] if name in cols and cols[name] < len(cells) else d  # noqa: E731
            segs.append({"id": cells[0], "title": get("title"), "beat": get("beat"), "min": get("min"),
                         "media": re.findall(r"\bM\d+[a-z]?\b", get("media"))})
    # Segment detail blocks
    details, cur = {}, None
    for r in rows:
        m = re.match(r"^#{3,5}\s+(S\d+[a-z]?)\b\s*(.*)$", r)
        if m:
            cur = details.setdefault(m.group(1), {"heading": m.group(2).strip()})
            continue
        if re.match(r"^#{1,5}\s", r):
            cur = None
            continue
        if cur is None:
            continue
        f = re.match(r"^\s*[-*]\s*(instruction|expected result|expected|result)\s*[:：]\s*(.+)$", r, re.I)
        if f:
            key = "instruction" if f.group(1).lower() == "instruction" else "expected"
            cur.setdefault(key, unquote(f.group(2)))
    return {"title": title, "header": header, "segments": segs, "details": details}


def find_image(plan_dir, media_ids):
    """Return (image path or None, media id used or None)."""
    media_dir = plan_dir / "media"
    for mid in media_ids:
        brief = media_dir / f"{mid}.md"
        if brief.exists():
            for tok in re.findall(r"[\w./\\:-]+\.hl\.png", brief.read_text(encoding="utf-8")):
                for base in (brief.parent, plan_dir):
                    p = (base / tok).resolve()
                    if p.exists():
                        return p, mid
        pats = [f"{mid}.hl.png", f"{mid}-*.hl.png", f"{mid}_*.hl.png", f"{mid}/*.hl.png"]
        for pat in pats:
            hits = sorted(glob.glob(str(media_dir / pat)))
            if hits:
                return pathlib.Path(hits[0]).resolve(), mid
    for mid in media_ids:  # no highlighted shot: fall back to a plain render (e.g. a diagram PNG)
        p = media_dir / f"{mid}.png"
        if p.exists():
            return p.resolve(), mid
    return None, (media_ids[0] if media_ids else None)


def build_steps(plan, plan_dir, only):
    steps, warnings = [], []
    segs = [s for s in plan["segments"] if not only or s["id"] in only]
    for n, s in enumerate(segs, 1):
        d = plan["details"].get(s["id"], {})
        instr = d.get("instruction")
        if not instr:
            warnings.append(f"{s['id']}: no '- instruction:' line in its segment detail")
        exp = d.get("expected")
        if not exp:
            warnings.append(f"{s['id']}: no '- expected:' line; the slide has no result line")
        img, mid = find_image(plan_dir, s["media"])
        if not img:
            warnings.append(f"{s['id']}: no image found for media {mid or '(none in the media column)'}")
        steps.append({"n": n, "id": s["id"], "title": d.get("heading") or s["title"],
                      "instruction": instr or f"[needs instruction: {s['id']}]", "expected": exp,
                      "image": str(img) if img else None, "media": mid,
                      "missing": f"[needs media: {mid}]" if mid else f"[needs media: {s['id']}]"})
    return steps, warnings


def meta_line(plan, n_steps):
    total = re.search(r"\d+", plan["header"].get("total", ""))
    return f"{n_steps}단계" + (f" · 약 {total.group(0)}분" if total else "")


def rel(path, start):
    try:
        return os.path.relpath(path, start).replace("\\", "/")
    except ValueError:  # different drive on Windows
        return pathlib.Path(path).as_uri()


def deck_markdown(plan, steps, deck_dir):
    e = html.escape
    parts = ["---", "marp: true", "theme: lesson-guide", "paginate: false", "lang: ko", f"title: {plan['title']}", "---", "",
             "<!-- _class: title -->", "", f"# {e(plan['title'])}", "", f'<div class="meta">{e(meta_line(plan, len(steps)))}</div>', ""]
    for s in steps:
        parts += ["---", "", f"<!-- _class: step -->", "", f'<div class="num">{s["n"]} / {len(steps)}</div>', "",
                  f"## {e(s['instruction'])}", ""]
        if s["image"]:
            parts += [f'<div class="shot"><img src="{e(rel(s["image"], deck_dir))}" alt=""></div>', ""]
        else:
            parts += [f'<div class="shot"><div class="missing">{e(s["missing"])}</div></div>', ""]
        if s["expected"]:
            parts += [f'<div class="expect">✓ {e(s["expected"])}</div>', ""]
    return "\n".join(parts)


def find_browser():
    for p in [os.environ.get("CHROME_PATH"),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]:
        if p and os.path.exists(p):
            return p
    return None


def marp_cmd():
    m = shutil.which("marp")
    if m:
        return [m]
    npx = shutil.which("npx")
    if npx:
        return [npx, "-y", "@marp-team/marp-cli@4.5.1"]
    sys.exit("guide.py: marp-cli not found; npm i -g @marp-team/marp-cli")


def find_typst():
    cands = [os.environ.get("TYPST"), shutil.which("typst")]
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        cands += sorted(glob.glob(os.path.join(local, "Microsoft", "WinGet", "Packages", "Typst.Typst*", "**", "typst.exe"), recursive=True))
        cands += [os.path.join(local, "typst", "typst.exe")]
    return next((c for c in cands if c and os.path.exists(c)), None)


def run(cmd, env=None):
    try:
        res = subprocess.run(cmd, capture_output=True, env=env, stdin=subprocess.DEVNULL, timeout=300)
    except subprocess.TimeoutExpired:
        return 1, f"timed out after 300 s: {' '.join(cmd[:3])}"
    return res.returncode, (res.stderr or res.stdout).decode("utf-8", "replace").strip()


def render_handout(plan, steps, dest):
    typst = find_typst()
    if not typst:
        return None, "typst not found (winget install --id Typst.Typst, or set TYPST to typst.exe)"
    with tempfile.TemporaryDirectory() as tmp:
        b = pathlib.Path(tmp)
        shutil.copy(TEMPLATE, b / "handout.typ")
        (b / "img").mkdir()
        data_steps = []
        for s in steps:
            img = None
            if s["image"]:
                img = f"img/{s['n']}{pathlib.Path(s['image']).suffix}"
                shutil.copy(s["image"], b / img)
            data_steps.append({"n": s["n"], "title": s["title"], "instruction": s["instruction"],
                               "expected": s["expected"], "image": img, "missing": s["missing"]})
        data = {"title": plan["title"], "meta": meta_line(plan, len(steps)), "steps": data_steps,
                "labels": {"notes": "메모"}, "lines": 4}
        (b / "handout.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        code, msg = run([typst, "compile", "--root", str(b), "--input", "data=handout.json", str(b / "handout.typ"), str(dest)])
    if code:
        return None, f"typst failed: {msg[-800:]}"
    return str(dest), None


def main():
    ap = argparse.ArgumentParser(description="Guide-mode plan to a step deck (PDF, phone PNGs) and a printable handout.")
    ap.add_argument("plan")
    ap.add_argument("--out", required=True, help="deck PDF path; the Marp source is written beside it as <stem>.md")
    ap.add_argument("--png-dir", help="also write one 1080x1920 PNG per slide here")
    ap.add_argument("--handout", nargs="?", const="", default=None, metavar="PDF", help="also build the Typst handout (default <stem>-handout.pdf)")
    ap.add_argument("--steps", help="comma-separated segment ids to include (default: every segment)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    plan_path = pathlib.Path(a.plan).resolve()
    plan = parse_plan(plan_path)
    warnings = []
    mode = plan["header"].get("mode", "")
    if mode and mode != "guide":
        warnings.append(f"plan mode is '{mode}', not guide; building the step deck anyway")
    only = {s.strip() for s in a.steps.split(",")} if a.steps else None
    steps, w = build_steps(plan, plan_path.parent, only)
    warnings += w
    if not steps:
        out({"ok": False, "error": "no segment rows (| S1 | ...) found in the plan's Segments table"})
        sys.exit(1)

    pdf = pathlib.Path(a.out).resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    deck = pdf.with_suffix(".md")
    theme = pdf.with_name(pdf.stem + ".theme.css")
    theme.write_text(THEME % {"w": SLIDE_W, "h": SLIDE_H}, encoding="utf-8")
    deck.write_text(deck_markdown(plan, steps, deck.parent), encoding="utf-8")

    env = dict(os.environ)
    browser = find_browser()
    if browser:
        env.setdefault("CHROME_PATH", browser)
    base = marp_cmd() + [str(deck), "--theme", str(theme), "--html", "--allow-local-files", "--no-stdin"]
    report = {"ok": True, "plan": str(plan_path), "deck": str(deck), "steps": [
        {k: s[k] for k in ("n", "id", "instruction", "expected", "media", "image")} for s in steps]}
    code, msg = run(base + ["--pdf", "-o", str(pdf)], env)
    if code or not pdf.exists():
        report.update(ok=False, error="marp PDF failed", detail=msg[-800:])
    else:
        report["pdf"] = str(pdf)
    if a.png_dir and report["ok"]:
        pdir = pathlib.Path(a.png_dir).resolve()
        pdir.mkdir(parents=True, exist_ok=True)
        code, msg = run(base + ["--images", "png", "--image-scale", str(IMAGE_SCALE), "-o", str(pdir / (pdf.stem + ".png"))], env)
        pngs = sorted(str(p) for p in pdir.glob(pdf.stem + "*.png"))
        if code or not pngs:
            report.update(ok=False, error="marp PNG failed", detail=msg[-800:])
        else:
            report["png"] = pngs
            report["png_px"] = [int(SLIDE_W * IMAGE_SCALE), int(SLIDE_H * IMAGE_SCALE)]
    if a.handout is not None:
        hpath = pathlib.Path(a.handout).resolve() if a.handout else pdf.with_name(pdf.stem + "-handout.pdf")
        done, err = render_handout(plan, steps, hpath)
        if err:
            report.update(ok=False, error=err)
        else:
            report["handout"] = done
    report["warnings"] = warnings
    if a.json or not report["ok"]:
        out(report)
    else:
        lines = [f"deck: {deck}", f"pdf: {report.get('pdf')}"]
        if report.get("png"):
            lines.append(f"png: {len(report['png'])} slides at {report['png_px'][0]}x{report['png_px'][1]} in {a.png_dir}")
        if report.get("handout"):
            lines.append(f"handout: {report['handout']}")
        lines += [f"warn: {x}" for x in warnings]
        sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
