#!/usr/bin/env python3
"""Branching decision scenario (Markdown) -> Twee 3 -> playable HTML via tweego.

Usage: python twine.py <scenario.md> --out scenario.html [--twee out.twee] [--format sugarcube|harlowe]
                       [--tweego <path>] [--fetch] [--check] [--json]

Scenario format (one file, plain Markdown):

    # 회의록 요약 맡기기                        <- story title
    start: 시작                                 <- optional, default = first passage
    format: sugarcube                           <- optional, sugarcube (default) or harlowe
    reveal label: 판정 보기                      <- optional, link text that reveals the verdict
    verdict labels: 좋은 선택 / 아쉬운 선택 / 생각해 볼 선택   <- optional, good / bad / mixed

    ## 시작 · 금요일 오후 5시                    <- passage id, then an optional display title
    팀장님이 회의록 요약을 30분 안에 달라고 합니다.   <- body text (any number of lines)
    - 초안을 그대로 보낸다 -> 그대로             <- choice: label -> target passage id
    - 숫자만 원문과 맞춰 본다 -> 확인

    ## 그대로 · 월요일 회의
    consequence: 팀장님이 틀린 숫자를 회의에서 그대로 읽었습니다.
    verdict: bad · 숫자는 원문과 한 번 맞춰 봐야 합니다.
    - 처음부터 다시 -> 시작

Each passage plays in this order: consequence (what happened because of the choice that led here),
then the body, then the verdict behind a reveal link, then the choices. The verdict never shows
before the consequence, and when a passage has a verdict its choices appear only after the reveal.
A passage without choices is an ending and should carry a verdict.

Checks (printed, exit 1 on errors): choices pointing at unknown passages, a missing start passage;
warnings: unreachable passages, endings without a verdict, a verdict without a consequence.

tweego: --tweego <path>, else tools/interactive/bin/tweego(.exe), else tweego on PATH. --fetch
downloads the tweego 2.1.1 release zip from GitHub into tools/interactive/bin first. Without tweego
the .twee file is still written and the reply says how to compile it.
"""
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.join(HERE, "bin")
TWEEGO_VERSION = "2.1.1"
TWEEGO_ZIPS = {
    ("win32", True): "tweego-2.1.1-windows-x64.zip", ("win32", False): "tweego-2.1.1-windows-x86.zip",
    ("linux", True): "tweego-2.1.1-linux-x64.zip", ("darwin", True): "tweego-2.1.1-macos-x64.zip",
}
RELEASE = "https://github.com/tmedwards/tweego/releases/download/v{v}/{name}"
DEFAULT_REVEAL = "판정 보기"
DEFAULT_LABELS = {"good": "좋은 선택", "bad": "아쉬운 선택", "mixed": "생각해 볼 선택"}
CHOICE_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*(?:->|→)\s*(.+?)\s*$")
errors, warnings = [], []


def warn(msg):
    warnings.append(msg)


def fail(msg):
    errors.append(msg)


# ---------- parse ----------

