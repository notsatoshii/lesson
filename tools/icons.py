#!/usr/bin/env python3
"""Fetch one-family icon sets from the Iconify API, cache them, and write SVG plus 2x PNG.

Usage:
  python icons.py fetch <family> <name>... [--color #2B2F36] [--size 48] [--out dir] [--lesson plan.md] [--switch]
  python icons.py search <family> <query> [--limit 20]
  python icons.py families

Families (Iconify prefix): lucide, ph (Phosphor), tabler, heroicons, iconoir, material-symbols, ri (Remix).
Aliases: phosphor = ph, remix = ri, material = material-symbols.

fetch downloads https://api.iconify.design/<prefix>/<name>.svg?color=<hex>&width=<size>&height=<size>,
caches the SVG in tools/.cache/icons/<prefix>/ (later runs work offline), and writes <name>.svg and
<name>@2x.png (size x 2 pixels, transparent) to --out (default: ./icons). PNG rendering uses resvg-py
when installed, else the installed Chrome through Playwright.

One family per lesson: with --lesson, the plan header must name the same family. If the header has
no `icon family:` field, it is added to the header line (`... · icon family: lucide`). If it names a
different family, the run is refused (exit 2); --switch rewrites the header to the new family and says
which icons must be refetched. Exit 1 when any icon is not found.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / ".cache" / "icons"
API = "https://api.iconify.design"
FAMILIES = {
    "lucide": "Lucide (ISC)",
    "ph": "Phosphor (MIT)",
    "tabler": "Tabler (MIT)",
    "heroicons": "Heroicons (MIT)",
    "iconoir": "Iconoir (MIT)",
    "material-symbols": "Material Symbols (Apache-2.0)",
    "ri": "Remix Icon (Apache-2.0)",
}
ALIASES = {"phosphor": "ph", "remix": "ri", "remixicon": "ri", "material": "material-symbols", "tabler-icons": "tabler"}
FAMILY_RE = re.compile(r"icon family\s*:\s*([A-Za-z0-9-]+)", re.I)


def out(obj):
    sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))


def family_prefix(name):
    p = ALIASES.get(name.lower(), name.lower())
    if p not in FAMILIES:
        sys.exit(f"icons.py: unknown family '{name}'. Use one of: {', '.join(FAMILIES)} (aliases: {', '.join(ALIASES)})")
    return p


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "lesson-skill-icons/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def fetch_svg(prefix, name, color, size):
    key = f"{name}-{color.lstrip('#').lower()}-{size}.svg"
    path = CACHE / prefix / key
    if path.exists():
        return path.read_text(encoding="utf-8"), "cache"
    q = urllib.parse.urlencode({"color": color, "width": size, "height": size})
    try:
        data = get(f"{API}/{prefix}/{urllib.parse.quote(name)}.svg?{q}").decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, "not found"
        raise
    if not data.lstrip().startswith("<svg"):
        return None, "not found"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")
    return data, "api"


def png_resvg(svg, px):
    import resvg_py
    return bytes(resvg_py.svg_to_bytes(svg_string=svg, width=px, height=px))


def png_chrome(jobs):
    """jobs: list of (svg, px, path). Renders each SVG in Chrome with a transparent background."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = None
        for kw in ({"channel": "chrome"}, {"channel": "msedge"}, {}):
            try:
                browser = pw.chromium.launch(**kw)
                break
            except Exception:  # noqa: BLE001
                continue
        if browser is None:
            raise RuntimeError("no browser for SVG to PNG; pip install resvg-py")
        page = browser.new_page(device_scale_factor=1)
        for svg, px, path in jobs:
            page.set_viewport_size({"width": px, "height": px})
            sized = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r"\1", svg, count=1)
            sized = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r"\1", sized, count=1)
            sized = sized.replace("<svg", f'<svg width="{px}" height="{px}"', 1)
            page.set_content(f"<html><body style='margin:0;background:transparent'>{sized}</body></html>")
            page.locator("svg").first.screenshot(path=str(path), omit_background=True)
        browser.close()


