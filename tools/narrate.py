#!/usr/bin/env python3
"""Draft narration and script-exact captions from a video storyboard or a plain script.

Usage:
  python narrate.py <media brief.md | script.txt> --out <dir>
                    [--voice ko-KR-SunHiNeural] [--engine edge|google|elevenlabs]
                    [--rate +0%] [--gap 0.4] [--max-chars 32] [--name narration]

Input:
  - A media brief (.md): the first table whose header has a "voice" column (the template's
    `| t | on screen | voice / caption | note |`). One audio clip per row with voice text;
    rows whose voice cell is empty or a dash are skipped and reported. The brief's `voice:`
    line is used when it names a voice id (for example ko-KR-SunHiNeural) and --voice is not given.
  - A plain script (.txt or anything else): one row per paragraph (blank-line separated);
    a file with no blank lines gives one row per line.

Output in --out:
  row-01.mp3, row-02.mp3, ...  one clip per voiced row
  <name>.mp3                   all clips joined with --gap seconds of silence between rows
  <name>.srt                   captions from the script text (never from speech recognition),
                               timed by the measured duration of each clip; a long row is split
                               into cues at sentence ends, then commas, then spaces, and the row's
                               time is shared by character count
  <name>.json                  manifest: voice, engine, per-row text, file, start, end, duration

Engines:
  edge        free, needs `pip install edge-tts` and a network connection. GPL-3.0 and an
              undocumented Microsoft service: drafts and internal use only.
  google      Google Cloud TTS (Chirp 3 HD for final Korean audio). Stub: reads credentials from
              env vars only and explains what to set.
  elevenlabs  ElevenLabs Multilingual v2. Stub: reads ELEVENLABS_API_KEY from env only.

Durations come from ffprobe when it is on PATH, else from the MP3 frame headers.
Joining uses ffmpeg when it is on PATH (with real silence gaps), else a byte join with no gaps
(the SRT then uses gap 0 so it still matches the joined file). --trim-tail S (off by default) cuts each
clip's trailing silence down to S seconds before timing, since edge-tts ends every clip with about 0.95 s
of silence; durations, the joined file and the SRT then follow the trimmed clips.
"""
import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

DEFAULT_VOICE = "ko-KR-SunHiNeural"
VOICE_ID = re.compile(r"\b[a-z]{2,3}-[A-Z]{2}-[A-Za-z0-9-]+\b")
DASHES = {"", "-", "\u2013", "\u2014", "n/a", "none", "(none)", "silence", "(silence)"}


# ---------- reading the script ----------

def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_separator(line):
    return re.match(r"^\s*\|[\s:\-|]+\|?\s*$", line) is not None


def clean_cell(text):
    text = re.sub(r"\*\*|__|`", "", text)
    text = text.replace("<br>", " ").replace("<br/>", " ")
    text = text.strip()
    # strip one pair of surrounding quotes, straight or curly
    m = re.match(r'^["“”\'‘’](.*)["“”\'‘’]$', text, re.S)
    if m:
        text = m.group(1).strip()
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", text))


def rows_from_brief(text):
    """Return (rows, voice_line, skipped). rows = [{"n", "t", "text"}]."""
    lines = text.splitlines()
    voice_line = None
    for line in lines:
        m = re.match(r"^\s*(?:[-*]\s*)?voice\s*:\s*(.+)$", line, re.I)
        if m and "<" not in m.group(1):
            voice_line = m.group(1).strip()
            break
        # the storyboard footer form: "captions: always · voice: ..."
        m = re.search(r"·\s*voice\s*:\s*([^·]+)", line, re.I)
        if m and "<" not in m.group(1) and voice_line is None:
            voice_line = m.group(1).strip()
    for i, line in enumerate(lines):
        if not line.strip().startswith("|") or is_separator(line):
            continue
        header = [h.lower() for h in split_row(line)]
        vcol = next((k for k, h in enumerate(header) if "voice" in h or "caption" in h or "narration" in h), None)
        if vcol is None or i + 1 >= len(lines) or not is_separator(lines[i + 1]):
            continue
        tcol = next((k for k, h in enumerate(header) if h in ("t", "time", "시간")), None)
        rows, skipped = [], []
        for j in range(i + 2, len(lines)):
            if not lines[j].strip().startswith("|"):
                break
            cells = split_row(lines[j])
            raw = cells[vcol] if vcol < len(cells) else ""
            t = cells[tcol] if tcol is not None and tcol < len(cells) else ""
            txt = clean_cell(raw)
            n = len(rows) + len(skipped) + 1
            if txt.lower() in DASHES or "<" in txt and "…" in txt:
                skipped.append({"n": n, "t": t})
                continue
            rows.append({"n": n, "t": t, "text": txt})
        return rows, voice_line, skipped
    return [], voice_line, []


