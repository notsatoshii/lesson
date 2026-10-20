#!/usr/bin/env python3
"""Build one short taste digest for a run, so each critic reads one file instead of six (stdlib only).

Usage: python taste_digest.py --band E --mode live --out docs/lessons/<slug>/taste-digest.md
       [--owner ~/.claude/lesson/taste.md] [--project taste.md]

Keeps, in the order taste/README.md gives: the project's taste.md and the owner's file whole; from
age-bands.md the intro, the brief's band row and "Rules across bands"; from references.md the mode's
section plus story shapes, counter-examples and the test; slop.md whole; defaults.md without the
loop budget, the sources and the other modes' screen sections, every band table cut to the brief's
band. Each part names its source file so a critic can open the full file when a finding needs it.
"""
import argparse
import os
import re
from pathlib import Path

TASTE = Path(__file__).resolve().parent.parent / "taste"
MODE_SECTION = {"live": "Live class or workshop", "online": "Self-paced online", "video": "Video",
                "guide": "Written guide", "talk": "Talk"}
DROP_DEFAULTS = {"Loop budget", "Sources for the evidence-backed lines"}


def sections(text):
    """Split markdown on '## ' headings: [(title or '', body)]."""
    out, title, buf = [], "", []
    for line in text.splitlines():
        if line.startswith("## "):
            out.append((title, "\n".join(buf).strip()))
            title, buf = line[3:].strip(), []
        else:
            buf.append(line)
    out.append((title, "\n".join(buf).strip()))
    return out


def cut_band_tables(body, band):
    """In any table whose first header cell is 'band', keep the header, separator and the band's row."""
    lines, out, i = body.splitlines(), [], 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and re.match(r"^\|\s*band\s*\|", line.strip(), re.I):
            out.append(line)
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = lines[i]
                first = row.strip().strip("|").split("|")[0]
                if re.match(r"^[\s:\-]+$", first) or re.search(rf"(^|\*\*|\s){band}(\*\*|\s|$)", first.strip()):
                    out.append(row)
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--band", required=True, type=str.upper, choices=list("ABCDEFG"))
    ap.add_argument("--mode", required=True, choices=sorted(MODE_SECTION))
    ap.add_argument("--owner", default=os.environ.get("LESSON_TASTE") or str(Path.home() / ".claude/lesson/taste.md"))
    ap.add_argument("--project", default="taste.md")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    parts = [f"# Taste digest · band {a.band} · mode {a.mode}\n\nBuilt by `tools/taste_digest.py` from the skill's "
             f"`taste/` files and the owner's file. Earlier parts win where two disagree. Open a full file only "
             f"when a finding needs a line this digest cut."]
    if Path(a.project).is_file():
        parts.append(f"## 1. Project taste (`{a.project}`)\n\n{read(a.project).strip()}")
    else:
        parts.append("## 1. Project taste\n\nnone")
    if Path(a.owner).is_file():
        parts.append(f"## 2. Owner's taste (`{a.owner}`)\n\n{re.sub(r'(?m)^#', '###', read(a.owner).strip())}")
    else:
        parts.append("## 2. Owner's taste\n\nnone (run `/lesson taste init`)")
    parts.append("## 3. House rules\n\nIn the brief's House rules section; they bound everything below.")

    ab = sections(read(TASTE / "age-bands.md"))
    intro = cut_band_tables(ab[0][1].replace("# Age bands", "").strip(), a.band)
    rules = next((b for t, b in ab if t.startswith("Rules across")), "")
    parts.append(f"## 4. Age band {a.band} (`taste/age-bands.md`)\n\n{intro}\n\n### Rules across bands\n\n{rules}")

    ref = dict(sections(read(TASTE / "references.md")))
    keep = [MODE_SECTION[a.mode], "Story shapes", "Counter-examples", "The test a plan must pass"]
    body = "\n\n".join(f"### {k}\n\n{ref[k]}" for k in keep if k in ref)
    parts.append(f"## 5. References (`taste/references.md`, mode {a.mode})\n\n{body}")

    slop = read(TASTE / "slop.md").replace("# Slop: the tells", "").strip()
    parts.append(f"## 6. Slop (`taste/slop.md`)\n\n{re.sub(r'(?m)^## ', '### ', slop)}")

    other_screens = {"Online screens"} if a.mode not in ("online", "video") else set()
    d = [(t, b) for t, b in sections(read(TASTE / "defaults.md")) if t and t not in DROP_DEFAULTS | other_screens]
    body = "\n\n".join(f"### {t}\n\n{cut_band_tables(b, a.band)}" for t, b in d)
    parts.append(f"## 7. Defaults (`taste/defaults.md`)\n\n{body}")

    parts.append("## 8. Design skills\n\nFor slides, handouts and screens: the `uiux` taste layer when installed "
                 "(`~/.claude/skills/uiux/taste/`, the owner's uiux file); read it only for a materials finding.")
    text = "\n\n".join(parts) + "\n"
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text, encoding="utf-8")
    full = sum(len(read(TASTE / f)) for f in ("README.md", "age-bands.md", "references.md", "slop.md", "defaults.md"))
    full += len(read(a.owner)) if Path(a.owner).is_file() else 0
    print(f"{a.out}: {len(text)} characters (the six full files: {full})")


if __name__ == "__main__":
    main()
