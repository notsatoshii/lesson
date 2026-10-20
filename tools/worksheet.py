#!/usr/bin/env python3
"""Render a data-driven printable worksheet (A4 by default) with Typst and check that it fits.

Usage:
  python worksheet.py <data.json> --out sheet.pdf [--png] [--ppi 144] [--template templates/worksheet.typ] [--json]

The JSON holds the sheet: title, footer, the expected page count (`pages`), colours (ink and accent
default to #221F38 and #D93D22), icons and a list of blocks (header, text, table, checklist, fields,
strip, columns, panel, oval, lines, cut, space, pagebreak); tools/README.md lists every key. Icon
and image paths are relative to the JSON file.

Compiles templates/worksheet.typ with `typst compile` (Korean font stack: Malgun Gothic, then Noto Sans
KR). --png also writes one PNG per page next to the PDF (<out>-1.png, <out>-2.png, ...; at --ppi, 144 by
default, which is 2x screen size). Then it reads the page count back from the document (`typst query`)
and warns when the sheet runs to more pages than the JSON's `pages` value: the A4 fit check. Table
rows asked under 7 mm are raised to 7 mm and reported. Exit 1 when typst fails, 2 when the fit check
fails.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE / "templates" / "worksheet.typ"


def say(obj, as_json):
    if as_json:
        sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    else:
        lines = [f"wrote {p}" for p in obj.get("files", [])]
        lines.append(f"pages: {obj.get('pages')}" + (f" (expected {obj['expected']})" if obj.get("expected") else ""))
        lines += [f"warn: {w}" for w in obj.get("warnings", [])]
        if obj.get("error"):
            lines.append("error: " + obj["error"])
        sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))


def rooted(path, root):
    """Path as Typst wants it inside --root: forward slashes, leading slash."""
    return "/" + pathlib.Path(os.path.relpath(path, root)).as_posix()


def run(cmd):
    return subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL, timeout=300)


def main():
    ap = argparse.ArgumentParser(description="Data-driven printable worksheet (Typst) with an A4 fit check.")
    ap.add_argument("data", help="worksheet JSON")
    ap.add_argument("--out", required=True, help="output .pdf")
    ap.add_argument("--png", action="store_true", help="also write one PNG per page")
    ap.add_argument("--ppi", type=int, default=144, help="PNG resolution (144 = 2x screen size)")
    ap.add_argument("--template", default=str(TEMPLATE))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    typst = shutil.which("typst")
    if not typst:
        sys.exit("worksheet.py: typst not found; winget install --id Typst.Typst (or cargo install typst-cli)")
    data_path = pathlib.Path(a.data).resolve()
    if not data_path.exists():
        sys.exit(f"worksheet.py: no such file: {a.data}")
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"worksheet.py: {a.data} is not valid JSON: {e}")
    if not isinstance(data.get("blocks"), list):
        sys.exit("worksheet.py: the JSON needs a `blocks` list")
    out = pathlib.Path(a.out).resolve()
    if out.suffix.lower() != ".pdf":
        sys.exit("worksheet.py: --out must end in .pdf (PNGs come with --png)")
    out.parent.mkdir(parents=True, exist_ok=True)

    template = pathlib.Path(a.template).resolve()
    tmp = None
    try:
        root = os.path.commonpath([str(template.parent), str(data_path.parent)])
    except ValueError:  # different drives on Windows: copy the template beside the data
        tmp = pathlib.Path(tempfile.mkdtemp(dir=data_path.parent, prefix=".worksheet-"))
        shutil.copy(template, tmp / template.name)
        template = tmp / template.name
        root = str(data_path.parent)

    inputs = ["--root", root, "--input", f"data={rooted(data_path, root)}",
              "--input", f"base={rooted(data_path.parent, root)}"]
    files, warnings = [], []
    try:
        res = run([typst, "compile", *inputs, str(template), str(out)])
        if res.returncode:
            say({"ok": False, "error": "typst compile failed",
                 "detail": res.stderr.decode("utf-8", "replace").strip()[-2000:]}, a.json)
            if not a.json:
                sys.stdout.buffer.write(res.stderr[-2000:] + b"\n")
            sys.exit(1)
        files.append(str(out))
        if a.png:
            for old in out.parent.glob(out.stem + "-*.png"):
                if old.stem[len(out.stem) + 1:].isdigit():
                    old.unlink()
            pattern = out.with_name(out.stem + "-{p}.png")
            res = run([typst, "compile", *inputs, "--format", "png", "--ppi", str(a.ppi), str(template), str(pattern)])
            if res.returncode:
                warnings.append("PNG export failed: " + res.stderr.decode("utf-8", "replace").strip()[-500:])
            else:
                files += sorted(str(p) for p in out.parent.glob(out.stem + "-*.png") if p.stem[len(out.stem) + 1:].isdigit())
        q = run([typst, "query", *inputs, str(template), "<ws-report>", "--field", "value", "--one"])
        report = json.loads(q.stdout.decode("utf-8")) if q.returncode == 0 else {}
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)

    pages = report.get("pages")
    warnings = list(report.get("warnings", [])) + warnings
    expected = data.get("pages")
    fit_ok = True
    if pages is None:
        warnings.append("could not read the page count back (typst query failed)")
    elif expected and pages > int(expected):
        fit_ok = False
        warnings.append(f"the sheet runs to {pages} pages, the JSON allows {expected}: it does not fit; "
                        "shorten text, lower row counts or heights (never under 7 mm), or trim gaps")
    say({"ok": fit_ok, "files": files, "pages": pages, "expected": expected, "warnings": warnings}, a.json)
    sys.exit(0 if fit_ok else 2)


if __name__ == "__main__":
    main()