def rows_from_script(text):
    text = text.replace("\r\n", "\n").strip()
    parts = re.split(r"\n\s*\n", text) if re.search(r"\n\s*\n", text) else text.split("\n")
    rows = []
    for p in parts:
        p = clean_cell(" ".join(x.strip() for x in p.splitlines()))
        if p:
            rows.append({"n": len(rows) + 1, "t": "", "text": p})
    return rows


# ---------- engines ----------

async def _edge_one(text, voice, rate, path):
    import edge_tts  # noqa: imported late so the other engines work without it

    await edge_tts.Communicate(text, voice, rate=rate).save(str(path))


def synth_edge(rows, voice, rate, outdir):
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        sys.exit("edge-tts is not installed: run `pip install edge-tts`, then retry.")

    async def run_all():
        for r in rows:
            await _edge_one(r["text"], voice, rate, r["path"])

    asyncio.run(run_all())


def synth_google(rows, voice, rate, outdir):
    key = os.environ.get("GOOGLE_TTS_API_KEY")
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not key and not creds:
        sys.exit(
            "google engine: no credentials found. Set one of these environment variables, never a file in the repo:\n"
            "  GOOGLE_APPLICATION_CREDENTIALS = path to a service-account JSON with Text-to-Speech enabled\n"
            "  GOOGLE_TTS_API_KEY             = an API key restricted to the Text-to-Speech API\n"
            "Voice: --voice ko-KR-Chirp3-HD-<name> (names in Google's voice list; Chirp 3 HD takes no SSML)."
        )
    sys.exit(
        "google engine is a stub in this version. Credentials were found in the environment.\n"
        "To finish it: POST https://texttospeech.googleapis.com/v1/text:synthesize with\n"
        '  {"input":{"text":<row text>},"voice":{"languageCode":"ko-KR","name":<voice>},"audioConfig":{"audioEncoding":"MP3"}}\n'
        "decode audioContent (base64) into each row's mp3; durations, joining and the SRT then work unchanged.\n"
        "Until then, draft with --engine edge."
    )


def synth_elevenlabs(rows, voice, rate, outdir):
    if not os.environ.get("ELEVENLABS_API_KEY"):
        sys.exit(
            "elevenlabs engine: ELEVENLABS_API_KEY is not set. Set it as an environment variable (never in a file in the repo).\n"
            "Voice: --voice <ElevenLabs voice id>; model eleven_multilingual_v2 lists Korean."
        )
    sys.exit(
        "elevenlabs engine is a stub in this version. ELEVENLABS_API_KEY was found in the environment.\n"
        "To finish it: POST https://api.elevenlabs.io/v1/text-to-speech/<voice id> with header xi-api-key and\n"
        '  {"text":<row text>,"model_id":"eleven_multilingual_v2"} and save the MP3 body per row.\n'
        "Until then, draft with --engine edge."
    )


ENGINES = {"edge": synth_edge, "google": synth_google, "elevenlabs": synth_elevenlabs}


# ---------- durations and joining ----------

_BITRATES = {  # MPEG-1 / MPEG-2(.5) layer III, kbps
    1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
    2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
}
_RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def mp3_duration_frames(path):
    """Sum MP3 frame durations by walking frame headers (layer III only)."""
    data = Path(path).read_bytes()
    i, total = 0, 0.0
    if data[:3] == b"ID3":
        size = ((data[6] & 0x7F) << 21) | ((data[7] & 0x7F) << 14) | ((data[8] & 0x7F) << 7) | (data[9] & 0x7F)
        i = 10 + size
    while i + 4 <= len(data):
        b1, b2, b3 = data[i + 1], data[i + 2], data[i + 3]
        if data[i] != 0xFF or (b1 & 0xE0) != 0xE0:
            i += 1
            continue
        ver = (b1 >> 3) & 3  # 3 = MPEG1, 2 = MPEG2, 0 = MPEG2.5
        layer = (b1 >> 1) & 3
        br_i, sr_i, pad = (b2 >> 4) & 15, (b2 >> 2) & 3, (b2 >> 1) & 1
        if ver == 1 or layer != 1 or br_i in (0, 15) or sr_i == 3:
            i += 1
            continue
        br = _BITRATES[1 if ver == 3 else 2][br_i] * 1000
        sr = _RATES[ver][sr_i]
        samples = 1152 if ver == 3 else 576
        size = (144 if ver == 3 else 72) * br // sr + pad
        if size <= 4:
            i += 1
            continue
        total += samples / sr
        i += size
    return total