def parse(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    story = {"title": "", "start": None, "format": "sugarcube", "reveal": DEFAULT_REVEAL,
             "labels": dict(DEFAULT_LABELS), "passages": []}
    cur = None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^#\s+(.+)$", line)
        if m and not story["title"]:
            story["title"] = m.group(1).strip()
            continue
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            head = m.group(1).strip()
            pid, title = (re.split(r"\s+[·|]\s+", head, maxsplit=1) + [""])[:2]
            pid = pid.strip()
            if re.search(r"[\[\]{}|\\]", pid) or "->" in pid:
                fail(f"passage id '{pid}' may not contain [ ] {{ }} | \\ or ->")
            cur = {"id": pid, "title": title.strip(), "body": [], "consequence": [], "verdict": None,
                   "choices": []}
            story["passages"].append(cur)
            continue
        if cur is None:
            m = re.match(r"^\s*(start|format|reveal label|verdict labels)\s*:\s*(.+)$", line, re.I)
            if m:
                key, val = m.group(1).lower(), m.group(2).strip()
                if key == "start":
                    story["start"] = val
                elif key == "format":
                    story["format"] = val.lower()
                elif key == "reveal label":
                    story["reveal"] = val
                else:
                    parts = [p.strip() for p in val.split("/")]
                    for k, p in zip(("good", "bad", "mixed"), parts):
                        if p:
                            story["labels"][k] = p
            continue
        m = re.match(r"^\s*consequence\s*:\s*(.+)$", line, re.I)
        if m:
            cur["consequence"].append(m.group(1).strip())
            continue
        m = re.match(r"^\s*verdict\s*:\s*(good|bad|mixed)\s*(?:[·|:,]\s*(.*))?$", line, re.I)
        if m:
            cur["verdict"] = {"kind": m.group(1).lower(), "why": (m.group(2) or "").strip()}
            continue
        m = CHOICE_RE.match(line)
        if m:
            label, target = m.group(1).strip(), m.group(2).strip()
            if "]" in label or "[" in label:
                fail(f"{cur['id']}: choice label '{label}' may not contain [ or ]")
            cur["choices"].append({"label": label, "target": target})
            continue
        cur["body"].append(line)
    for p in story["passages"]:
        while p["body"] and not p["body"][0].strip():
            p["body"].pop(0)
        while p["body"] and not p["body"][-1].strip():
            p["body"].pop()
    return story


def check(story):
    ids = [p["id"] for p in story["passages"]]
    if not ids:
        fail("no passages (## headings)")
        return
    for d in sorted({i for i in ids if ids.count(i) > 1}):
        fail(f"duplicate passage id '{d}'")
    story["start"] = story["start"] or ids[0]
    if story["start"] not in ids:
        fail(f"start passage '{story['start']}' does not exist")
    if story["format"] not in ("sugarcube", "harlowe"):
        fail(f"format '{story['format']}' not supported (sugarcube or harlowe)")
    for p in story["passages"]:
        for c in p["choices"]:
            if c["target"] not in ids:
                fail(f"{p['id']}: choice '{c['label']}' points at unknown passage '{c['target']}'")
        if not p["choices"] and not p["verdict"]:
            warn(f"{p['id']}: ending without a verdict")
        if p["verdict"] and not p["consequence"]:
            warn(f"{p['id']}: verdict without a consequence (show what happened before judging it)")
    seen, todo = set(), [story["start"]]
    by_id = {p["id"]: p for p in story["passages"]}
    while todo:
        pid = todo.pop()
        if pid in seen or pid not in by_id:
            continue
        seen.add(pid)
        todo += [c["target"] for c in by_id[pid]["choices"]]
    for pid in ids:
        if pid not in seen:
            warn(f"{pid}: unreachable from '{story['start']}'")


# ---------- twee ----------

def ifid(title):
    """Stable IFID per title (UUID shaped as v4, which Twine and tweego expect)."""
    h = hashlib.sha1(("lesson-twine:" + title).encode("utf-8")).hexdigest().upper()
    return f"{h[:8]}-{h[8:12]}-4{h[13:16]}-{'89AB'[int(h[16], 16) % 4]}{h[17:20]}-{h[20:32]}"


def passage_twee(p, story):
    fmt, out = story["format"], []
    if p["title"]:
        out += [f"<h2>{p['title']}</h2>", ""]
    if p["consequence"]:
        out += ['<div class="consequence">' + "<br>".join(p["consequence"]) + "</div>", ""]
    if p["body"]:
        out += p["body"] + [""]
    links = [f"[[{c['label']}->{c['target']}]]" for c in p["choices"]]
    if p["verdict"]:
        v = p["verdict"]
        inner = [f'<div class="verdict {v["kind"]}"><strong>{story["labels"][v["kind"]]}</strong>'
                 + (f"<br>{v['why']}" if v["why"] else "") + "</div>"] + links
        if fmt == "sugarcube":
            out += [f'<<linkreplace "{story["reveal"]}">>'] + inner + ["<</linkreplace>>"]
        else:
            out += [f'(link: "{story["reveal"]}")['] + inner + ["]"]
    else:
        out += links
    return "\n".join(out).rstrip()


CSS = """.consequence, .verdict { color: #1A1A1A; }
.consequence { background: #FFF4E5; border-left: 4px solid #FF4D2E; padding: .8em 1em; margin: 0 0 1em; border-radius: 6px; }
.verdict { padding: .8em 1em; margin: 1em 0; border-radius: 6px; }
.verdict.good { background: #E7F6EC; }
.verdict.bad { background: #FDECEC; }
.verdict.mixed { background: #F1F1F1; }
body, tw-story { font-family: "Noto Sans KR", "Malgun Gothic", sans-serif; line-height: 1.6; word-break: keep-all; }"""


def to_twee(story):
    fmt_name = "SugarCube" if story["format"] == "sugarcube" else "Harlowe"
    data = {"ifid": ifid(story["title"]), "format": fmt_name, "start": story["start"]}
    parts = [":: StoryTitle", story["title"] or "Scenario", "",
             ":: StoryData", json.dumps(data, ensure_ascii=False, indent=2), "",
             ":: StoryStylesheet [stylesheet]", CSS, ""]
    for p in story["passages"]:
        parts += [f":: {p['id']}", passage_twee(p, story), ""]
    return "\n".join(parts)


# ---------- tweego ----------

def find_tweego(explicit):
    exe = "tweego.exe" if os.name == "nt" else "tweego"
    for c in [explicit, os.path.join(BIN, exe), shutil.which("tweego")]:
        if c and os.path.exists(c):
            return c
    return None


def fetch_tweego():
    is64 = sys.maxsize > 2 ** 32
    name = TWEEGO_ZIPS.get((sys.platform, is64)) or TWEEGO_ZIPS.get((sys.platform, True))
    if not name:
        raise RuntimeError(f"no tweego build for {sys.platform}")
    url = RELEASE.format(v=TWEEGO_VERSION, name=name)
    with urllib.request.urlopen(url, timeout=120) as r:
        blob = r.read()
    os.makedirs(BIN, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for m in z.infolist():  # refuse paths that escape bin/
            target = os.path.realpath(os.path.join(BIN, m.filename))
            if not target.startswith(os.path.realpath(BIN)):
                raise RuntimeError("unsafe path in tweego zip: " + m.filename)
        z.extractall(BIN)
    exe = os.path.join(BIN, "tweego.exe" if os.name == "nt" else "tweego")
    if os.name != "nt" and os.path.exists(exe):
        os.chmod(exe, 0o755)
    return url, len(blob)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Compile a branching decision scenario to Twee 3 and HTML.")
    ap.add_argument("scenario")
    ap.add_argument("--out", help="output .html (the .twee goes beside it unless --twee is given)")
    ap.add_argument("--twee", help="where to write the .twee file")
    ap.add_argument("--format", choices=["sugarcube", "harlowe"], help="override the file's format line")
    ap.add_argument("--tweego", help="path to the tweego binary")
    ap.add_argument("--fetch", action="store_true", help=f"download tweego {TWEEGO_VERSION} into tools/interactive/bin first")
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not a.out and not a.twee and not a.check:
        ap.error("give --out, --twee or --check")

    story = parse(a.scenario)
    if a.format:
        story["format"] = a.format
    check(story)
    res = {"ok": not errors, "title": story["title"], "format": story["format"], "start": story["start"],
           "passages": len(story["passages"]),
           "endings": sum(1 for p in story["passages"] if not p["choices"]),
           "choices": sum(len(p["choices"]) for p in story["passages"]),
           "errors": errors, "warnings": warnings}
    if errors or a.check:
        return report(res, a.json, 1 if errors else 0)

    twee_path = a.twee or os.path.splitext(a.out)[0] + ".twee"
    with open(twee_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(to_twee(story))
    res["twee"] = os.path.abspath(twee_path)
    if a.out:
        if a.fetch and not find_tweego(a.tweego):
            try:
                url, size = fetch_tweego()
                res["fetched"] = f"{url} ({size} bytes)"
            except Exception as e:  # noqa: BLE001
                warn(f"could not fetch tweego: {e}")
        exe = find_tweego(a.tweego)
        if exe:
            p = subprocess.run([exe, "-o", a.out, twee_path], capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            if p.returncode == 0 and os.path.exists(a.out):
                res["html"] = os.path.abspath(a.out)
                res["tweego"] = exe
            else:
                res["ok"] = False
                errors.append("tweego failed: " + (p.stderr or p.stdout).strip()[-1500:])
        else:
            res["html"] = None
            res["how_to_compile"] = (f"tweego not found. Run again with --fetch, or download tweego {TWEEGO_VERSION} "
                                     f"from https://github.com/tmedwards/tweego/releases, unzip it into "
                                     f"tools/interactive/bin, then: tweego -o {a.out} {twee_path}")
    return report(res, a.json, 0 if res["ok"] else 1)


def report(res, as_json, code):
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"{res['title']}: {res['passages']} passages, {res['choices']} choices, {res['endings']} endings, "
              f"format {res['format']}, start '{res['start']}'")
        for k in ("twee", "html", "fetched", "how_to_compile"):
            if res.get(k):
                print(f"{k}: {res[k]}")
        for e in res["errors"]:
            print("ERROR: " + e)
        for w in res["warnings"]:
            print("warn: " + w)
    return code


if __name__ == "__main__":
    sys.exit(main())
