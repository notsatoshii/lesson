#!/usr/bin/env python3
"""Phone-width screenshot plus callout lines for a media brief (Playwright).

Usage:
  python capture.py <url | file.html> --out shot.png [--width 390 --height 844] [--dpr 1]
                    [--select "css" [--label "..."] [--arrow]]... [--mask "css"]... [--mask-mode blur|paint]
                    [--click "css" | --fill "css=text" | --press Key]... [--wait 300] [--full-page] [--pad 6]
                    [--brief media/M2.md] [--highlight] [--json]

Opens the page in the installed Chrome (Playwright channel "chrome"; falls back to Edge, then to
Playwright's own Chromium), sets a phone viewport, runs the optional --click / --fill / --press steps
in the order given, hides private data (--mask), takes the screenshot and reads the bounding box of
every --select element. Each selected element becomes one numbered callout line in the format
highlight.py parses:

  1. box 24,180,342,48 · "제목을 입력하세요"

Coordinates are screenshot pixels (CSS pixels times --dpr), so highlight.py needs no --scale.
--label after a --select names that callout; --arrow after a --select points an arrow at the element
instead of drawing a box. --brief writes the lines into the brief's screenshot+highlights section
(replacing the old callouts list) and records how the shot was taken. --highlight then runs
highlight.py to write <shot>.hl.png. The callout lines are always printed; --json prints a report.

Masking happens in the page before the shot, so the raw PNG never holds the private data:
blur (default) sets a CSS blur on the element; paint uses Playwright's solid mask colour.
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent


class StepAction(argparse.Action):
    """--fill and --click append to one ordered list of page steps."""

    def __call__(self, parser, ns, value, option_string=None):
        steps = getattr(ns, "steps", None) or []
        steps.append((option_string.lstrip("-"), value))
        ns.steps = steps


class SelectAction(argparse.Action):
    """--select appends a callout; --label and --arrow modify the most recent one."""

    def __call__(self, parser, ns, value, option_string=None):
        items = getattr(ns, "callouts", None) or []
        if option_string == "--select":
            items.append({"css": value, "label": None, "kind": "box"})
        elif not items:
            parser.error(f"{option_string} must follow a --select")
        elif option_string == "--label":
            items[-1]["label"] = value
        elif option_string == "--arrow":
            items[-1]["kind"] = "arrow"
        ns.callouts = items


def to_url(target):
    if re.match(r"^[a-z][a-z0-9+.-]*://", target, re.I) or target.startswith("about:"):
        return target
    p = pathlib.Path(target).resolve()
    if not p.exists():
        sys.exit(f"capture.py: no such file or URL: {target}")
    return p.as_uri()


def launch(pw):
    errors = []
    for kw in ({"channel": "chrome"}, {"channel": "msedge"}, {}):
        try:
            return pw.chromium.launch(**kw), kw.get("channel", "chromium")
        except Exception as e:  # noqa: BLE001 - try the next browser
            errors.append(f"{kw.get('channel', 'chromium')}: {str(e).splitlines()[0]}")
    sys.exit("capture.py: no browser could start (install Chrome, or run `python -m playwright install chromium`)\n  "
             + "\n  ".join(errors))


def callout_line(n, c):
    if c["kind"] == "arrow":
        shape = f"arrow {c['x1']},{c['y1']} -> {c['x2']},{c['y2']}"
    else:
        shape = f"box {c['x']},{c['y']},{c['w']},{c['h']}"
    label = f' · "{c["label"]}"' if c.get("label") else ""
    return f"{n}. {shape}{label}"


def geometry(box, kind, pad, dpr, img_w, img_h):
    """CSS-pixel bounding box -> screenshot-pixel callout coordinates, clipped to the image."""
    x0 = max(0, (box["x"] - pad) * dpr)
    y0 = max(0, (box["y"] - pad) * dpr)
    x1 = min(img_w, (box["x"] + box["width"] + pad) * dpr)
    y1 = min(img_h, (box["y"] + box["height"] + pad) * dpr)
    g = {"x": round(x0), "y": round(y0), "w": round(x1 - x0), "h": round(y1 - y0)}
    if kind == "arrow":
        # tail below and right of the element, head on its bottom edge; flipped above when no room
        tx, ty = round((x0 + x1) / 2), round(y1)
        sy = ty + round(70 * dpr)
        if sy > img_h - 10:
            ty = round(y0)
            sy = max(10, ty - round(70 * dpr))
        sx = min(img_w - 10, tx + round(50 * dpr))
        g.update({"x1": sx, "y1": sy, "x2": tx, "y2": ty})
    return g


def section_bounds(rows):
    sec = None
    for i, r in enumerate(rows):
        if re.match(r"^\s*#{1,6}\s*.*screenshot\s*\+\s*highlights", r, re.I):
            sec = i
            break
    if sec is None:
        return None, None
    level = len(re.match(r"^\s*(#+)", rows[sec]).group(1))
    for j in range(sec + 1, len(rows)):
        m = re.match(r"^\s*(#+)\s", rows[j])
        if m and len(m.group(1)) <= level:
            return sec, j
    return sec, len(rows)


def update_brief(path, lines, note):
    """Replace the callouts list in the brief's screenshot+highlights section; add or refresh a captured line."""
    p = pathlib.Path(path)
    text = p.read_text(encoding="utf-8")
    rows = text.splitlines()
    sec, end = section_bounds(rows)
    if sec is None:
        rows += ["", "### screenshot+highlights", "- callouts (numbered, in order of action):"]
        sec, end = section_bounds(rows)
    head = next((j for j in range(sec + 1, end) if re.match(r"^\s*[-*]\s*callouts\b", rows[j], re.I)), None)
    if head is None:
        rows.insert(end, "- callouts (numbered, in order of action):")
        head, end = end, end + 1
    j = head + 1  # drop the old numbered lines (and the template's "…" line) under the callouts bullet
    while j < end and (re.match(r"^\s+\d+[.)]\s", rows[j]) or rows[j].strip() in ("…", "...", "2. …")):
        j += 1
    new = ["  " + ln for ln in lines] or ["  (no callouts selected)"]
    rows[head + 1:j] = new
    end += len(new) - (j - head - 1)
    cap = next((k for k in range(sec + 1, end) if re.match(r"^\s*[-*]\s*captured\s*:", rows[k], re.I)), None)
    if cap is not None:
        rows[cap] = f"- captured: {note}"
    else:
        rows.insert(head + 1 + len(new), f"- captured: {note}")
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Phone-width screenshot plus callout lines for a media brief.")
    ap.add_argument("target", help="URL, or a local .html file")
    ap.add_argument("--out", required=True, help="screenshot path (.png)")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=844)
    ap.add_argument("--dpr", type=float, default=1, help="device pixel ratio (2 = sharper; coordinates double too)")
    ap.add_argument("--select", action=SelectAction, metavar="CSS", help="element to call out (repeatable, numbered in order)")
    ap.add_argument("--label", action=SelectAction, metavar="TEXT", help="label for the preceding --select")
    ap.add_argument("--arrow", action=SelectAction, nargs=0, help="the preceding --select gets an arrow, not a box")
    ap.add_argument("--mask", action="append", default=[], metavar="CSS", help="element(s) holding private data (repeatable)")
    ap.add_argument("--mask-mode", choices=["blur", "paint"], default="blur")
    ap.add_argument("--click", action=StepAction, metavar="CSS", help="click before the shot (repeatable; steps run in the order given)")
    ap.add_argument("--fill", action=StepAction, metavar="CSS=TEXT", help="type into a field before the shot (repeatable)")
    ap.add_argument("--press", action=StepAction, metavar="KEY", help="press a key, e.g. Enter (repeatable)")
    ap.add_argument("--wait", type=int, default=300, help="ms to wait after load and after each step")
    ap.add_argument("--full-page", action="store_true")
    ap.add_argument("--pad", type=int, default=6, help="CSS px added around each selected element")
    ap.add_argument("--dark", action="store_true", help="emulate prefers-color-scheme: dark")
    ap.add_argument("--lang", default="ko-KR", help="browser locale (default ko-KR)")
    ap.add_argument("--brief", help="media brief to write the callouts into")
    ap.add_argument("--highlight", action="store_true", help="run highlight.py afterwards (writes <shot>.hl.png)")
    ap.add_argument("--json", action="store_true", help="print a JSON report instead of the bare lines")
    a = ap.parse_args()
    callouts = getattr(a, "callouts", None) or []

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("capture.py: needs Playwright: pip install playwright (uses the installed Chrome; no browser download needed)")

    url = to_url(a.target)
    out = pathlib.Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    warnings = []
    with sync_playwright() as pw:
        browser, used = launch(pw)
        ctx = browser.new_context(viewport={"width": a.width, "height": a.height}, device_scale_factor=a.dpr,
                                  is_mobile=True, has_touch=True, locale=a.lang,
                                  color_scheme="dark" if a.dark else "light")
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(a.wait)
        for kind, val in getattr(a, "steps", None) or []:
            try:
                if kind == "click":
                    page.locator(val).first.click(timeout=8000)
                elif kind == "fill":
                    css, _, text = val.partition("=")
                    page.locator(css).first.fill(text, timeout=8000)
                else:
                    page.keyboard.press(val)
            except Exception as e:  # noqa: BLE001 - report the failed step, keep the run
                sys.exit(f"capture.py: step --{kind} {val!r} failed: {str(e).splitlines()[0]}")
            page.wait_for_timeout(a.wait)
        masked, paint = [], []
        for css in a.mask:
            loc = page.locator(css)
            n = loc.count()
            if not n:
                warnings.append(f"mask matched nothing: {css}")
                continue
            masked.append({"css": css, "count": n})
            if a.mask_mode == "paint":
                paint.append(loc)
            else:
                loc.evaluate_all("els => els.forEach(e => { e.style.filter = 'blur(9px)'; })")
        page.wait_for_timeout(100)
        boxes = []
        for c in callouts:
            loc = page.locator(c["css"])
            n = loc.count()
            if not n:
                warnings.append(f"select matched nothing, skipped: {c['css']}")
                boxes.append(None)
                continue
            if n > 1:
                warnings.append(f"select matched {n} elements, using the first: {c['css']}")
            if not a.full_page:
                loc.first.scroll_into_view_if_needed()
            box = loc.first.bounding_box()
            if box and a.full_page:
                box = {**box, "y": box["y"] + page.evaluate("window.scrollY"),
                       "x": box["x"] + page.evaluate("window.scrollX")}
            boxes.append(box)
        page.screenshot(path=str(out), full_page=a.full_page, mask=paint or None, mask_color="#9AA0A6")
        if a.full_page:
            css_w, css_h = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
        else:
            css_w, css_h = a.width, a.height
        img_w, img_h = round(css_w * a.dpr), round(css_h * a.dpr)
        browser.close()

    rows, lines = [], []
    for c, b in zip(callouts, boxes):
        if b is None:
            continue
        g = geometry(b, c["kind"], a.pad, a.dpr, img_w, img_h)
        if g["w"] <= 0 or g["h"] <= 0:
            warnings.append(f"element is outside the screenshot, skipped: {c['css']}")
            continue
        row = {"n": len(rows) + 1, "css": c["css"], "kind": c["kind"], "label": c["label"], **g}
        rows.append(row)
        lines.append(callout_line(row["n"], row))
    if len(rows) > 3:
        warnings.append(f"{len(rows)} callouts on one screenshot; the brief allows three, split it into two shots")

    note = (f"{a.target} · {a.width}x{a.height} dpr {a.dpr:g} · {datetime.date.today().isoformat()} · tool: capture.py"
            + (f" · masked {sum(m['count'] for m in masked)} element(s)" if masked else ""))
    if a.brief:
        update_brief(a.brief, lines, note)
    hl = None
    if a.highlight:
        cmd = [sys.executable, str(HERE / "highlight.py"), str(out)]
        if a.dpr and a.dpr != 1:  # a 2x shot needs 2x strokes, badges and labels or they look thin
            cmd += ["--size", f"{a.dpr:g}"]
        if a.brief:
            cmd += ["--spec", a.brief]
        else:
            for r in rows:
                lab = f',"{r["label"]}"' if r["label"] else ""
                cmd += (["--arrow", f"{r['x1']},{r['y1']},{r['x2']},{r['y2']}{lab}"] if r["kind"] == "arrow"
                        else ["--box", f"{r['x']},{r['y']},{r['w']},{r['h']}{lab}"])
        res = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, timeout=300)
        if res.returncode:
            warnings.append("highlight.py failed: " + res.stderr.decode("utf-8", "replace").strip()[-300:])
        else:
            hl = json.loads(res.stdout.decode("utf-8")).get("out")

    if a.json:
        report = {"url": url, "out": str(out), "size": [img_w, img_h], "browser": used, "callouts": rows,
                  "lines": lines, "masked": masked, "brief": a.brief, "highlighted": hl, "warnings": warnings}
        sys.stdout.buffer.write((json.dumps(report, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    else:
        text = "\n".join(lines + [f"warn: {w}" for w in warnings] + ([f"highlighted: {hl}"] if hl else []))
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
