#!/usr/bin/env python3
"""Lesson plan -> LiaScript course (Markdown with quizzes), ready for the LiaScript exporter (SCORM).

Usage: python lia.py <plan.md> --out lesson.lia.md [--media-dir <dir>] [--bundle] [--author "InnovLabs"]
                     [--language ko] [--narrator "Korean Female"] [--json]

One section per segment of the plan's Segments table (title, what happens, the instruction from
Segment detail, the segment's media, its check items as quizzes, the transition line). Teacher-only
fields (materials, fast / slow / wrong, the Outcome's English scaffold) are left out.

Check items are written in a segment's detail block in the Q/A/W format, one field per line or on
one line joined with " / ":

    - check:
      - Q: 규칙을 만들 때 가장 먼저 볼 것은 무엇인가요?
      - A: 보낸 사람
      - W: 메일 길이 :: 길이는 같은 사람이 보내도 매번 다릅니다.
      - H: 매번 바뀌지 않는 것을 고르세요.
      - why: 보낸 사람은 메일마다 바뀌지 않는 기준입니다.
    - Q: 오늘 만든 규칙 개수는? / A: 3

A = correct option (two or more A lines make a multiple-choice quiz), W = wrong option, optional
"text :: feedback" on a W gives answer-specific feedback, H = hint (any number), why = explanation.
Q with A and no W becomes a text-input quiz. Feedback and explanation appear in the LiaScript
solution block, which opens once the quiz is solved or resolved.

Media: ids from the segment's media cell and the Media list are matched to files in --media-dir
(default: media/ beside the plan, then the plan folder): <id>.hl.png, then <id>*.png/.jpg/.webp/
.svg/.gif, then .mp4 (embedded as video) and .mp3 (audio). Alt text comes from the media brief's
"Alt text" section (<id>*.md) or the Media list purpose. A missing file becomes a visible
[media needed: ...] line and a warning.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys

IMG_EXT = [".hl.png", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"]
VID_EXT = [".mp4", ".webm"]
AUD_EXT = [".mp3", ".m4a", ".ogg", ".wav"]
FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?(Q|A|W|H|why|hint)\s*[:：]\s*(.+?)\s*$", re.I)
warnings = []


def warn(msg):
    warnings.append(msg)
    print("warn: " + msg, file=sys.stderr)


def split_row(line):
    s = line.strip().strip("|")
    return [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", s)]


def section(text, name, level=2):
    """Body of a '## name' section (case-insensitive prefix match), or ''."""
    m = re.search(r"^" + "#" * level + r"\s+" + re.escape(name) + r"[^\n]*\n(.*?)(?=^#{1,%d}\s|\Z)" % level,
                  text, re.M | re.S | re.I)
    return m.group(1) if m else ""


def table(body, first_col=None):
    """Rows of the first Markdown table in body as dicts keyed by lowercased header."""
    lines = [x for x in body.splitlines() if x.strip().startswith("|")]
    if len(lines) < 2:
        return []
    header = [h.lower().strip("* ") for h in split_row(lines[0])]
    rows = []
    for line in lines[2:]:
        cells = [c.replace("**", "").strip() for c in split_row(line)]
        row = {h: (cells[i] if i < len(cells) else "") for i, h in enumerate(header)}
        if first_col and not re.match(first_col, cells[0] if cells else ""):
            continue
        rows.append(row)
    return rows


def pick(row, *names):
    for n in names:
        for k, v in row.items():
            if k == n or k.startswith(n):
                return v
    return ""


def semver(v):
    v = v.strip()
    return v + ".0.0" if v.isdigit() else v


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"“'「" and s[-1] in "\"”'」":
        return s[1:-1].strip()
    return s


# ---------- segment detail ----------

def detail_blocks(text):
    """{segment id: block text} from '#### S1 ...' headings anywhere in the plan."""
    blocks = {}
    for m in re.finditer(r"^#{3,4}\s+(S\d+[a-z]?)\b[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)", text, re.M | re.S):
        blocks[m.group(1)] = m.group(2)
    return blocks


def bullet(block, name):
    m = re.search(r"^\s*[-*]\s*" + re.escape(name) + r"\s*[:：]\s*(.+)$", block, re.M | re.I)
    return unquote(m.group(1)) if m else ""


def parse_checks(block):
    """Q/A/W items in a detail block, in order."""
    items, cur = [], None
    lines = []
    for line in block.splitlines():
        # one-liner "Q: ... / A: ... / W: ..." becomes several field lines
        if re.search(r"\bQ\s*[:：]", line) and re.search(r"\s/\s*(A|W|H|why)\s*[:：]", line, re.I):
            lead = re.sub(r"^\s*(?:[-*]\s*)?(?:check\s*[:：]\s*)?", "", line, flags=re.I)
            lines += [p.strip() for p in re.split(r"\s/\s*(?=(?:Q|A|W|H|why|hint)\s*[:：])", lead, flags=re.I)]
        else:
            lines.append(line)
    for line in lines:
        m = FIELD_RE.match(line)
        if not m:
            continue
        key, val = m.group(1).lower(), unquote(m.group(2))
        if key == "q":
            cur = {"q": val, "a": [], "w": [], "h": [], "why": ""}
            items.append(cur)
        elif cur is None:
            warn(f"'{key.upper()}:' line before any 'Q:' ignored: {val[:40]}")
        elif key == "a":
            cur["a"].append(val)
        elif key == "w":
            text, _, fb = val.partition("::")
            cur["w"].append({"text": text.strip(), "feedback": fb.strip()})
        elif key in ("h", "hint"):
            cur["h"].append(val)
        else:
            cur["why"] = val
    for it in items:
        if not it["a"]:
            warn(f"check item has no 'A:' line, skipped: {it['q'][:50]}")
    return [it for it in items if it["a"]]


def stable_order(options, seed):
    """Deterministic shuffle so the correct option is not always first (LiaScript also randomizes)."""
    return sorted(options, key=lambda o: hashlib.sha1((seed + o[0]).encode("utf-8")).hexdigest())


def quiz_md(item):
    out = [f"**{item['q']}**", ""]
    if not item["w"]:
        out.append(f"[[{item['a'][0]}]]")
    else:
        multi = len(item["a"]) > 1
        opts = [(a, True) for a in item["a"]] + [(w["text"], False) for w in item["w"]]
        out.append("<!-- data-randomize -->")
        for text, ok in stable_order(opts, item["q"]):
            mark = "X" if ok else " "
            out.append(f"- [[{mark}]] {text}" if multi else f"- [({mark})] {text}")
    for h in item["h"]:
        out.append(f"- [[?]] {h}" if item["w"] else f"[[?]] {h}")
    feedback = [f"- {w['text']}: {w['feedback']}" for w in item["w"] if w["feedback"]]
    if item["why"] or feedback:
        out += ["*" * 40, ""]
        if item["why"]:
            out += [item["why"], ""]
        if feedback:
            out += feedback + [""]
        out.append("*" * 40)
    return "\n".join(out)


# ---------- media ----------

def find_media(mid, dirs):
    for d in dirs:
        if not os.path.isdir(d):
            continue
        names = os.listdir(d)
        def match(ext):
            exact = [n for n in names if n.lower() == (mid + ext).lower()]
            loose = [n for n in names if n.lower().endswith(ext) and re.match(re.escape(mid) + r"(?![0-9A-Za-z])", n, re.I)]
            return (exact or sorted(loose) or [None])[0]
        for ext in IMG_EXT + VID_EXT + AUD_EXT:
            n = match(ext)
            if n:
                return os.path.join(d, n), ext
    return None, None


def brief_alt(mid, dirs):
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for n in sorted(os.listdir(d)):
            if n.lower().endswith(".md") and re.match(re.escape(mid) + r"(?![0-9A-Za-z])", n, re.I):
                with open(os.path.join(d, n), encoding="utf-8") as f:
                    body = section(f.read(), "Alt text").strip()
                body = re.sub(r"<[^>]*>", "", body).strip()
                if body:
                    return " ".join(body.split())
    return ""


def media_md(mid, purpose, dirs, out_dir, bundle=False):
    path, ext = find_media(mid, dirs)
    alt = brief_alt(mid, dirs) or purpose or mid
    alt = alt.replace("[", "(").replace("]", ")")
    if not path:
        warn(f"{mid}: no media file found in {', '.join(dirs)}")
        return f"> [media needed: {mid}{' · ' + purpose if purpose else ''}]", None
    if bundle:  # copy into <out>/media/ so the export folder holds only the course
        dest_dir = os.path.join(out_dir, "media")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, os.path.basename(path))
        if os.path.abspath(dest) != os.path.abspath(path):
            shutil.copy2(path, dest)
        path = dest
    rel = os.path.relpath(path, out_dir).replace(os.sep, "/")
    if rel.startswith(".."):
        warn(f"{mid}: {rel} sits outside the output folder; the SCORM export packs only the output folder (use --bundle)")
    prefix = "!?" if ext in VID_EXT else ("?" if ext in AUD_EXT else "!")
    return f"{prefix}[{alt}]({rel})", rel


# ---------- main ----------

def convert(plan_path, out_path, media_dir, author, language, narrator, bundle=False):
    with open(plan_path, encoding="utf-8") as f:
        text = f.read()
    title_m = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_m.group(1).strip() if title_m else os.path.splitext(os.path.basename(plan_path))[0]
    head = {}
    for k in ("slug", "mode", "age band", "total", "version"):
        m = re.search(re.escape(k) + r"\s*:\s*([^·\n]+)", text, re.I)
        if m:
            head[k] = m.group(1).strip()
    segs = table(section(text, "Segments"), r"^S\d+")
    if not segs:
        sys.exit("error: no Segments table rows (| S1 | ...) in " + plan_path)
    media_rows = {pick(r, "id"): r for r in table(section(text, "Media list"), r"^M\d+")}
    details = detail_blocks(text)
    plan_dir = os.path.dirname(os.path.abspath(plan_path))
    dirs = [os.path.abspath(media_dir)] if media_dir else [os.path.join(plan_dir, "media"), plan_dir]
    out_dir = os.path.dirname(os.path.abspath(out_path))

    comment = " · ".join(f"{k}: {v}" for k, v in head.items())
    md = ["<!--", f"author:   {author}", f"version:  {semver(head.get('version', '1'))}", f"language: {language}",
          f"narrator: {narrator}", f"comment:  {comment or title}", "-->", "", f"# {title}", ""]
    stats = {"sections": 0, "quizzes": 0, "media": 0, "media_missing": 0}
    used_media = set()
    for s in segs:
        sid = pick(s, "id")
        block = details.get(sid, "")
        seg_title = pick(s, "title") or sid
        md += [f"## {sid} · {seg_title}", ""]
        what = pick(s, "what happens", "what")
        if what and what not in ("–", "-"):
            md += [what, ""]
        instr = bullet(block, "instruction")
        if instr:
            md += [f"> {instr}", ""]
        ids = re.findall(r"\bM\d+\b", pick(s, "media"))
        ids += [mid for mid, r in media_rows.items() if pick(r, "segment") == sid and mid not in ids]
        for mid in ids:
            line, rel = media_md(mid, pick(media_rows.get(mid, {}), "purpose"), dirs, out_dir, bundle)
            md += [line, ""]
            used_media.add(mid)
            stats["media" if rel else "media_missing"] += 1
        for item in parse_checks(block):
            md += [quiz_md(item), ""]
            stats["quizzes"] += 1
        trans = bullet(block, "transition")
        if trans:
            md += [f"*{trans}*", ""]
        stats["sections"] += 1
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md).rstrip() + "\n")
    return stats


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Convert a lesson plan into a LiaScript course.")
    ap.add_argument("plan")
    ap.add_argument("--out", required=True, help="output .md (e.g. lesson.lia.md)")
    ap.add_argument("--media-dir", help="folder with media files and briefs (default: media/ beside the plan)")
    ap.add_argument("--author", default="InnovLabs")
    ap.add_argument("--language", default="ko")
    ap.add_argument("--narrator", default="Korean Female", help="LiaScript narrator voice (ResponsiveVoice name)")
    ap.add_argument("--bundle", action="store_true",
                    help="copy the media used into <out folder>/media/ so the folder can be exported on its own")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    stats = convert(a.plan, a.out, a.media_dir, a.author, a.language, a.narrator, a.bundle)
    res = {"ok": True, "out": os.path.abspath(a.out), **stats, "warnings": warnings}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"{res['out']}: {stats['sections']} sections, {stats['quizzes']} quizzes, "
              f"{stats['media']} media embedded, {stats['media_missing']} missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