def duration(path):
    if shutil.which("ffprobe"):
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True,
        )
        try:
            return float(p.stdout.strip())
        except ValueError:
            pass
    return mp3_duration_frames(path)


def trim_tail(path, keep):
    """Cut a clip's trailing silence (under -45 dB) down to `keep` seconds; edge-tts ends every clip with
    about 0.95 s of silence. Re-encodes the MP3 at its own sample rate; leaves the file alone without ffmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("warn: ffmpeg not found, --trim-tail skipped", file=sys.stderr)
        return False
    tmp = path.with_suffix(".trim.mp3")
    af = (f"areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB:start_silence={keep},"
          "areverse")
    p = subprocess.run([ffmpeg, "-y", "-v", "error", "-i", str(path), "-af", af, "-c:a", "libmp3lame", "-b:a", "48k",
                        str(tmp)], capture_output=True, text=True)
    if p.returncode or not tmp.exists():
        tmp.unlink(missing_ok=True)
        print(f"warn: --trim-tail failed on {path.name}: {p.stderr.strip()}", file=sys.stderr)
        return False
    tmp.replace(path)
    return True


def join(rows, gap, out):
    """Join clips; returns the gap actually used (0 when ffmpeg is missing)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        with open(out, "wb") as f:
            for r in rows:
                f.write(Path(r["path"]).read_bytes())
        print("warn: ffmpeg not found, clips byte-joined with no silence gaps; SRT uses gap 0", file=sys.stderr)
        return 0.0
    inputs, parts = [], []
    for k, r in enumerate(rows):
        inputs += ["-i", str(r["path"])]
        parts.append(f"[{k}:a]aresample=24000,aformat=channel_layouts=mono[a{k}]")
    labels = []
    n = len(rows)
    for k in range(n):
        labels.append(f"[a{k}]")
        if gap > 0 and k < n - 1:
            parts.append(f"anullsrc=r=24000:cl=mono,atrim=duration={gap}[s{k}]")
            labels.append(f"[s{k}]")
    parts.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[out]")
    cmd = [ffmpeg, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts),
           "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "64k", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"ffmpeg join failed: {p.stderr.strip()}")
    return gap


# ---------- captions ----------

def split_caption(text, max_chars):
    """Split one row's script text into caption-sized cues, keeping the words as written."""
    if len(text) <= max_chars:
        return [text]
    pieces = [s for s in re.split(r"(?<=[.!?。？！…])\s+", text) if s]
    out = []
    for s in pieces:
        while len(s) > max_chars:
            window = s[: max_chars + 1]
            cut = max(window.rfind(", "), window.rfind("، "))
            if cut < max_chars // 3:
                cut = window.rfind(" ")
            if cut < max_chars // 3:
                cut = max_chars
            out.append(s[: cut + (1 if s[cut:cut + 1] == "," else 0)].strip())
            s = s[cut + 1:].strip() if s[cut:cut + 1] in (" ", ",") else s[cut:].strip()
        if s:
            out.append(s)
    # merge very short tails into the previous cue when they fit
    merged = []
    for c in out:
        if merged and len(merged[-1]) + 1 + len(c) <= max_chars:
            merged[-1] = merged[-1] + " " + c
        else:
            merged.append(c)
    return merged


def slot_seconds(t):
    """Length of a storyboard time cell such as '0-6 s', '6–13 s' or '0:05-0:12'; None if unreadable."""
    def sec(x):
        if ":" in x:
            m, s_ = x.split(":", 1)
            return int(m) * 60 + float(s_)
        return float(x)
    m = re.match(r"^\s*(\d+(?::\d+)?(?:\.\d+)?)\s*s?\s*[-\u2013\u2014~]\s*(\d+(?::\d+)?(?:\.\d+)?)\s*s?\s*$", t or "")
    if not m:
        return None
    return sec(m.group(2)) - sec(m.group(1))


def ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(rows, max_chars):
    cues = []
    for r in rows:
        parts = split_caption(r["text"], max_chars)
        weights = [max(1, len(p.replace(" ", ""))) for p in parts]
        total = sum(weights)
        t = r["start"]
        for p, w in zip(parts, weights):
            d = r["duration"] * w / total
            cues.append((t, t + d, p))
            t += d
    blocks = [f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n" for k, (a, b, txt) in enumerate(cues, 1)]
    return "\n".join(blocks), len(cues)


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description="Narration MP3s and script-exact SRT from a storyboard or script.")
    ap.add_argument("source", help="media brief (.md) with a voice/caption column, or a plain script")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--voice", help=f"voice id (default: the brief's voice: line if it names one, else {DEFAULT_VOICE})")
    ap.add_argument("--engine", choices=sorted(ENGINES), default="edge")
    ap.add_argument("--rate", default="+0%", help="edge speaking rate, e.g. -10%% or +5%%")
    ap.add_argument("--gap", type=float, default=0.4, help="seconds of silence between rows in the joined file")
    ap.add_argument("--max-chars", type=int, default=32, help="max characters per caption cue")
    ap.add_argument("--name", default="narration", help="base name of the joined MP3, SRT and manifest")
    ap.add_argument("--dry", action="store_true", help="print the rows that would be voiced and stop")
    ap.add_argument("--trim-tail", type=float, metavar="S",
                    help="cut each clip's trailing silence down to S seconds (edge ends clips with ~0.95 s); "
                         "off by default")
    a = ap.parse_args()

    src = Path(a.source)
    text = src.read_text(encoding="utf-8-sig")
    voice_line, skipped = None, []
    if src.suffix.lower() == ".md":
        rows, voice_line, skipped = rows_from_brief(text)
        if not rows:
            sys.exit(f"{src}: no table with a voice/caption column and voiced rows found")
    else:
        rows = rows_from_script(text)
        if not rows:
            sys.exit(f"{src}: script is empty")

    voice = a.voice
    if not voice and voice_line and a.engine == "edge":
        m = VOICE_ID.search(voice_line)
        if m and m.group(0).endswith("Neural"):
            voice = m.group(0)
    voice = voice or DEFAULT_VOICE

    if a.dry:
        lines = [f"voice {voice} · engine {a.engine} · {len(rows)} voiced rows · {len(skipped)} skipped"]
        lines += [f"row {r['n']:02d} {r['t'] or '':>8} {r['text']}" for r in rows]
        sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))
        return

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for r in rows:
        r["path"] = out / f"row-{r['n']:02d}.mp3"
    ENGINES[a.engine](rows, voice, a.rate, out)
    if a.trim_tail is not None:
        for r in rows:
            trim_tail(r["path"], a.trim_tail)

    joined = out / f"{a.name}.mp3"
    gap = join(rows, a.gap, joined)
    t = 0.0
    for k, r in enumerate(rows):
        r["duration"] = round(duration(r["path"]), 3)
        r["start"] = round(t, 3)
        r["end"] = round(t + r["duration"], 3)
        t = r["end"] + (gap if k < len(rows) - 1 else 0)
    srt, ncues = build_srt(rows, a.max_chars)
    (out / f"{a.name}.srt").write_text(srt, encoding="utf-8")
    joined_dur = round(duration(joined), 3)

    manifest = {
        "source": str(src), "engine": a.engine, "voice": voice, "rate": a.rate, "gap": gap,
        "joined": joined.name, "joined_duration": joined_dur, "script_duration": round(t, 3),
        "srt": f"{a.name}.srt", "cues": ncues,
        "rows": [{k: (str(Path(v).name) if k == "path" else v) for k, v in r.items()} for r in rows],
        "skipped_rows": skipped,
    }
    (out / f"{a.name}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [f"voice {voice} · engine {a.engine} · {len(rows)} rows · gap {gap:g} s"]
    for r in rows:
        lines.append(f"row {r['n']:02d}  {r['duration']:6.2f} s  {r['start']:6.2f} -> {r['end']:6.2f}  {r['path'].name}")
        slot = slot_seconds(r["t"])
        if slot is not None and r["duration"] > slot + 0.5:
            lines.append(f"warn: row {r['n']:02d} voice runs {r['duration']:.1f} s, its storyboard slot '{r['t']}' is {slot:g} s")
    for s in skipped:
        lines.append(f"row {s['n']:02d}  skipped (no voice text) {s['t']}")
    lines.append(f"joined {joined.name}: {joined_dur:.2f} s (script timeline {t:.2f} s) · {ncues} cues in {a.name}.srt")
    if a.engine == "edge":
        lines.append("note: edge-tts is for drafts (GPL-3.0, undocumented service); final audio via --engine google|elevenlabs")
    sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