def plan_family(plan_path, prefix, switch):
    """Record or enforce `icon family:` in the plan header. Returns (status, previous)."""
    p = pathlib.Path(plan_path)
    text = p.read_text(encoding="utf-8")
    rows = text.splitlines()
    first_h2 = next((i for i, r in enumerate(rows) if r.startswith("## ")), len(rows))
    header = rows[:first_h2]
    hit = next(((i, m) for i, r in enumerate(header) if (m := FAMILY_RE.search(r))), None)
    if hit:
        i, m = hit
        prev = family_prefix(m.group(1)) if m.group(1).lower() in FAMILIES or m.group(1).lower() in ALIASES else m.group(1)
        if prev == prefix:
            return "matches", prev
        if not switch:
            return "refused", prev
        rows[i] = rows[i][:m.start(1)] + prefix + rows[i][m.end(1):]
        p.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return "switched", prev
    meta = next((i for i, r in enumerate(header) if re.match(r"^\s*slug\s*:", r, re.I)), None)
    if meta is not None:
        rows[meta] = rows[meta].rstrip() + f" · icon family: {prefix}"
    else:
        title = next((i for i, r in enumerate(header) if r.startswith("# ")), -1)
        rows[title + 1:title + 1] = ["", f"icon family: {prefix}"]
    p.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return "recorded", None


def cmd_fetch(a):
    prefix = family_prefix(a.family)
    color = a.color if a.color.startswith("#") else "#" + a.color
    if not re.fullmatch(r"#[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?", color):
        sys.exit(f"icons.py: --color must be a hex colour like #2B2F36, got {a.color}")
    family_note = None
    if a.lesson:
        status, prev = plan_family(a.lesson, prefix, a.switch)
        if status == "refused":
            out({"ok": False, "error": f"the lesson already uses icon family '{prev}'; one family per lesson. "
                 f"Fetch from '{prev}', or pass --switch to move the whole lesson to '{prefix}' and refetch every icon.",
                 "lesson": a.lesson, "family": prev, "requested": prefix})
            sys.exit(2)
        family_note = {"status": status, "family": prefix, "previous": prev}
    dest = pathlib.Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    px = a.size * 2
    results, chrome_jobs, missing = [], [], []
    try:
        import resvg_py  # noqa: F401
        renderer = "resvg-py"
    except ImportError:
        renderer = "chrome"
    for name in a.names:
        svg, source = fetch_svg(prefix, name, color, a.size)
        if svg is None:
            missing.append(name)
            results.append({"name": name, "ok": False, "source": source})
            continue
        svg_path, png_path = dest / f"{name}.svg", dest / f"{name}@2x.png"
        svg_path.write_text(svg, encoding="utf-8")
        if renderer == "resvg-py":
            png_path.write_bytes(png_resvg(svg, px))
        else:
            chrome_jobs.append((svg, px, png_path))
        results.append({"name": name, "ok": True, "source": source, "svg": str(svg_path), "png": str(png_path)})
    if chrome_jobs:
        png_chrome(chrome_jobs)
    report = {"ok": not missing, "family": prefix, "license": FAMILIES[prefix], "color": color, "size": a.size,
              "png_px": px, "renderer": renderer, "icons": results}
    if family_note:
        report["lesson"] = {"plan": a.lesson, **family_note}
        if family_note["status"] == "switched":
            report["lesson"]["refetch"] = f"every icon in the lesson from '{family_note['previous']}' must be refetched from '{prefix}'"
    if missing:
        report["hint"] = f"not found in {prefix}: {', '.join(missing)}; try: icons.py search {prefix} <word>"
    out(report)
    sys.exit(0 if not missing else 1)


def cmd_search(a):
    prefix = family_prefix(a.family)
    q = urllib.parse.urlencode({"query": a.query, "prefix": prefix, "limit": max(32, a.limit)})
    data = json.loads(get(f"{API}/search?{q}").decode("utf-8"))
    names = [i.split(":", 1)[1] for i in data.get("icons", [])][: a.limit]
    out({"family": prefix, "query": a.query, "icons": names})


def main():
    ap = argparse.ArgumentParser(description="Iconify icons, one family per lesson, SVG plus 2x PNG.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="download icons")
    f.add_argument("family")
    f.add_argument("names", nargs="+")
    f.add_argument("--color", default="#2B2F36", help="hex colour (default #2B2F36)")
    f.add_argument("--size", type=int, default=48, help="icon size in px; the PNG is twice this (default 48)")
    f.add_argument("--out", default="icons", help="output folder (default ./icons)")
    f.add_argument("--lesson", help="plan.md whose header records the lesson's one icon family")
    f.add_argument("--switch", action="store_true", help="change the lesson's recorded family instead of refusing")
    s = sub.add_parser("search", help="find icon names in a family")
    s.add_argument("family")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=20)
    sub.add_parser("families", help="list the supported families")
    a = ap.parse_args()
    if a.cmd == "fetch":
        cmd_fetch(a)
    elif a.cmd == "search":
        cmd_search(a)
    else:
        out({"families": FAMILIES, "aliases": ALIASES})


if __name__ == "__main__":
    main()
