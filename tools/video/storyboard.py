#!/usr/bin/env python3
"""Media brief storyboard -> captioned MP4.

Usage: python storyboard.py <media-brief.md> --out out.mp4 [--audio <dir>] [--size phone|landscape|WxH]
                            [--engine auto|revideo|ffmpeg] [--scene scene.json] [--scene-only]
                            [--gap 0.4] [--font "Noto Sans KR"] [--keep]

Reads the brief's video storyboard table (columns t | on screen | voice / caption | note), writes a
scene JSON, and renders one beat per row: the "on screen" text, or an image when the cell names a
.png/.jpg/.webp/.svg path (resolved against the brief's folder; text in the same cell becomes a
headline above it), with the caption column burned in as caption pages.

Timing: the t column ("0-5 s", "5–12s", "0:05-0:12", or a bare "4 s" duration). With --audio <dir>
(one MP3 per row, e.g. tools/narrate.py output), each row lasts its MP3 plus --gap seconds, the MP3s
are joined into the soundtrack, and an <name>.srt beside an MP3 times that row's caption pages.

Engines: revideo (the Revideo project in this folder, headless Chrome) or ffmpeg (Pillow frames +
ffmpeg concat, no motion). auto tries revideo and falls back to ffmpeg if it fails; the JSON summary
names the engine that produced the file. Needs ffmpeg/ffprobe on PATH; Pillow for the ffmpeg engine.
"""
import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = {"phone": (1080, 1920), "portrait": (1080, 1920), "landscape": (1920, 1080), "wide": (1920, 1080)}
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif")
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
        ".svg": "image/svg+xml", ".gif": "image/gif"}
FPS = 30
FONT_FILES = {
    "regular": ["C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/NotoSansKR-Regular.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/System/Library/Fonts/AppleSDGothicNeo.ttc"],
    "bold": ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/NotoSansKR-Bold.ttf",
             "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
             "/System/Library/Fonts/AppleSDGothicNeo.ttc"],
}
THEME = {"bg": "#F7F5F2", "ink": "#1A1A1A", "card": "#FFFFFF", "capBg": "#111111", "capInk": "#FFFFFF",
         "accent": "#FF4D2E"}
PLACEHOLDER_RE = re.compile(r"^\s*[\"“”']?\s*<[^>]*>\s*[\"“”']?\s*$")
QUOTES = "\"'“”‘’「」『』"
warnings = []


def warn(msg):
    warnings.append(msg)
    print("warn: " + msg, file=sys.stderr)


# ---------- brief parsing ----------

