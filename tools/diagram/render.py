#!/usr/bin/env python3
"""Render a Mermaid diagram with the house theme (Korean fonts, white card, large type) to PNG at 2x.

Usage:
  python render.py <file.mmd | brief.md> --out x.png [--block 1] [--scale 2] [--json]

Input is a .mmd file, or any Markdown file (a media brief) holding a ```mermaid block; --block picks
which one (default the first). Output format follows the --out extension: .png (default, at --scale,
default 2), .svg or .pdf. Uses mermaid-cli (`mmdc`, npm i -g @mermaid-js/mermaid-cli) with
mermaid.json (base theme, fontFamily "Malgun Gothic, Noto Sans KR") and theme.css from this folder,
and the installed Chrome or Edge (a puppeteer config is written to tools/.cache/ on first run, so
mermaid-cli needs no Chromium download).

Checks printed as warnings, mirroring the media brief: more than 7 boxes, a left-right flowchart
(phones read top-down better), and SVG output (it relies on the viewer having a Hangul font; PNG at
2x is the safe export). Exit 1 when mmdc fails or the input has no Mermaid source.
Mark the one box to look at first with `A:::accent`, context boxes with `B:::muted`.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE.parent / ".cache"
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
FLOW_RE = re.compile(r"^\s*(flowchart|graph)\s+(TD|TB|BT|LR|RL)\b", re.I | re.M)
NODE_RE = re.compile(r"(?<![\w-])([A-Za-z](?:[\w-]*\w)?)\s*(\[\[|\[\(|\(\(|\[|\(|\{\{|\{|>)")


def out(obj):
    sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))


def find_browser():
    env = os.environ.get("PUPPETEER_EXECUTABLE_PATH") or os.environ.get("CHROME_PATH")
    for p in ([env] if env else []) + BROWSERS:
        if p and os.path.exists(p):
            return p
    return None


def puppeteer_config():
    browser = find_browser()
    if not browser:
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "puppeteer.json"
    cfg = {"executablePath": browser, "headless": True, "args": ["--no-sandbox", "--font-render-hinting=none"]}
    path.write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    return path


def mermaid_source(path, block):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if path.lower().endswith((".mmd", ".mermaid")):
        return text.strip()
    blocks = re.findall(r"^```+\s*mermaid[^\n]*\n(.*?)^```+", text, re.M | re.S)
    if not blocks:
        return None
    if block > len(blocks):
        sys.exit(f"render.py: asked for block {block}, the file has {len(blocks)} mermaid block(s)")
    return blocks[block - 1].strip()


def checks(src, fmt):
    warnings = []
    m = FLOW_RE.search(src)
    if m and m.group(2).upper() in ("LR", "RL"):
        warnings.append(f"flowchart {m.group(2).upper()}: phones read top-down; prefer `flowchart TD`")
    if m:
        body = "\n".join(l for l in src.splitlines() if not re.match(r"^\s*(%%|classDef|class |style |linkStyle|subgraph|end\b)", l))
        nodes = {n for n in NODE_RE.findall(body) for n in [n[0]] if n.lower() not in ("flowchart", "graph", "click")}
        if len(nodes) > 7:
            warnings.append(f"{len(nodes)} boxes; the media brief allows 7 at most, split the diagram")
    else:
        nodes = set()
    if fmt == "svg":
        warnings.append("SVG text uses the viewer's fonts; a phone without a Hangul font shows boxes. Export PNG at 2x for lessons")
    return warnings, len(nodes)


def main():
    ap = argparse.ArgumentParser(description="Mermaid to PNG at 2x with the house theme.")
    ap.add_argument("source", help=".mmd file, or a Markdown file with a ```mermaid block")
    ap.add_argument("--out", required=True, help="output .png, .svg or .pdf")
    ap.add_argument("--block", type=int, default=1, help="which mermaid block in a Markdown file (default 1)")
    ap.add_argument("--scale", type=float, default=2)
    ap.add_argument("--config", default=str(HERE / "mermaid.json"))
    ap.add_argument("--css", default=str(HERE / "theme.css"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    src = mermaid_source(a.source, a.block)
    if not src:
        out({"ok": False, "error": f"no mermaid source in {a.source}"})
        sys.exit(1)
    dest = pathlib.Path(a.out).resolve()
    fmt = dest.suffix.lower().lstrip(".") or "png"
    if fmt not in ("png", "svg", "pdf"):
        sys.exit("render.py: --out must end in .png, .svg or .pdf")
    dest.parent.mkdir(parents=True, exist_ok=True)
    mmdc = shutil.which("mmdc")
    if not mmdc:
        sys.exit("render.py: mmdc not found; npm i -g @mermaid-js/mermaid-cli (set PUPPETEER_SKIP_DOWNLOAD=1 to reuse the installed Chrome)")
    warnings, n_nodes = checks(src, fmt)
    with tempfile.TemporaryDirectory() as tmp:
        mmd = pathlib.Path(tmp) / "diagram.mmd"
        mmd.write_text(src + "\n", encoding="utf-8")
        cmd = [mmdc, "-i", str(mmd), "-o", str(dest), "-c", a.config, "-C", a.css, "-b", "white", "-q"]
        if fmt == "png":
            cmd += ["-s", str(a.scale)]
        pcfg = puppeteer_config()
        if pcfg:
            cmd += ["-p", str(pcfg)]
        res = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, timeout=300)
    if res.returncode or not dest.exists():
        err = (res.stderr or res.stdout).decode("utf-8", "replace").strip()
        out({"ok": False, "error": "mmdc failed", "detail": err[-1500:], "command": " ".join(cmd)})
        sys.exit(1)
    report = {"ok": True, "out": str(dest), "format": fmt, "boxes": n_nodes, "warnings": warnings}
    if fmt == "png":
        try:
            from PIL import Image
            with Image.open(dest) as im:
                report["size"] = list(im.size)
        except Exception:  # noqa: BLE001 - size is informational
            pass
    if a.json:
        out(report)
    else:
        lines = [f"wrote {dest}" + (f" ({report['size'][0]}x{report['size'][1]})" if "size" in report else "")]
        lines += [f"warn: {w}" for w in warnings]
        sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