def split_row(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells = re.split(r"(?<!\\)\|", s)  # an escaped \| stays inside its cell
    return [c.replace("\\|", "|").strip() for c in cells]


def find_storyboard(text):
    """Return (header, rows) of the first table whose header has a t column and an on-screen column."""
    lines = text.splitlines()
    for i in range(len(lines) - 1):
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            header = [h.lower().strip("* ") for h in split_row(lines[i])]
            if "t" in header and any("screen" in h for h in header):
                rows = []
                j = i + 2
                while j < len(lines) and lines[j].lstrip().startswith("|"):
                    rows.append(split_row(lines[j]))
                    j += 1
                return header, rows
    return None, []


def col(header, *names):
    for n in names:
        if n in header:
            return header.index(n)
    for n in names:
        for k, h in enumerate(header):
            if n in h:
                return k
    return None


def num(s):
    s = s.strip()
    if ":" in s:
        v = 0.0
        for p in s.split(":"):
            v = v * 60 + float(p)
        return v
    return float(s)


NUMTOK = r"(\d+(?::\d+)?(?:\.\d+)?)"
T_RANGE = re.compile(NUMTOK + r"\s*(?:s|초)?\s*(?:[–—~-]|to)\s*" + NUMTOK, re.I)
T_SINGLE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(?:s|sec|초)?\s*$", re.I)


def parse_t(cell):
    """-> (start or None, duration or None)."""
    c = cell.replace("*", "")
    m = T_RANGE.search(c)
    if m:
        a, b = num(m.group(1)), num(m.group(2))
        if b > a:
            return a, b - a
    m = T_SINGLE.match(c)
    if m:
        return None, float(m.group(1))
    return None, None


def clean_caption(s):
    s = s.replace("**", "").replace("<br>", " ").strip()
    if len(s) >= 2 and s[0] in QUOTES and s[-1] in QUOTES:
        s = s[1:-1].strip()
    return s


def find_image(cell, base):
    """Pull an image path out of an on-screen cell. Returns (path or None, remaining text)."""
    text, cand = cell, None
    m = re.search(r"!\[[^\]]*\]\(([^)]+)\)", text)
    if m:
        cand, text = m.group(1).strip(), text.replace(m.group(0), " ")
    else:
        for tok in re.findall(r"`([^`]+)`|(\S+)", text):
            t = (tok[0] or tok[1]).strip(".,;:()[]")
            if t.lower().endswith(IMG_EXT):
                cand = t
                text = text.replace("`" + t + "`", " ").replace(t, " ")
                break
    text = re.sub(r"\s+", " ", text.replace("**", "")).strip(" ·|-–")
    if not cand:
        return None, text
    path = cand if os.path.isabs(cand) else os.path.normpath(os.path.join(base, cand))
    if not os.path.exists(path):
        warn(f"image not found: {cand} (looked at {path}); showing its name as text")
        return None, (text + " " if text else "") + f"[image missing: {os.path.basename(cand)}]"
    return path, text


# ---------- captions ----------

def visible_len(s):
    return len(re.sub(r"\s", "", s)) or 1


def caption_pages(text, max_chars):
    """Split a caption into pages of at most max_chars, at sentence ends, then commas, then spaces."""
    if not text:
        return []
    sentences = [x.strip() for x in re.split(r"(?<=[.!?。？！…])\s+", text) if x.strip()]
    pages = []
    for s in sentences:
        while len(s) > max_chars:
            cut = -1
            k = s.rfind(", ", 0, max_chars + 1)
            if k > max_chars // 3:
                cut = k + 1
            else:
                k = s.rfind(" ", 0, max_chars + 1)
                cut = k if k > max_chars // 3 else max_chars
            pages.append(s[:cut].strip())
            s = s[cut:].strip()
        if s:
            pages.append(s)
    return pages


def time_pages(pages, duration, lead=0.15, tail=0.3):
    """Share a row's time across its caption pages by visible character count."""
    if not pages:
        return []
    span = max(0.5, duration - lead - tail)
    total = sum(visible_len(p) for p in pages)
    out, t = [], lead
    for p in pages:
        d = span * visible_len(p) / total
        out.append({"text": p, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return out


SRT_TIME = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")


def read_srt(path):
    cues = []
    with open(path, encoding="utf-8-sig") as f:
        blocks = re.split(r"\n\s*\n", f.read().strip())
    for b in blocks:
        lines = [x for x in b.splitlines() if x.strip()]
        for k, line in enumerate(lines):
            m = SRT_TIME.search(line)
            if m:
                g = [int(x) for x in m.groups()]
                a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
                z = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
                txt = " ".join(lines[k + 1:]).strip()
                if txt:
                    cues.append({"text": txt, "start": a, "end": z})
                break
    return cues


# ---------- audio ----------

def which(name):
    p = shutil.which(name)
    if not p:
        sys.exit(f"error: {name} not found on PATH")
    return p


def run(args, what, **kw):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if p.returncode != 0:
        raise RuntimeError(f"{what} failed ({p.returncode}): {(p.stderr or p.stdout).strip()[-1500:]}")
    return p


def probe_duration(path):
    p = subprocess.run([which("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        sys.exit(f"error: could not read duration of {path}: {p.stderr.strip()}")


def natural_key(s):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", s)]


def match_audio(audio_dir, rows):
    """One MP3 per row. tools/narrate.py writes row-NN.mp3 numbered by table row (skipped rows keep
    their number) plus a joined file; those are matched by number. Otherwise: exactly one MP3 per
    row in name order, or the last number in each file name as the row number."""
    files = sorted([f for f in os.listdir(audio_dir) if f.lower().endswith(".mp3")], key=natural_key)
    if not files:
        sys.exit(f"error: no .mp3 files in {audio_dir}")
    narrated = {int(m.group(1)): f for f in files for m in [re.match(r"^row-(\d+)\.mp3$", f, re.I)] if m}
    if narrated:
        out = [narrated.get(r["table_n"]) for r in rows]
        key = "table row"
    elif len(files) == len(rows):
        out = files
        key = None
    else:
        by_num = {}
        for f in files:
            nums = re.findall(r"\d+", os.path.splitext(f)[0])
            if nums:
                by_num.setdefault(int(nums[-1]), f)
        out = [by_num.get(r["index"]) for r in rows]
        key = "the number in each file name"
        warn(f"{len(files)} MP3s for {len(rows)} rows; matched by {key}")
    missing = [str(r["index"]) for r, f in zip(rows, out) if f is None]
    if missing:
        warn(f"rows without audio (silence, t column timing): {', '.join(missing)}"
             + (f" (matched by {key})" if key else ""))
    return [os.path.join(audio_dir, f) if f else None for f in out]


def build_soundtrack(rows, out_path):
    args, filters = [which("ffmpeg"), "-y", "-v", "error"], []
    for i, r in enumerate(rows):
        if r.get("audio"):
            args += ["-i", r["audio"]]
        else:
            args += ["-f", "lavfi", "-t", str(r["duration"]), "-i", "anullsrc=r=44100:cl=stereo"]
        d = r["duration"]
        filters.append(f"[{i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo,"
                       f"apad=whole_dur={d},atrim=0:{d},asetpts=PTS-STARTPTS[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(len(rows))) + f"concat=n={len(rows)}:v=0:a=1[out]")
    args += ["-filter_complex", ";".join(filters), "-map", "[out]", "-c:a", "pcm_s16le", out_path]
    run(args, "joining audio")


def mux(video, audio, out, total):
    run([which("ffmpeg"), "-y", "-v", "error", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.3f}", "-movflags", "+faststart", out],
        "muxing audio")


# ---------- scene ----------

def build_scene(brief, size, audio_dir, gap, font):
    with open(brief, encoding="utf-8") as f:
        text = f.read()
    header, raw = find_storyboard(text)
    if not header:
        sys.exit("error: no storyboard table (a header with 't' and 'on screen') in " + brief)
    ct, cs = col(header, "t", "time"), col(header, "on screen", "screen")
    cc = col(header, "voice / caption", "caption", "voice")
    cn = col(header, "note", "notes")
    base = os.path.dirname(os.path.abspath(brief))
    w, h = size
    max_chars = 30 if h > w else 40
    rows = []
    for table_n, cells in enumerate(raw, 1):
        def get(k):
            return cells[k] if k is not None and k < len(cells) else ""
        screen_cell, cap_cell = get(cs), get(cc)
        if PLACEHOLDER_RE.match(screen_cell or "<>") and PLACEHOLDER_RE.match(cap_cell or "<>"):
            continue  # the template's placeholder row
        start, dur = parse_t(get(ct))
        img, rest = find_image(screen_cell, base)
        screen = {"kind": "image", "path": img, "text": rest} if img else {"kind": "text", "text": rest}
        rows.append({"index": len(rows) + 1, "table_n": table_n, "t": get(ct), "start_hint": start, "duration": dur,
                     "screen": screen, "caption": clean_caption(cap_cell), "note": get(cn)})
    if not rows:
        sys.exit("error: the storyboard table has no filled rows")

    audio = match_audio(audio_dir, rows) if audio_dir else [None] * len(rows)
    t = 0.0
    for r, a in zip(rows, audio):
        r["audio"] = os.path.abspath(a) if a else None
        if a:
            r["audio_duration"] = round(probe_duration(a), 3)
            r["duration"] = round(r["audio_duration"] + gap, 3)
        elif r["duration"] is None:
            r["duration"] = 4.0
            warn(f"row {r['index']}: no time in t cell '{r['t']}' and no audio; using 4 s")
        if not audio_dir and r["start_hint"] is not None and abs(r["start_hint"] - t) > 0.05:
            warn(f"row {r['index']}: t cell starts at {r['start_hint']} s but earlier rows end at {t:.2f} s; rows play back to back")
        r["start"] = round(t, 3)
        t += r["duration"]
        srt = os.path.splitext(a)[0] + ".srt" if a else None
        if srt and os.path.exists(srt):
            pages = []
            for c in read_srt(srt):  # a long cue is still split into pages
                for p in time_pages(caption_pages(c["text"], max_chars), c["end"] - c["start"], 0, 0):
                    pages.append({"text": p["text"], "start": round(c["start"] + p["start"], 3),
                                  "end": round(c["start"] + p["end"], 3)})
            r["captions"], r["caption_source"] = pages, "srt"
        else:
            r["captions"] = time_pages(caption_pages(r["caption"], max_chars), r["duration"])
            r["caption_source"] = "script"
        del r["start_hint"]
    scene = {"source": os.path.abspath(brief), "width": w, "height": h, "fps": FPS, "font": font,
             "theme": THEME, "layout": layout(w, h), "duration": round(t, 3), "rows": rows,
             "ffmpeg": shutil.which("ffmpeg") or ""}
    prewrap(scene)
    return scene


def layout(W, H):
    """Sizes shared by both engines (the Revideo scene reads them from the scene JSON)."""
    portrait = H > W
    short = W if portrait else H
    pad = round(W * 0.07)
    return {"pad": pad, "head_px": round(short * (0.075 if portrait else 0.07)),
            "cap_px": round(short * (0.048 if portrait else 0.042)),
            "cap_bottom": round(H * (0.12 if portrait else 0.08)),
            "head_w": W - pad * 2, "cap_w": round(W - pad * 3.6)}


def measurer(kind, px):
    """Width function for a font size: Pillow metrics when available, else a Hangul-aware estimate."""
    try:
        from PIL import Image, ImageDraw
        font = load_font(kind, px)
        d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
        return lambda s: d.textlength(s, font=font)
    except ImportError:
        return lambda s: sum(px if ord(ch) > 0x2E80 else px * 0.55 for ch in s)


def break_lines(text, measure, width):
    """Word-keeping line breaks (Korean breaks at spaces, as CSS keep-all would); long words split."""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = (cur + " " + word).strip()
            if measure(trial) <= width:
                cur = trial
                continue
            if cur:
                lines.append(cur)
            cur = ""
            for ch in word:
                if cur and measure(cur + ch) > width:
                    lines.append(cur)
                    cur = ""
                cur += ch
        if cur:
            lines.append(cur)
    return lines


def prewrap(scene):
    """Store line breaks in the scene so both engines wrap the same way (Revideo uses textWrap 'pre')."""
    L = scene["layout"]
    safe = 0.94  # Noto Sans KR runs slightly wider than Malgun Gothic, which Pillow may measure with
    cap = measurer("regular", L["cap_px"])
    for r in scene["rows"]:
        for c in r["captions"]:
            c["text"] = "\n".join(break_lines(c["text"], cap, L["cap_w"] * safe))
        head = r["screen"].get("text")
        if head:
            px = round(L["head_px"] * (0.8 if r["screen"].get("path") else 1))
            r["screen"]["head_px"] = px
            r["screen"]["text"] = "\n".join(break_lines(head, measurer("bold", px), L["head_w"] * safe))


def with_data_uris(scene):
    s = json.loads(json.dumps(scene))
    for r in s["rows"]:
        p = r["screen"].get("path")
        if p:
            ext = os.path.splitext(p)[1].lower()
            with open(p, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            r["screen"]["src"] = f"data:{MIME.get(ext, 'application/octet-stream')};base64,{data}"
    return s


# ---------- engines ----------

def render_revideo(scene, out_mp4, work):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node not found on PATH")
    if not os.path.isdir(os.path.join(HERE, "node_modules", "@revideo", "renderer")):
        raise RuntimeError("Revideo not installed: run npm install in " + HERE)
    scene_file = os.path.join(work, "scene.revideo.json")
    with open(scene_file, "w", encoding="utf-8") as f:
        json.dump(with_data_uris(scene), f, ensure_ascii=False)
    env = dict(os.environ, DISABLE_TELEMETRY="true", PUPPETEER_SKIP_DOWNLOAD="true")
    run([node, os.path.join(HERE, "render.mjs"), scene_file, out_mp4], "Revideo render",
        cwd=HERE, env=env, timeout=1800)
    if not os.path.exists(out_mp4):
        raise RuntimeError("Revideo finished but wrote no file")


def load_font(kind, size):
    from PIL import ImageFont
    for path in FONT_FILES[kind] + FONT_FILES["regular"]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    warn("no Hangul font found; Korean will not render in the ffmpeg engine")
    return ImageFont.load_default()


def wrap(draw, text, font, width):
    return break_lines(text, lambda s: draw.textlength(s, font=font), width)


def draw_frame(scene, row, caption, path):
    from PIL import Image, ImageDraw
    W, H = scene["width"], scene["height"]
    th, L = scene["theme"], scene["layout"]
    pad, cap_px, cap_bottom = L["pad"], L["cap_px"], L["cap_bottom"]
    img = Image.new("RGB", (W, H), th["bg"])
    d = ImageDraw.Draw(img)
    stage_top, stage_bottom = pad, H - cap_bottom - cap_px * 4
    scr = row["screen"]
    blocks = []
    head = scr.get("text") or ""
    if head:
        f = load_font("bold", scr.get("head_px", L["head_px"]))
        lines = wrap(d, head, f, L["head_w"])
        lh = round(f.size * 1.3)
        blocks.append(("text", lines, f, lh, lh * len(lines)))
    if scr.get("path"):
        if scr["path"].lower().endswith(".svg"):
            warn(f"row {row['index']}: the ffmpeg engine cannot draw SVG; use a PNG export")
        else:
            pic = Image.open(scr["path"]).convert("RGBA")
            used = sum(b[4] for b in blocks) + (pad * 0.6 if blocks else 0)
            max_w, max_h = W - pad * 2.6, stage_bottom - stage_top - used - pad
            k = min(max_w / pic.width, max_h / pic.height)
            pic = pic.resize((max(1, int(pic.width * k)), max(1, int(pic.height * k))), Image.LANCZOS)
            cpad = round(pad * 0.3)
            blocks.append(("pic", pic, cpad, None, pic.height + cpad * 2))
    gap = round(pad * 0.6)
    total = sum(b[4] for b in blocks) + gap * max(0, len(blocks) - 1)
    y = stage_top + (stage_bottom - stage_top - total) / 2
    for b in blocks:
        if b[0] == "text":
            _, lines, f, lh, _ = b
            for i, line in enumerate(lines):
                d.text(((W - d.textlength(line, font=f)) / 2, y + i * lh), line, font=f, fill=th["ink"])
        else:
            _, p, cpad, _, bh = b
            x0 = (W - p.width) / 2 - cpad
            d.rounded_rectangle([x0, y, x0 + p.width + cpad * 2, y + bh], radius=24, fill=th["card"])
            img.paste(p, (int(x0 + cpad), int(y + cpad)), p)
        y += b[4] + gap
    if caption:
        f = load_font("regular", cap_px)
        lines = wrap(d, caption, f, L["cap_w"])
        lh = round(cap_px * 1.35)
        bw = max(d.textlength(x, font=f) for x in lines) + cap_px * 1.6
        bh = lh * len(lines) + cap_px * 0.9
        x0, y1 = (W - bw) / 2, H - cap_bottom
        d.rounded_rectangle([x0, y1 - bh, x0 + bw, y1], radius=18, fill=th["capBg"])
        for i, line in enumerate(lines):
            d.text(((W - d.textlength(line, font=f)) / 2, y1 - bh + cap_px * 0.45 + i * lh), line,
                   font=f, fill=th["capInk"])
    img.save(path)


def render_ffmpeg(scene, out_mp4, work):
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise RuntimeError("Pillow not installed (pip install pillow)")
    entries, n = [], 0
    for row in scene["rows"]:
        cuts, t = [], 0.0  # (seconds, caption text or None)
        for c in row["captions"]:
            if c["start"] > t + 1e-3:
                cuts.append((c["start"] - t, None))
            cuts.append((c["end"] - max(c["start"], t), c["text"]))
            t = c["end"]
        if row["duration"] > t + 1e-3:
            cuts.append((row["duration"] - t, None))
        cache = {}
        for dur, cap in cuts:
            if dur <= 0:
                continue
            if cap not in cache:
                n += 1
                p = os.path.join(work, f"f{n:04d}.png")
                draw_frame(scene, row, cap, p)
                cache[cap] = p
            entries.append((cache[cap], dur))
    lst = os.path.join(work, "frames.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p, dur in entries:
            f.write(f"file '{p.replace(os.sep, '/')}'\nduration {dur:.3f}\n")
        f.write(f"file '{entries[-1][0].replace(os.sep, '/')}'\n")
    run([which("ffmpeg"), "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-t", f"{scene['duration']:.3f}", "-movflags", "+faststart", out_mp4], "ffmpeg frame render")


def probe(path):
    p = subprocess.run([which("ffprobe"), "-v", "error", "-show_entries",
                        "stream=codec_type,codec_name,width,height:format=duration", "-of", "json", path],
                       capture_output=True, text=True)
    info = json.loads(p.stdout or "{}")
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
    return {"width": v.get("width"), "height": v.get("height"), "video": v.get("codec_name"),
            "audio": a.get("codec_name") if a else None,
            "duration": round(float(info.get("format", {}).get("duration", 0)), 2)}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Render a media brief's storyboard table to a captioned MP4.")
    ap.add_argument("brief")
    ap.add_argument("--out", help="output .mp4 (required unless --scene-only)")
    ap.add_argument("--audio", help="folder with one MP3 per storyboard row (e.g. tools/narrate.py output)")
    ap.add_argument("--size", default="phone", help="phone (1080x1920, default), landscape (1920x1080) or WxH")
    ap.add_argument("--engine", default="auto", choices=["auto", "revideo", "ffmpeg"])
    ap.add_argument("--scene", help="also write the scene JSON here")
    ap.add_argument("--scene-only", action="store_true", help="write the scene JSON (stdout or --scene) and stop")
    ap.add_argument("--gap", type=float, default=0.4, help="seconds of silence after each MP3 (default 0.4)")
    ap.add_argument("--font", help="font family for the revideo engine (default Noto Sans KR if installed, else Malgun Gothic)")
    ap.add_argument("--keep", action="store_true", help="keep the work folder (frames, soundtrack, scene)")
    a = ap.parse_args()

    if a.size in SIZES:
        size = SIZES[a.size]
    else:
        m = re.match(r"^(\d+)x(\d+)$", a.size)
        if not m:
            sys.exit("error: --size must be phone, landscape or WxH")
        size = (int(m.group(1)) // 2 * 2, int(m.group(2)) // 2 * 2)
    noto = ["C:/Windows/Fonts/NotoSansKR-VF.ttf", "C:/Windows/Fonts/NotoSansKR-Regular.ttf"]
    font = a.font or ("Noto Sans KR" if any(os.path.exists(p) for p in noto) else "Malgun Gothic")
    scene = build_scene(a.brief, size, a.audio, a.gap, font)
    if a.scene:
        with open(a.scene, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=2)
    if a.scene_only:
        if not a.scene:
            print(json.dumps(scene, ensure_ascii=False, indent=2))
        return 0
    if not a.out:
        sys.exit("error: --out is required")
    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    work = tempfile.mkdtemp(prefix="storyboard-")
    silent = os.path.join(work, "silent.mp4")
    engine_used, errors = None, []
    try:
        for engine in (["revideo", "ffmpeg"] if a.engine == "auto" else [a.engine]):
            try:
                (render_revideo if engine == "revideo" else render_ffmpeg)(scene, silent, work)
                engine_used = engine
                break
            except Exception as e:  # noqa: BLE001
                errors.append(f"{engine}: {e}")
                warn(f"{engine} engine failed: {str(e).splitlines()[0][:300]}")
        if not engine_used:
            print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
            return 1
        if any(r.get("audio") for r in scene["rows"]):
            track = os.path.join(work, "soundtrack.wav")
            build_soundtrack(scene["rows"], track)
            mux(silent, track, out, scene["duration"])
        else:
            shutil.move(silent, out)
    finally:
        if a.keep:
            print("work folder: " + work, file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)
    summary = {"ok": True, "out": out, "engine": engine_used, "rows": len(scene["rows"]),
               "planned_duration": scene["duration"], **probe(out),
               "captions": sum(len(r["captions"]) for r in scene["rows"]),
               "caption_source": sorted({r["caption_source"] for r in scene["rows"]}),
               "warnings": warnings}
    if errors:
        summary["fallback_reason"] = errors
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
